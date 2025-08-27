from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.exceptions import AccessError


class TestContractProcess(SCTestCase):
    def setUp(self):
        super().setUp()
        self.ContractContractProcess = self.env["contract.contract.process"]
        self.public_user = self.env.ref("base.public_user")
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        self.mobile_data = {
            "partner_id": partner.ref,
            "email": partner.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": partner.bank_ids[0].acc_number,
        }

    def test_create_mobile_contract_directly_fail_with_public_user(self):
        """Test that creating a mobile contract through the mobile.contract.process
        model with a public user raises an AccessError (no sudo layer)."""

        with self.assertRaises(AccessError):
            self.env["mobile.contract.process"].with_user(self.public_user.id).create(
                **self.mobile_data
            )

    def test_create_mobile_contract_with_public_user(self):
        """Test that creating a mobile contract through the ContractContractProcess
        model with a public user does not raise an AccessError (sudo layer)."""

        contract = self.ContractContractProcess.with_user(self.public_user.id).create(
            **self.mobile_data
        )
        self.assertTrue(contract)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.mobile.MobileContractProcess.create"  # noqa
    )
    def test_create_mobile_contract(self, mock_mobile_contract_process_create):
        expected_contract = object
        mock_mobile_contract_process_create.return_value = expected_contract
        data = {
            "service_technology": "Mobile",
        }
        contract = self.ContractContractProcess.create(**data)

        self.assertEqual(contract, expected_contract)
        mock_mobile_contract_process_create.assert_called_once_with(**data)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.adsl.ADSLContractProcess.create"  # noqa
    )
    def test_create_adsl_contract(self, mock_adsl_contract_process_create):
        expected_contract = object
        mock_adsl_contract_process_create.return_value = expected_contract
        data = {
            "service_technology": "ADSL",
        }
        contract = self.ContractContractProcess.create(**data)

        self.assertEqual(contract, expected_contract)
        mock_adsl_contract_process_create.assert_called_once_with(**data)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess.create"  # noqa
    )
    def test_create_fiber_contract(self, mock_fiber_contract_process_create):
        expected_contract = object
        mock_fiber_contract_process_create.return_value = expected_contract
        data = {
            "service_technology": "Fiber",
        }
        contract = self.ContractContractProcess.create(**data)

        self.assertEqual(contract, expected_contract)
        mock_fiber_contract_process_create.assert_called_once_with(**data)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.router4g.Router4GContractProcess.create"  # noqa
    )
    def test_create_router4g_contract(self, mock_router4g_contract_process_create):
        expected_contract = object
        mock_router4g_contract_process_create.return_value = expected_contract
        data = {
            "service_technology": "4G",
        }
        contract = self.ContractContractProcess.create(**data)

        self.assertEqual(contract, expected_contract)
        mock_router4g_contract_process_create.assert_called_once_with(**data)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.switchboard.SBContractProcess.create"  # noqa
    )
    def test_create_switchboard_contract(self, mock_sb_contract_process_create):
        expected_contract = object
        mock_sb_contract_process_create.return_value = expected_contract
        data = {
            "service_technology": "Switchboard",
        }
        contract = self.ContractContractProcess.create(**data)

        self.assertEqual(contract, expected_contract)
        mock_sb_contract_process_create.assert_called_once_with(**data)
