from datetime import datetime
from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractTariffChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        start_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
        product = self.browse_ref("somconnexio.150Min2GB")
        contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        self.wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=contract.id)
            .sudo()
            .create(
                {
                    "start_date": start_date,
                    "summary": "Tariff change 150 min 2 GB",
                    "new_tariff_product_id": product.id,
                }
            )
        )

    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.contract_tariff_change.contract_tariff_change.ContractChangeTariffProcess"  # noqa
    )
    def test_wizard_run_from_api_ok(self, MockContractChangeTariffProcess):
        params = {"key": "value"}

        self.wizard.run_from_api(**params)

        MockContractChangeTariffProcess.assert_called_once()
        MockContractChangeTariffProcess.return_value.run_from_api.assert_called_once_with(  # noqa
            **params
        )
