from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractIBANChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.partner_mandate = self.browse_ref(
            "somconnexio.demo_mandate_partner_1_demo"
        )
        self.user_admin = self.browse_ref("base.user_admin")
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        self.wizard = (
            self.env["contract.iban.change.wizard"]
            .with_context(active_id=self.partner.id)
            .sudo()
            .create(
                {
                    "contract_ids": [(6, 0, [self.contract.id])],
                    "account_banking_mandate_id": self.partner_mandate.id,
                }
            )
        )

    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.contract_iban_change.contract_iban_change.ContractIbanChangeProcess"  # noqa
    )
    def test_wizard_from_api_ok(self, MockContractIbanChangeProcess):
        self.wizard.run_from_api()

        MockContractIbanChangeProcess.assert_called_once()
        MockContractIbanChangeProcess.return_value.run_from_api.assert_called_once()
