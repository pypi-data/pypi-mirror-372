import logging

from odoo.exceptions import UserError

from .ba import BAContractProcess

_logger = logging.getLogger(__name__)


class ADSLContractProcess(BAContractProcess):
    _name = "adsl.contract.process"
    _inherit = "ba.contract.process"
    _description = """
        ADSL Contract creation
    """

    @staticmethod
    def validate_service_technology_deps(params):
        errors = []
        if params["service_supplier"] != "Jazztel":
            errors.append("ADSL needs Jazztel supplier")
        if "service_address" not in params:
            errors.append('ADSL needs "service_address"')
        if "adsl_contract_service_info" not in params:
            errors.append("ADSL needs adsl_contract_service_info")
        if errors:
            raise UserError("\n".join(errors))

    def _create_adsl_contract_service_info(self, params):
        if not params:
            return False
        router_product = self._get_router_product_id(params["router_product_id"])
        router_lot_id = self._create_router_lot_id(
            params["router_serial_number"],
            router_product,
        )
        return (
            self.env["adsl.service.contract.info"]
            .sudo()
            .create(
                {
                    "phone_number": params["phone_number"],
                    "administrative_number": params["administrative_number"],
                    "router_product_id": router_product.id,
                    "ppp_user": params["ppp_user"],
                    "ppp_password": params["ppp_password"],
                    "endpoint_user": params["endpoint_user"],
                    "endpoint_password": params["endpoint_password"],
                    "router_lot_id": router_lot_id.id,
                }
            )
        )
