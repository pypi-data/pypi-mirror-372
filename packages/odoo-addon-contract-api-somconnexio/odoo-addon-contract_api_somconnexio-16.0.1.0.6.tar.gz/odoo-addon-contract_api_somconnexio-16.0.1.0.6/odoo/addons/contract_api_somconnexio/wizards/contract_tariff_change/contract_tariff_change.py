from odoo import models, fields

from ...services.contract_change_tariff_process import ContractChangeTariffProcess


class ContractTariffChangeWizard(models.TransientModel):
    _inherit = "contract.tariff.change.wizard"
    parent_pack_contract_id = fields.Many2one('contract.contract')
    shared_bond_id = fields.Char('Sharing Bond ID')

    def run_from_api(self, **params):
        service = ContractChangeTariffProcess(self.env)
        service.run_from_api(**params)
