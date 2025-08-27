import logging

from datetime import date, datetime
from odoo.exceptions import UserError
from odoo import _
from . import schemas
from odoo.addons.somconnexio.helpers.date import first_day_next_month

try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ContractChangeTariffProcess:
    _description = """
        Run Contract Change Tariff Request Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting process to change a contract's tariff with body: {}".format(
                params
            )
        )
        v = Validator(purge_unknown=True)
        if not v.validate(
            params,
            self.validator_create(),
        ):
            raise UserError(_("BadRequest {}").format(v.errors))
        params = self._prepare_create(params)
        wiz = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=params["contract_id"])
            .sudo()
            .create(params)
        )
        wiz.button_change()

        contract = self.env["contract.contract"].sudo().browse(params["contract_id"])

        if params["parent_pack_contract_id"]:
            self._vinculate_parent_pack_contract(
                contract, params["parent_pack_contract_id"]
            )
        if params["shared_bond_id"]:
            self._set_shared_bond_id_to_contract(contract, params["shared_bond_id"])
            contract.update_pack_mobiles_tariffs_after_joining_pack(
                params["start_date"]
            )

        return self.to_dict(wiz)

    def _vinculate_parent_pack_contract(self, contract, parent_pack_contract_id):
        contract.sudo().write({"parent_pack_contract_id": parent_pack_contract_id})

    def _set_shared_bond_id_to_contract(self, contract, shared_bond_id):
        contract.mobile_contract_service_info_id.sudo().write(
            {"shared_bond_id": shared_bond_id}
        )

    def _prepare_create(self, params):
        requested_product = params.get("product_code")
        mobile_phone = params.get("phone_number")
        contract_code = params.get("code")

        if not (mobile_phone or contract_code):
            raise UserError(
                _(
                    "Either a contract_code (fiber) or a phone_number (mobile) is required to search contracts"  # noqa
                )
            )

        if mobile_phone:
            contract = (
                self.env["contract.contract"]
                .sudo()
                .search(
                    [
                        (
                            "mobile_contract_service_info_id.phone_number",
                            "=",
                            mobile_phone,
                        ),
                        "|",
                        ("date_end", ">", date.today().strftime("%Y-%m-%d")),
                        ("date_end", "=", False),
                    ]
                )
            )

            mobile_templ = (
                self.env["product.template"]
                .sudo()
                .search(
                    [("categ_id", "=", self.env.ref("somconnexio.mobile_service").id)]
                )
            )
            product = (
                self.env["product.product"]
                .sudo()
                .search(
                    [
                        ("product_tmpl_id", "in", [tmpl.id for tmpl in mobile_templ]),
                        ("default_code", "=", requested_product),
                    ]
                )
            )

            if not contract:
                raise UserError(
                    _("Mobile contract not found with phone: {}".format(mobile_phone))
                )

        elif contract_code:
            contract = (
                self.env["contract.contract"]
                .sudo()
                .search(
                    [
                        ("code", "=", contract_code),
                        "|",
                        ("date_end", ">", date.today().strftime("%Y-%m-%d")),
                        ("date_end", "=", False),
                    ]
                )
            )

            fiber_templ = (
                self.env["product.template"]
                .sudo()
                .search(
                    [
                        (
                            "categ_id",
                            "=",
                            self.env.ref("somconnexio.broadband_fiber_service").id,
                        )
                    ]
                )
            )
            product = (
                self.env["product.product"]
                .sudo()
                .search(
                    [
                        ("product_tmpl_id", "in", [tmpl.id for tmpl in fiber_templ]),
                        ("default_code", "=", requested_product),
                    ]
                )
            )

            if not contract:
                raise UserError(
                    _("Contract not found with code: {}".format(contract_code))
                )

        if not product:
            raise UserError(
                _("Product not found with code: {}".format(requested_product))  # noqa
            )

        if params.get("start_date"):
            start_date = self._extract_date_from_string(params["start_date"])
        else:
            start_date = first_day_next_month()

        if params.get("parent_pack_contract_id"):
            parent_pack_contract = (
                self.env["contract.contract"]
                .sudo()
                .search([("code", "=", params["parent_pack_contract_id"])])
            )
        else:
            parent_pack_contract = self.env["contract.contract"]

        return {
            "contract_id": contract.id,
            "start_date": start_date,
            "new_tariff_product_id": product.id,
            "parent_pack_contract_id": parent_pack_contract.id,
            "shared_bond_id": params.get("shared_bond_id"),
            "summary": "{} {}".format("Canvi de tarifa a", product.showed_name),
        }

    def _extract_date_from_string(self, string_date):
        try:
            date = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").date()
        except ValueError:
            try:
                date = datetime.strptime(string_date, "%Y-%m-%d")
            except ValueError:
                raise UserError(_("Date with unknown format: {}".format(string_date)))
        return date

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_CHANGE_TARIFF

    @staticmethod
    def to_dict(wiz):
        return {"wiz_id": wiz.id}
