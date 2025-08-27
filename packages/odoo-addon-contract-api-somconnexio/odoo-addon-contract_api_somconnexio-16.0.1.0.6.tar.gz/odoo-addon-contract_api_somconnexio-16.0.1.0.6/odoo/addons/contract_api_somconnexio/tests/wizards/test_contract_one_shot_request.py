from datetime import datetime
from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractOneShotRequestWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        start_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
        product = self.browse_ref("somconnexio.EnviamentSIM")
        contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        self.wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=contract.id)
            .sudo()
            .create(
                {
                    "start_date": start_date,
                    "one_shot_product_id": product.id,
                    "summary": "",
                    "done": True,
                }
            )
        )

    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.contract_one_shot_request.contract_one_shot_request.ContractOneShotProcess"  # noqa
    )
    def test_wizard_run_from_api_ok(self, MockContractOneShotProcess):
        params = {"key": "value"}

        self.wizard.run_from_api(**params)

        MockContractOneShotProcess.assert_called_once()
        MockContractOneShotProcess.return_value.run_from_api.assert_called_once_with(
            **params
        )
