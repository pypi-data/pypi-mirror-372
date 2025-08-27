from odoo import models

from ...services.contract_email_change_process import ContractEmailChangeProcess


class PartnerEmailChangeWizard(models.TransientModel):
    _inherit = "partner.email.change.wizard"

    def run_from_api_contract(self, **params):
        service = ContractEmailChangeProcess(self.env)
        service.run_from_api(**params)
