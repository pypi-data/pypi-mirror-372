from odoo import models
from ...services.contract_one_shot_process import ContractOneShotProcess


class ContractOneShotRequestWizard(models.TransientModel):
    _inherit = "contract.one.shot.request.wizard"

    def run_from_api(self, **params):
        service = ContractOneShotProcess(self.env)
        service.run_from_api(**params)
