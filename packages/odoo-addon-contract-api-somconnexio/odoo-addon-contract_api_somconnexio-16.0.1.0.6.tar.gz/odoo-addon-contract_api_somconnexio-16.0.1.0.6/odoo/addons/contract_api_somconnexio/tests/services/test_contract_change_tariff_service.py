import json
from mock import patch

from odoo.exceptions import UserError
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.somconnexio.helpers.date import (
    first_day_next_month,
    date_to_str,
    last_day_of_this_month,
)

from ...services.contract_change_tariff_process import ContractChangeTariffProcess


class TestContractChangeTariffService(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp()
        # Mobile
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.old_mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades20GB")
        self.new_mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades50GB")
        self.mobile_data = {
            "product_code": self.new_mobile_product.default_code,
            "phone_number": self.mobile_contract.phone_number,
        }

        # Fiber contract
        self.fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.old_fiber_product = self.browse_ref("somconnexio.Fibra600Mb")
        self.new_fiber_product = self.browse_ref("somconnexio.Fibra100Mb")
        self.fiber_data = {
            "product_code": self.new_fiber_product.default_code,
            "code": self.fiber_contract.code,
        }

        # General
        self.partner = self.mobile_contract.partner_id
        self.url = "/public-api/change-tariff"

    def test_route_right_run_wizard_mobile_without_date(self):
        response = self.http_public_post(self.url, data=self.mobile_data)
        expected_start_date = first_day_next_month()

        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        partner_activities = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        created_activity = partner_activities[-1]

        self.assertTrue(self.mobile_contract.contract_line_ids[0].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].product_id,
            self.old_mobile_product,
        )
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].product_id,
            self.new_mobile_product,
        )
        self.assertEqual(
            created_activity.summary,
            "Canvi de tarifa a {}".format(self.new_mobile_product.showed_name),
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_right_mobile_with_start_date(self):
        expected_start_date = first_day_next_month()
        expected_finished_date = last_day_of_this_month()
        self.mobile_data.update({"start_date": date_to_str(expected_start_date)})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)

        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].date_end, expected_finished_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].product_id,
            self.old_mobile_product,
        )
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].product_id,
            self.new_mobile_product,
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_right_mobile_with_OTRS_formatted_date(self):
        expected_start_date = first_day_next_month()
        expected_finished_date = last_day_of_this_month()
        self.mobile_data.update(
            {"start_date": "{} 00:00:00".format(date_to_str(expected_start_date))}
        )

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)

        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].date_end, expected_finished_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].product_id,
            self.old_mobile_product,
        )
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].product_id,
            self.new_mobile_product,
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_right_mobile_empty_start_date(self):
        self.mobile_data.update({"start_date": ""})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        expected_start_date = first_day_next_month()

        self.assertTrue(self.mobile_contract.contract_line_ids[0].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[0].product_id,
            self.old_mobile_product,
        )
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.mobile_contract.contract_line_ids[1].product_id,
            self.new_mobile_product,
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_bad_mobile_phone(self):
        wrong_phone = "8383838"
        self.mobile_data.update({"phone_number": wrong_phone})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Mobile contract not found with phone: {}".format(wrong_phone),
            process.run_from_api,
            **self.mobile_data
        )

    def test_route_bad_product(self):
        wrong_product = "FAKE_DEFAULT_CODE"
        self.mobile_data.update({"product_code": wrong_product})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Product not found with code: {}".format(wrong_product),
            process.run_from_api,
            **self.mobile_data
        )

    def test_route_bad_date(self):
        wrong_date = "202-202-202"
        self.mobile_data.update({"start_date": wrong_date})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Date with unknown format: {}".format(wrong_date),
            process.run_from_api,
            **self.mobile_data
        )

    def test_route_neither_phone_nor_code(self):
        self.mobile_data.update({"phone_number": "", "code": ""})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaises(UserError, process.run_from_api, **self.mobile_data)

    def test_route_right_run_wizard_fiber_without_date(self):
        response = self.http_public_post(self.url, data=self.fiber_data)
        expected_start_date = first_day_next_month()

        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.fiber_data)
        partner_activities = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        created_activity = partner_activities[-1]

        self.assertTrue(self.fiber_contract.contract_line_ids[0].date_end)
        self.assertEqual(
            self.fiber_contract.contract_line_ids[0].product_id, self.old_fiber_product
        )
        self.assertFalse(self.fiber_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.fiber_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.fiber_contract.contract_line_ids[1].product_id, self.new_fiber_product
        )
        self.assertEqual(
            created_activity.summary,
            "Canvi de tarifa a {}".format(self.new_fiber_product.showed_name),
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_right_fiber_with_start_date(self):
        expected_start_date = first_day_next_month()
        expected_finished_date = last_day_of_this_month()
        self.fiber_data.update({"start_date": date_to_str(expected_start_date)})

        response = self.http_public_post(self.url, data=self.fiber_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.fiber_data)

        self.assertEqual(
            self.fiber_contract.contract_line_ids[0].date_end, expected_finished_date
        )
        self.assertEqual(
            self.fiber_contract.contract_line_ids[0].product_id, self.old_fiber_product
        )
        self.assertFalse(self.fiber_contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.fiber_contract.contract_line_ids[1].date_start, expected_start_date
        )
        self.assertEqual(
            self.fiber_contract.contract_line_ids[1].product_id, self.new_fiber_product
        )
        self.assertFalse(self.mobile_contract.parent_pack_contract_id)

    def test_route_bad_fiber_contract_code(self):
        wrong_code = "inexisting_code"
        self.fiber_data.update({"code": wrong_code})

        response = self.http_public_post(self.url, data=self.fiber_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Contract not found with code: {}".format(wrong_code),
            process.run_from_api,
            **self.fiber_data
        )

    def test_route_right_run_wizard_parent_pack_contract(self):
        self.mobile_data.update({"parent_pack_contract_id": self.fiber_data["code"]})
        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        self.assertEqual(
            self.mobile_contract.parent_pack_contract_id, self.fiber_contract
        )

    @patch(
        "odoo.addons.somconnexio.models.contract.Contract.update_pack_mobiles_tariffs_after_joining_pack"  # noqa
    )
    def test_route_right_run_wizard_update_sharing_mobiles(
        self, mock_update_sharing_mobiles
    ):
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        sharing_data_product_3 = self.env.ref("somconnexio.50GBCompartides3mobils")
        shared_bond_id = sharing_contract.shared_bond_id
        expected_start_date = first_day_next_month()
        self.mobile_data.update(
            {
                "phone_number": self.mobile_contract.phone_number,
                "product_code": sharing_data_product_3.default_code,
                "shared_bond_id": shared_bond_id,
                "start_date": date_to_str(expected_start_date),
            }
        )
        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        self.assertEqual(self.mobile_contract.shared_bond_id, shared_bond_id)
        mock_update_sharing_mobiles.assert_called_once_with(
            process._extract_date_from_string(self.mobile_data["start_date"])
        )

    @patch(
        "odoo.addons.somconnexio.models.contract.Contract.quit_pack_and_update_mobile_tariffs",  # noqa
    )
    def test_run_wizard_quit_sharing_mobiles(self, mock_quit_sharing_bond):
        contract = self.browse_ref("somconnexio.contract_mobile_il_50_shared_1_of_3")
        sharing_contract = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_3"
        )
        contract._compute_contracts_in_pack()
        self.assertEqual(len(contract.contracts_in_pack), 4)
        self.assertIn(contract, sharing_contract.contracts_in_pack)
        self.assertEqual(
            sharing_contract.current_tariff_product,
            self.browse_ref("somconnexio.50GBCompartides3mobils"),
        )

        # Contract API change
        mobile_data = {
            "product_code": "SE_SC_REC_MOBILE_T_UNL_5120",
            "phone_number": contract.phone_number,
        }

        response = self.http_public_post(self.url, data=mobile_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**mobile_data)

        # Sharing contract contract
    #    mock_quit_sharing_bond.assert_called_once_with()

    # def test_route_right_run_wizard_shared_bond_id_OTRS_empty_character(self):
    #     self.mobile_data.update(
    #         {
    #             "product_code": "SE_SC_REC_MOBILE_2_SHARED_UNL_51200",
    #             "shared_bond_id": {},
    #         }
    #     )
    #     response = self.http_public_post(self.url, data=self.mobile_data)
    #     self.assertEqual(response.status_code, 200)
    #     decoded_response = json.loads(response.content.decode("utf-8"))
    #     self.assertEqual(decoded_response, {"result": "OK"})
    #     process = ContractChangeTariffProcess(self.env)
    #     process.run_from_api(**self.mobile_data)
    #
    #     self.assertFalse(self.mobile_contract.shared_bond_id)
