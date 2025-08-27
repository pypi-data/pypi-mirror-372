import logging

from odoo.exceptions import UserError
from .base import BaseContractProcess

_logger = logging.getLogger(__name__)


class SBContractProcess(BaseContractProcess):
    _name = "sb.contract.process"
    _inherit = "base.contract.process"
    _description = """
        Switchboard Contract creation
    """

    def _prepare_create(self, params):
        params_result = super()._prepare_create(params)

        if params.get("switchboard_contract_service_info"):
            switchboard_contract_service_info = (
                self._create_switchboard_contract_service_info(
                    params["switchboard_contract_service_info"]
                )
            )
            params_result.update(
                {
                    "name": switchboard_contract_service_info.phone_number,
                    "switchboard_service_contract_info_id": (
                        switchboard_contract_service_info.id
                    ),
                }
            )

        return params_result

    @staticmethod
    def validate_service_technology_deps(params):
        errors = []
        sb_supplier = "Enreach Contact"
        if params["service_supplier"] != sb_supplier:
            errors.append(f"Switchboard needs {sb_supplier} supplier")
        if "switchboard_contract_service_info" not in params:
            errors.append("Switchboard needs switchboard_contract_service_info")
        if errors:
            raise UserError("\n".join(errors))

    def _create_switchboard_contract_service_info(self, params):
        if not params:
            return False
        return (
            self.env["switchboard.service.contract.info"]
            .sudo()
            .create({
                "phone_number": params.get("phone_number"),
                "phone_number_2": params.get("phone_number_2"),
                "mobile_phone_number": params.get("mobile_phone_number"),
                "icc": params.get("icc"),
                "agent_name": params.get("agent_name"),
                "agent_email": params.get("agent_email"),
                "extension": params.get("extension"),
                "MAC_CPE_SIP": params.get("MAC_CPE_SIP"),
                "SIP_channel_name": params.get("SIP_channel_name"),
                "SIP_channel_password": params.get("SIP_channel_password"),
            })
        )
