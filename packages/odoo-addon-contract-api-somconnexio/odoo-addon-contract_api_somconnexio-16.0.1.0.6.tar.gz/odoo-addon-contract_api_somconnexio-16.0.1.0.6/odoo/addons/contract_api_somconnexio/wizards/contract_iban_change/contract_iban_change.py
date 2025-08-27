from odoo import models

from ...services.contract_iban_change_process import ContractIbanChangeProcess


class ContractIbanChangeWizard(models.TransientModel):
    _inherit = "contract.iban.change.wizard"

    def run_from_api(self, **params):
        service = ContractIbanChangeProcess(self.env)
        service.run_from_api(**params)
