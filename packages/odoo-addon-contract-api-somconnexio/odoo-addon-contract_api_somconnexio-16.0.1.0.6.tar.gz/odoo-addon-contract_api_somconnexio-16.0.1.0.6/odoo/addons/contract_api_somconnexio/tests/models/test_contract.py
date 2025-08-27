from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class ContractTestCase(SCTestCase):
    def setUp(self):
        self.contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.sb_contract = self.env.ref(
            "switchboard_somconnexio.contract_switchboard_app_500"
        )
        self.shared_bond_mobile_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        self.adsl = self.env.ref("somconnexio.contract_adsl")
        self.adsl_without_fix = self.env.ref("somconnexio.contract_adsl_without_fix")
        self.fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.fourth_g_contract = self.env.ref("somconnexio.contract_4G")
        self.pack_mobile_contract = self.env.ref(
            "somconnexio.contract_mobile_il_20_pack"
        )

    def test_to_dict(self):
        result = self.contract._to_dict()

        self.assertEqual(result["id"], self.contract.id)
        self.assertEqual(result["code"], self.contract.code)
        self.assertEqual(result["email"], self.contract.partner_id.email)
        self.assertEqual(
            result["customer_firstname"], self.contract.partner_id.firstname
        )
        self.assertEqual(
            result["customer_lastname"], self.contract.partner_id.lastname
        )
        self.assertEqual(result["customer_ref"], self.contract.partner_id.ref)
        self.assertEqual(result["customer_vat"], self.contract.partner_id.vat)
        self.assertEqual(result["phone_number"], self.contract.phone_number)
        self.assertEqual(
            result["current_tariff_product"],
            self.contract.current_tariff_product.default_code,
        )
        self.assertEqual(
            result["description"], self.contract.current_tariff_product.showed_name
        )
        self.assertEqual(
            result["technology"], self.contract.service_technology_id.name
        )
        self.assertEqual(result["supplier"], self.contract.service_supplier_id.name)
        self.assertEqual(result["lang"], self.contract.lang)
        self.assertEqual(
            result["iban"],
            self.contract.mandate_id.partner_bank_id.sanitized_acc_number,
        )
        self.assertEqual(result["is_terminated"], self.contract.is_terminated)
        self.assertEqual(result["date_start"], self.contract.date_start)
        self.assertEqual(result["date_end"], self.contract.date_end)
        self.assertEqual(
            result["fiber_signal"], self.contract.fiber_signal_type_id.code
        )
        self.assertEqual(result["subscription_type"], "mobile")
        self.assertEqual(result["address"]["country"], "Spain")
        self.assertEqual(result["address"]["state"], "Girona (Gerona)")
        self.assertEqual(result["address"]["street"], self.contract.partner_id.street)
        self.assertEqual(result["address"]["city"], self.contract.partner_id.city)
        self.assertEqual(result["address"]["zip_code"], self.contract.partner_id.zip)
        self.assertEqual(result["subscription_technology"], "mobile")
        self.assertFalse(result["parent_contract"])
        self.assertFalse(result["shared_bond_id"])
        self.assertFalse(result["has_landline_phone"])
        self.assertEqual(result["data"], 20480)
        self.assertEqual(result["minutes"], 99999)
        self.assertEqual(result["bandwidth"], 0)
        self.assertEqual(result["price"], 13.0)
        self.assertEqual(
            result["available_operations"],
            [
                'ChangeTariffMobile',
                'AddOneShotMobile',
                'ChangeContractHolder'
            ]
        )

    def test_route_contract_search_to_dict_available_operations_switchboard(self):
        result = self.sb_contract._to_dict()

        self.assertEqual(result["id"], self.sb_contract.id)
        self.assertEqual(result["subscription_type"], "switchboard")
        self.assertEqual(
            result["available_operations"],
            [],
        )

    def test_route_contract_search_to_dict_mobile_shared_bond(
        self,
    ):
        result = self.shared_bond_mobile_contract._to_dict()

        self.assertEqual(result["id"], self.shared_bond_mobile_contract.id)
        self.assertEqual(
            result["available_operations"],
            ["AddOneShotMobile"],
        )
        self.assertEqual(
            result["parent_contract"],
            self.shared_bond_mobile_contract.parent_pack_contract_id.code,
        )
        self.assertEqual(
            result["shared_bond_id"],
            self.shared_bond_mobile_contract.shared_bond_id,
        )
        self.assertEqual(
            result["price"],
            7.5,
        )
        self.assertFalse(result["has_landline_phone"])
        self.assertEqual(result["data"], 51200)
        self.assertEqual(result["minutes"], 99999)

    def test_route_contract_search_to_dict_subscription_type_broadband_adsl(self):
        result = self.adsl._to_dict()

        self.assertEqual(result["id"], self.adsl.id)
        self.assertEqual(result["subscription_type"], "broadband")
        self.assertEqual(result["subscription_technology"], "adsl")
        self.assertEqual(
            result["available_operations"],
            ["ChangeContractHolder", "ChangeTariffFiberLandline"],
        )

    def test_route_contract_search_to_dict_subscription_technology_fiber(self):
        result = self.fiber_contract._to_dict()

        self.assertEqual(result["id"], self.fiber_contract.id)
        self.assertEqual(result["subscription_technology"], "fiber")
        self.assertTrue(result["has_landline_phone"])
        self.assertEqual(result["bandwidth"], 600)
        self.assertEqual(
            result["available_operations"],
            ["ChangeContractHolder"],
        )

    def test_route_contract_search_to_dict_available_operations_change_tariff_fiber_out_landline(  # noqa
        self,
    ):
        fiber_wo_fix = self.env.ref("somconnexio.Fibra300Mb")
        fiber_contract_without_line = self.fiber_contract.copy({"name": "test"})
        fiber_contract_without_line.contract_line_ids.update(
            {"product_id": fiber_wo_fix.id}
        )
        result = fiber_contract_without_line._to_dict()

        self.assertEqual(result["id"], fiber_contract_without_line.id)
        self.assertEqual(result["subscription_technology"], "fiber")
        self.assertEqual(
            result["available_operations"],
            ["ChangeTariffFiberOutLandline", "ChangeContractHolder"],
        )

    def test_route_contract_adsl_search_to_dict_available_operations_change_tariff_fiber_out_landline(  # noqa
        self,
    ):
        result = self.adsl_without_fix._to_dict()
        self.assertEqual(result["id"], self.adsl_without_fix.id)
        self.assertEqual(
            result["available_operations"],
            ["ChangeContractHolder", "ChangeTariffFiberOutLandline"],
        )

    def test_route_contract_search_to_dict_available_operations_router_4g(
        self,
    ):
        result = self.fourth_g_contract._to_dict()
        self.assertEqual(result["id"], self.fourth_g_contract.id)
        self.assertEqual(
            result["available_operations"],
            ["ChangeContractHolder"],
        )

    def test_route_contract_search_to_dict_available_operations_t_conserva(self):
        mobile_contract_conserva = self.env.ref(
            "somconnexio.contract_mobile_t_conserva"
        )
        result = mobile_contract_conserva._to_dict()

        self.assertEqual(result["id"], mobile_contract_conserva.id)
        self.assertEqual(
            result["available_operations"],
            ["ChangeTariffMobile", "ChangeContractHolder"],
        )

    def test_route_contract_search_to_dict_mobile_pack(self):
        result = self.pack_mobile_contract._to_dict()

        self.assertEqual(result["id"], self.pack_mobile_contract.id)
        self.assertEqual(
            result["available_operations"],
            ["ChangeTariffMobile", "AddOneShotMobile"],
        )
        self.assertEqual(
            result["parent_contract"],
            self.pack_mobile_contract.parent_pack_contract_id.code,
        )
        self.assertFalse(result["has_landline_phone"])
        self.assertEqual(result["data"], 20480)
        self.assertEqual(result["minutes"], 99999)

    def test_route_contract_search_to_dict_description_translation(
        self,
    ):
        ca_contract = self.adsl._to_dict()
        self.adsl.partner_id.lang = "es_ES"
        es_contract = self.adsl._to_dict()

        # TODO: Review translations
        self.assertEqual(ca_contract["description"], "ADSL 100 min a fix o mòbil")
        self.assertEqual(es_contract["description"], "ADSL 100 min a fix o mòbil")

    def test_route_contract_partner_company(
        self,
    ):
        result = self.adsl_without_fix._to_dict()
        self.assertEqual(result["id"], self.adsl_without_fix.id)
        self.assertEqual(result["customer_firstname"], "")
