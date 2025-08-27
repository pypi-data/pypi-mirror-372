from .base_test_contract_process import BaseContractProcessTestCase
from odoo.exceptions import UserError


class TestSBContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.sb_product = self.env.ref(
            "switchboard_somconnexio.CentraletaVirtualSIMBasic"
        )
        self.data = {
            "partner_id": self.partner.ref,
            "service_supplier": "Enreach Contact",
            "service_technology": "Switchboard",
            "ticket_number": "2024112900000015",
            "email": self.partner.email,
            "iban": self.mandate.partner_bank_id.acc_number,
            "switchboard_contract_service_info": {
                "SIP_channel_name": self.fake.name(),
                "extension": str(self.fake.random_int(1, 99)),
                "SIP_channel_password": self.fake.password(),
                "phone_number": self.fake.phone_number(),
                "phone_number_2": self.fake.phone_number(),
                "mobile_phone_number": self.fake.phone_number(),
                "MAC_CPE_SIP": self.fake.mac_address(),
                "agent_email": self.fake.email(),
                "agent_name": self.fake.name(),
                "icc": "8934048319120034815",
            },
            "contract_lines": [
                {
                    "product_code": self.sb_product.default_code,
                    "date_start": "2024-11-01 00:00:00",
                },
                {"product_code": "CH_SC_OSO_SIM", "date_start": "2024-11-01 00:00:00"},
            ],
        }
        self.SBContractProcess = self.env["sb.contract.process"]

    def test_contract_create(self, *args):
        content = self.SBContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertIn(
            self.sb_product,
            contract.contract_line_ids.mapped("product_id"),
        )
        sb_info = contract.switchboard_service_contract_info_id
        sb_info_original_data = self.data["switchboard_contract_service_info"]

        self.assertEqual(sb_info.phone_number, sb_info_original_data["phone_number"])
        self.assertEqual(
            sb_info.phone_number_2, sb_info_original_data["phone_number_2"]
        )
        self.assertEqual(
            sb_info.mobile_phone_number, sb_info_original_data["mobile_phone_number"]
        )
        self.assertEqual(sb_info.icc, sb_info_original_data["icc"])
        self.assertEqual(sb_info.extension, sb_info_original_data["extension"])
        self.assertEqual(sb_info.agent_name, sb_info_original_data["agent_name"])
        self.assertEqual(sb_info.agent_email, sb_info_original_data["agent_email"])
        self.assertEqual(sb_info.MAC_CPE_SIP, sb_info_original_data["MAC_CPE_SIP"])
        self.assertEqual(
            sb_info.SIP_channel_name, sb_info_original_data["SIP_channel_name"]
        )
        self.assertEqual(
            sb_info.SIP_channel_password, sb_info_original_data["SIP_channel_password"]
        )

    def test_contract_create_missing_sb_contract_info(self, *args):
        self.data.pop("switchboard_contract_service_info")
        self.assertRaisesRegex(
            UserError,
            "Switchboard needs switchboard_contract_service_info",
            self.SBContractProcess.create,
            **self.data
        )

    def test_contract_create_missing_service_supplier(self, *args):
        self.data["service_supplier"] = "Other"
        self.assertRaisesRegex(
            UserError,
            "Switchboard needs Enreach Contact supplier",
            self.SBContractProcess.create,
            **self.data
        )
