from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestPartnerEmailChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        partner = self.env.ref("somconnexio.res_partner_1_demo")
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        partner_email_b = self.env["res.partner"].create(
            {
                "name": "Email b",
                "email": "email_b@example.org",
                "type": "contract-email",
                "parent_id": partner.id,
            }
        )
        self.wizard = (
            self.env["partner.email.change.wizard"]
            .with_context(active_id=partner.id)
            .sudo()
            .create(
                {
                    "change_contact_email": "no",
                    "change_contracts_emails": "yes",
                    "contract_ids": [(6, 0, [contract.id])],
                    "email_ids": [(6, 0, [partner_email_b.id])],
                }
            )
        )

    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.partner_email_change.partner_email_change.ContractEmailChangeProcess"  # noqa
    )
    def test_wizard_run_from_api_ok(self, MockContractEmailChangeProcess):
        params = {"key": "value"}

        self.wizard.run_from_api_contract(**params)

        MockContractEmailChangeProcess.assert_called_once()
        MockContractEmailChangeProcess.return_value.run_from_api.assert_called_once_with(  # noqa
            **params
        )
