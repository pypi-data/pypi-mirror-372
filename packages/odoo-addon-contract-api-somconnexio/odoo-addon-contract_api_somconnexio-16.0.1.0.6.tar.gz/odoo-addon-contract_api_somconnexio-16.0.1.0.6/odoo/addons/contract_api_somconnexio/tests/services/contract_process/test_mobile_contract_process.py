from .base_test_contract_process import BaseContractProcessTestCase
from unittest.mock import patch
from odoo.exceptions import UserError


class TestMobileContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
        }
        self.pack_code = self.browse_ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        ).default_code

        self.fiber_contract_data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra100Mb").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
        }
        other_partner = self.browse_ref("somconnexio.res_partner_1_demo")
        sharing_product = self.browse_ref("somconnexio.50GBCompartides2mobils")
        self.sharing_mobile_data = {
            "partner_id": other_partner.ref,
            "email": other_partner.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
                # "shared_bond_id": "",
            },
            "contract_lines": [
                {
                    "product_code": sharing_product.default_code,
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": other_partner.bank_ids[0].acc_number,
        }

        self.MobileContractProcess = self.env["mobile.contract.process"]
        self.FiberContractProcess = self.env["fiber.contract.process"]

    def test_contract_create(self, *args):
        content = self.MobileContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertIn(
            self.browse_ref("somconnexio.150Min1GB"),
            [c.product_id for c in contract.contract_line_ids],
        )

    # def test_contract_create_with_shared_data(self, *args):
    #     # shared_bond_id = "AAAA"
    #     mobile_content = self.data.copy()
    #     # mobile_content["mobile_contract_service_info"].update(
    #     #    {"shared_bond_id": shared_bond_id}
    #     # )
    #
    #     content = self.MobileContractProcess.create(**self.data)
    #     contract = self.env["contract.contract"].browse(content["id"])
    #     # self.assertEqual(
    #     #    contract.mobile_contract_service_info_id.shared_bond_id, shared_bond_id
    #     # )

    def test_contract_create_with_empty_shared_data(self, *args):
        shared_bond_id = {}

        mobile_content = self.data.copy()
        mobile_content["mobile_contract_service_info"].update(
            {"shared_bond_id": shared_bond_id}
        )

        content = self.MobileContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertFalse(
            contract.mobile_contract_service_info_id.shared_bond_id,
        )

    @patch(
        "odoo.addons.somconnexio.models.contract.Contract._change_tariff_only_in_ODOO"
    )
    def test_create_mobile_sharing_bond_1_to_2(self, mock_change_tariff_odoo, *args):
        """
        No sharing data contract can stay without beeing linked to
        another, but every contract is created independently from the API,
        so always one will be first.
        """

        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        new_shared_bond = "A83028"
        sharing_product_2 = self.browse_ref("somconnexio.50GBCompartides2mobils")

        first_contract_mobile_data = self.sharing_mobile_data.copy()
        first_contract_mobile_data["mobile_contract_service_info"][
            "shared_bond_id"
        ] = new_shared_bond
        first_contract_mobile_data["parent_pack_contract_id"] = fiber_contract.code

        content = self.MobileContractProcess.create(**first_contract_mobile_data)
        first_sharing_contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(len(first_sharing_contract.contracts_in_pack), 2)

        second_contract_mobile_data = self.sharing_mobile_data.copy()
        second_contract_mobile_data["mobile_contract_service_info"][
            "shared_bond_id"
        ] = new_shared_bond
        second_contract_mobile_data.update(
            {
                "parent_pack_contract_id": fiber_contract.code,
            }
        )

        content = self.MobileContractProcess.create(**second_contract_mobile_data)
        second_sharing_contract = self.env["contract.contract"].browse(content["id"])

        # No tariff change applied to first contract
        mock_change_tariff_odoo.assert_not_called()

        self.assertEqual(
            first_sharing_contract.shared_bond_id,
            second_sharing_contract.shared_bond_id,
        )
        self.assertEqual(len(first_sharing_contract.contracts_in_pack), 3)
        self.assertEqual(
            first_sharing_contract.contracts_in_pack,
            second_sharing_contract.contracts_in_pack,
        )
        self.assertIn(
            first_sharing_contract,
            second_sharing_contract.contracts_in_pack,
        )
        self.assertEqual(
            first_sharing_contract.current_tariff_product, sharing_product_2
        )

    def test_create_mobile_sharing_bond_2_to_3(self, *args):
        sharing_contract = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        sharing_contract._compute_contracts_in_pack()
        sharing_data_product_2 = self.browse_ref("somconnexio.50GBCompartides2mobils")
        sharing_data_product_3 = self.browse_ref("somconnexio.50GBCompartides3mobils")

        shared_bond_id = sharing_contract.shared_bond_id
        self.sharing_mobile_data["mobile_contract_service_info"][
            "shared_bond_id"
        ] = shared_bond_id
        self.sharing_mobile_data["contract_lines"][0][
            "product_code"
        ] = sharing_data_product_3.default_code
        self.sharing_mobile_data[
            "parent_pack_contract_id"
        ] = sharing_contract.parent_pack_contract_id.code

        self.assertEqual(len(sharing_contract.contracts_in_pack), 3)
        self.assertEqual(
            sharing_contract.current_tariff_product, sharing_data_product_2
        )
        content = self.MobileContractProcess.create(**self.sharing_mobile_data)
        contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(contract.shared_bond_id, shared_bond_id)
        self.assertEqual(len(sharing_contract.contracts_in_pack), 4)
        self.assertIn(
            contract,
            sharing_contract.contracts_in_pack,
        )
        sharing_contract._compute_current_tariff_contract_line()
        self.assertEqual(
            sharing_contract.current_tariff_product, sharing_data_product_3
        )

    @patch(
        "odoo.addons.somconnexio.models.contract.Contract._change_tariff_only_in_ODOO"
    )
    def test_create_mobile_sharing_bond_3_sequential(
        self, mock_change_tariff_ODOO, *args
    ):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        shared_bond_id = "A83028"
        sharing_3_mobiles_data = self.sharing_mobile_data.copy()
        sharing_data_product_3 = self.browse_ref("somconnexio.50GBCompartides3mobils")

        sharing_3_mobiles_data.update(
            {
                "mobile_contract_service_info": {
                    "phone_number": "654321123",
                    "icc": "123456",
                    "shared_bond_id": shared_bond_id,
                },
                "contract_lines": [
                    {
                        "product_code": sharing_data_product_3.default_code,
                        "date_start": "2023-01-01 00:00:00",
                    }
                ],
                "parent_pack_contract_id": fiber_contract.code,
            }
        )

        content = self.MobileContractProcess.create(**sharing_3_mobiles_data)
        first_contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(len(first_contract.contracts_in_pack), 2)
        self.assertEqual(first_contract.current_tariff_product, sharing_data_product_3)

        sharing_3_mobiles_data["mobile_contract_service_info"].update(
            {
                "phone_number": "654321124",
                "icc": "123457",
            }
        )
        content = self.MobileContractProcess.create(**sharing_3_mobiles_data)
        second_contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(len(second_contract.contracts_in_pack), 3)
        self.assertEqual(second_contract.current_tariff_product, sharing_data_product_3)

        sharing_3_mobiles_data["mobile_contract_service_info"].update(
            {
                "phone_number": "654321125",
                "icc": "123458",
            }
        )
        content = self.MobileContractProcess.create(**sharing_3_mobiles_data)
        third_contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(len(third_contract.contracts_in_pack), 4)
        self.assertEqual(third_contract.current_tariff_product, sharing_data_product_3)

        mock_change_tariff_ODOO.assert_not_called()

    def test_create_mobile_sharing_bond_3_to_4(self, *args):
        sharing_contract = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_3"
        )
        sharing_contract._compute_contracts_in_pack()
        sharing_data_product_3 = self.browse_ref("somconnexio.50GBCompartides3mobils")

        shared_bond_id = sharing_contract.shared_bond_id
        self.sharing_mobile_data["mobile_contract_service_info"][
            "shared_bond_id"
        ] = shared_bond_id
        self.sharing_mobile_data["contract_lines"][0][
            "product_code"
        ] = sharing_data_product_3.default_code
        self.sharing_mobile_data[
            "parent_pack_contract_id"
        ] = sharing_contract.parent_pack_contract_id.code

        self.assertEqual(len(sharing_contract.contracts_in_pack), 4)
        self.assertEqual(
            sharing_contract.current_tariff_product, sharing_data_product_3
        )

        self.assertRaisesRegex(
            UserError,
            "No more than 3 mobiles can be packed together",
            self.MobileContractProcess.create,
            **self.sharing_mobile_data
        )
