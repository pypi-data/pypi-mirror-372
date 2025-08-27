import logging

from odoo import _
from odoo.exceptions import UserError
from .base import BaseContractProcess

_logger = logging.getLogger(__name__)


class MobileContractProcess(BaseContractProcess):
    _name = "mobile.contract.process"
    _inherit = "base.contract.process"
    _description = """
        Mobile Contract creation
    """

    @staticmethod
    def validate_service_technology_deps(params):
        errors = []
        if params["service_technology"] == "Mobile":
            if params["service_supplier"] != "MásMóvil":
                errors.append("Mobile needs MásMóvil supplier")
            if "mobile_contract_service_info" not in params:
                errors.append("Mobile needs mobile_contract_service_info")
        if errors:
            raise UserError("\n".join(errors))

    def _create_mobile_contract_service_info(self, params):
        if not params:
            return False

        # TODO -> Remove this when OTRS stops sending an empty dict
        shared_bond_id = (
            params.get("shared_bond_id") if params.get("shared_bond_id") else False
        )

        return (
            self.env["mobile.service.contract.info"]
            .create(
                {
                    "phone_number": params["phone_number"],
                    "icc": params["icc"],
                    "shared_bond_id": shared_bond_id,
                }
            )
        )

    def _is_pack(self, contract):
        products = contract.contract_line_ids.mapped("product_id")

        if products.filtered(lambda p: p.product_is_pack_exclusive):
            return True
        return False

    def create(self, **params):
        contract_dict = super().create(**params)
        contract = self.env["contract.contract"].browse(contract_dict["id"])
        if self._is_pack(contract):
            self._relate_with_parent_pack_contract(
                contract, params.get("parent_pack_contract_id")
            )
        if contract.shared_bond_id:
            contract.update_pack_mobiles_tariffs_after_joining_pack()
        return contract_dict

    def _get_parent_pack_contract(self, contract, parent_pack_contract_id):
        parent_contract = None
        if parent_pack_contract_id:
            # Search the parent contract (fiber of the same pack)
            parent_contract = (
                self.env["contract.contract"]
                .search(
                    [("code", "=", parent_pack_contract_id)],
                )
            )
            if not parent_contract:
                raise UserError(
                    _(
                        "Fiber contract with ref = {} not found".format(
                            parent_pack_contract_id
                        )
                    )
                )
        return parent_contract

    def _relate_with_parent_pack_contract(self, contract, parent_pack_contract_id):
        parent_contract = self._get_parent_pack_contract(
            contract, parent_pack_contract_id
        )
        if not parent_contract:
            return
        # Save the contract id as parent contract
        contract.write(
            {
                "parent_pack_contract_id": parent_contract.id,
            }
        )
