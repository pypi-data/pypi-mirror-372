import logging

from odoo import models, _

from .. import schemas
from odoo.exceptions import UserError

try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ErrorNotImplemented(Exception):
    pass


# pylint: disable=W8106
class BaseContractProcess(models.AbstractModel):
    _name = "base.contract.process"
    _register = True
    _description = """
        Base Contract creation
    """

    @staticmethod
    def validate_service_technology_deps(params):
        raise ErrorNotImplemented()

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_CREATE

    def _validate(self, params):
        v = Validator(purge_unknown=True)
        if not v.validate(
            params,
            self.validator_create(),
        ):
            raise UserError(_("BadRequest {}").format(v.errors))
        self.validate_service_technology_deps(params)

    def create(self, **params):
        _logger.info("Create contract received with body: {}".format(params))
        self._validate(params)
        params = self._prepare_create(params)
        cc = self.env["contract.contract"].create(params)
        return self._to_dict(cc)

    @staticmethod
    def _to_dict(contract):
        return {
            **contract._to_dict(),
            "partner_id": contract.partner_id.id,
            "create_reason": contract.create_reason,
        }

    def _prepare_create_line(self, line):
        product = (
            self.env["product.product"]
            .sudo()
            .search([("default_code", "=", line["product_code"])])
        )
        if not product:
            raise UserError(
                _("Product with code %s not found") % (line["product_code"],)
            )
        response_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": line["date_start"],
        }
        return response_line

    def _check_service_combination(self, technology_id, supplier_id):
        if (
            not self.env["service.technology.service.supplier"]
            .sudo()
            .search(
                [
                    ("service_technology_id", "=", technology_id),
                    ("service_supplier_id", "=", supplier_id),
                ]
            )
        ):
            return False
        else:
            return True

    def _create_mobile_contract_service_info(self, params):
        return False

    def _create_adsl_contract_service_info(self, params):
        return False

    def _create_router_4G_contract_service_info(self, params):
        return False

    def _create_vodafone_fiber_contract_service_info(self, params):
        return False

    def _create_mm_fiber_contract_service_info(self, params):
        return False

    def _create_orange_fiber_contract_service_info(self, params):
        return False

    def _create_xoln_fiber_contract_service_info(self, params):
        return False

    def _create_switchboard_contract_service_info(self, params):
        return False

    def _prepare_service_partner_id(self, partner_id, service_address):
        service_address_obj = (
            self.env["res.partner"]
            .sudo()
            .search(
                [
                    ("parent_id", "=", partner_id),
                    ("street", "=", service_address["street"]),
                    ("zip", "=", service_address["zip_code"]),
                    ("city", "=", service_address["city"]),
                    ("state_id.code", "=", service_address["state"]),
                    ("type", "=", "service"),
                ]
            )
        )
        if not service_address_obj:
            state = (
                self.env["res.country.state"]
                .sudo()
                .search(
                    [
                        ("country_id", "=", self.env.ref("base.es").id),
                        ("code", "=", service_address["state"]),
                    ]
                )
            )
            service_address_obj = (
                self.env["res.partner"]
                .sudo()
                .create(
                    {
                        "parent_id": partner_id,
                        "street": service_address["street"],
                        "zip": service_address["zip_code"],
                        "city": service_address["city"],
                        "state_id": state.id,
                        "type": "service",
                    }
                )
            )
        return service_address_obj.id

    # TODO -> Refactor this method to separate technology logic in different classes
    def _prepare_create(self, params):
        if "code" in params:
            code = params["code"]
        else:
            code = None
        partner = (
            self.env["res.partner"]
            .sudo()
            .search(
                [
                    ("ref", "=", params["partner_id"]),
                ]
            )
        )
        partner_id = partner.id
        if not partner:
            raise UserError(_("Partner id %s not found") % (partner_id,))
        partner_email = partner.get_or_create_contract_email(params["email"])

        contract_lines = []
        # We must evaluate the "contract_line" field because OTRS cannot send a list
        # with only one element, so we do this differentiation to know how to treat it.
        if params.get("contract_line"):
            params["contract_lines"] = [params.get("contract_line")]
        contract_lines.extend(
            self._prepare_create_line(line) for line in params["contract_lines"]
        )
        mobile_contract_service_info = self._create_mobile_contract_service_info(
            params.get("mobile_contract_service_info")
        )
        adsl_contract_service_info = self._create_adsl_contract_service_info(
            params.get("adsl_contract_service_info")
        )
        vodafone_fiber_contract_service_info = (
            self._create_vodafone_fiber_contract_service_info(
                params.get("vodafone_fiber_contract_service_info")
            )
        )
        router_4G_contract_service_info = self._create_router_4G_contract_service_info(
            params.get("router_4G_contract_service_info")
        )
        mm_fiber_contract_service_info = self._create_mm_fiber_contract_service_info(
            params.get("mm_fiber_contract_service_info")
        )
        xoln_fiber_contract_service_info = (
            self._create_xoln_fiber_contract_service_info(
                params.get("xoln_fiber_contract_service_info")
            )
        )
        orange_fiber_contract_service_info = (
            self._create_orange_fiber_contract_service_info(
                params.get("orange_fiber_contract_service_info")
            )
        )
        name = ""
        if mobile_contract_service_info:
            name = mobile_contract_service_info.phone_number
        elif adsl_contract_service_info:
            name = adsl_contract_service_info.phone_number
        elif vodafone_fiber_contract_service_info:
            name = vodafone_fiber_contract_service_info.phone_number
        elif router_4G_contract_service_info:
            name = router_4G_contract_service_info.phone_number
        elif mm_fiber_contract_service_info:
            name = mm_fiber_contract_service_info.phone_number
        elif xoln_fiber_contract_service_info:
            name = xoln_fiber_contract_service_info.phone_number
        elif orange_fiber_contract_service_info:
            name = orange_fiber_contract_service_info.phone_number
        if "service_partner_id" in params:
            service_partner_id = params["service_partner_id"]
        elif "service_address" in params:
            service_partner_id = self._prepare_service_partner_id(
                partner_id, params["service_address"]
            )
        else:
            service_partner_id = False

        fiber_signal_type_id = ""
        if params.get("fiber_signal_type"):
            fiber_signal_type_id = (
                self.env["fiber.signal.type"]
                .sudo()
                .search(
                    [
                        ("code", "=", params["fiber_signal_type"]),
                    ]
                )
                .id
            )

        sanitized_iban = params["iban"].replace(" ", "").upper()
        mandate = partner.get_mandate(sanitized_iban)
        response = {
            "name": name,
            "partner_id": partner_id,
            "email_ids": [(4, partner_email.id, False)],
            "service_partner_id": service_partner_id,
            "mobile_contract_service_info_id": (
                mobile_contract_service_info and mobile_contract_service_info.id
            ),
            "adsl_service_contract_info_id": (
                adsl_contract_service_info and adsl_contract_service_info.id
            ),
            "vodafone_fiber_service_contract_info_id": (
                vodafone_fiber_contract_service_info
                and vodafone_fiber_contract_service_info.id
            ),
            "mm_fiber_service_contract_info_id": (
                mm_fiber_contract_service_info and mm_fiber_contract_service_info.id
            ),
            "xoln_fiber_service_contract_info_id": (
                xoln_fiber_contract_service_info and xoln_fiber_contract_service_info.id
            ),
            "orange_fiber_service_contract_info_id": (
                orange_fiber_contract_service_info
                and orange_fiber_contract_service_info.id
            ),
            "router_4G_service_contract_info_id": (
                router_4G_contract_service_info and router_4G_contract_service_info.id
            ),
            "invoice_partner_id": partner_id,
            "service_technology_id": self._get_service_tech(
                params["service_technology"]
            ).id,
            "service_supplier_id": self._get_service_supplier(
                params["service_supplier"]
            ).id,
            "fiber_signal_type_id": fiber_signal_type_id,
            "payment_mode_id": self.env.ref("somconnexio.payment_mode_inbound_sepa").id,
            "mandate_id": mandate.id,
            "line_recurrence": True,
        }
        if code:
            response["code"] = code
        if not self._check_service_combination(
            response["service_technology_id"], response["service_supplier_id"]
        ):
            raise UserError(
                _("Bad combination {} and {}").format(
                    params["service_technology"], params["service_supplier"]
                )
            )

        if contract_lines:
            response.update(
                {
                    "contract_line_ids": [
                        (0, False, contract_line) for contract_line in contract_lines
                    ],
                }
            )
        return response

    def _get_service_tech(self, name):
        service_tech = self.env["service.technology"].search([("name", "=", name)])
        if service_tech:
            return service_tech
        else:
            raise UserError(_("No service technology for name %s") % name)

    def _get_service_supplier(self, name):
        service_supplier = self.env["service.supplier"].search([("name", "=", name)])
        if service_supplier:
            return service_supplier
        else:
            raise UserError(_("No service supplier for name %s") % name)
