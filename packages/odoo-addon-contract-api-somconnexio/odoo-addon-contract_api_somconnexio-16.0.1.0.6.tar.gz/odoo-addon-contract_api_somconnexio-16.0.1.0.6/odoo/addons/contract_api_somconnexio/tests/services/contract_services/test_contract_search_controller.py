import json
import odoo
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin


class TestContractSearchController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.url = "/api/contract"
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.fiber_contract = self.env.ref("somconnexio.contract_fibra_600")

    @odoo.tools.mute_logger("odoo.addons.auth_api_key.models.ir_http")
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_without_auth(self):
        response = self.http_public_get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.reason, "FORBIDDEN")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_unknown_parameter(self):
        url = "{}?{}={}".format(self.url, "unknown_parameter", "2828")
        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_multiple_parameters(self):
        url = "{}?{}={}&{}={}".format(
            self.url, "code", "111111", "partner_vat", "ES1828028"
        )
        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_subscription_type_single_parameter(self):
        url = "{}?{}={}".format(self.url, "subscription_type", "mobile")
        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_subscription_type_unallowed_value(self):
        url = "{}?{}={}&{}={}".format(
            self.url,
            "customer_ref",
            "1",
            "subscription_type",
            "some",
        )
        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_code_not_found(self):
        url = "{}?{}={}".format(self.url, "code", "111111")
        response = self.http_get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_vat_not_found(self):
        url = "{}?{}={}".format(self.url, "partner_vat", "111111")
        response = self.http_get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract__not_found(self):
        url = "{}?{}={}".format(self.url, "phone_number", "111111")
        response = self.http_get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    def test_route_contract_search_code_ok(self):
        url = "{}?{}={}".format(self.url, "code", self.mobile_contract.code)
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))

        self.assertEqual(result["contracts"][0]["id"], self.mobile_contract.id)

    def test_route_contract_search_phone_number_ok(self, *args):
        url = "{}?{}={}".format(
            self.url, "phone_number", self.mobile_contract.phone_number
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(result["contracts"]), 1)
        self.assertEqual(result["contracts"][0]["id"], self.mobile_contract.id)

    def test_route_contract_search_partner_code_ok(self):
        url = "{}?{}={}".format(
            self.url, "customer_ref", self.mobile_contract.partner_id.ref
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertIn(self.mobile_contract.id, [c["id"] for c in result["contracts"]])

    def test_route_contract_search_partner_code_multi_filter(self):
        url = "{}?{}={}&{}={}&{}={}".format(
            self.url,
            "customer_ref",
            self.fiber_contract.partner_id.ref,
            "phone_number",
            self.fiber_contract.phone_number,
            "subscription_type",
            "broadband",
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(result["contracts"]), 1)
        self.assertIn(self.fiber_contract.id, [c["id"] for c in result["contracts"]])

    def test_route_contract_search_partner_vat_multiple_ok(self, *args):
        num_contracts = len(
            self.env["contract.contract"].search(
                [("partner_id", "=", self.partner.id)],
                limit=10,
            )
        )
        url = "{}?{}={}".format(self.url, "partner_vat", self.partner.vat)
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertIn("contracts", result)
        self.assertEqual(len(result["contracts"]), num_contracts)

    def test_route_contract_search_partner_pagination(self, *args):
        num_contracts = self.env["contract.contract"].search_count(
            [("partner_id", "=", self.partner.id)]
        )
        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "limit", 1
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertIn("contracts", result)
        self.assertEqual(len(result["contracts"]), 1)
        self.assertIn("paging", result)
        self.assertIn("limit", result["paging"])
        self.assertEqual(result["paging"]["limit"], 1)
        self.assertIn("offset", result["paging"])
        self.assertEqual(result["paging"]["offset"], 0)
        self.assertIn("totalNumberOfRecords", result["paging"])
        self.assertEqual(result["paging"]["totalNumberOfRecords"], num_contracts)

    def test_route_contract_search_partner_pagination_with_offset(self, *args):
        num_contracts = self.env["contract.contract"].search_count(
            [("partner_id", "=", self.partner.id)]
        )
        url = "{}?{}={}&{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "limit", 1, "offset", 1
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertIn("contracts", result)
        self.assertEqual(len(result["contracts"]), 1)
        self.assertIn("paging", result)
        self.assertIn("offset", result["paging"])
        self.assertEqual(result["paging"]["offset"], 1)
        self.assertIn("limit", result["paging"])
        self.assertEqual(result["paging"]["limit"], 1)
        self.assertIn("totalNumberOfRecords", result["paging"])
        self.assertEqual(result["paging"]["totalNumberOfRecords"], num_contracts)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_pagination_bad_limit(self, *args):
        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "limit", "XXX"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "Limit must be numeric")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_pagination_bad_offset(self, *args):
        url = "{}?{}={}&{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "limit", "1", "offset", "XXX"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "Offset must be numeric")

    def test_route_contract_search_partner_sort_by(self, *args):
        expected_contracts_sorted = (
            self.env["contract.contract"]
            .search(
                [("partner_id", "=", self.partner.id)],
                limit=10,
                order="name",
            )
            .mapped("code")
        )

        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "sortBy", "name"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))

        codes = [c["code"] for c in result["contracts"]]
        self.assertEqual(codes, expected_contracts_sorted)
        self.assertIn("paging", result)
        self.assertIn("sortBy", result["paging"])
        self.assertEqual(result["paging"]["sortBy"], "name")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_bad_sort_by(self, *args):
        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "sortBy", "XXX"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "Invalid field to sortBy")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_sort_order(self, *args):
        expected_contracts_sorted = (
            self.env["contract.contract"]
            .search(
                [("partner_id", "=", self.partner.id)],
                limit=10,
                order="name desc",
            )
            .mapped("code")
        )

        url = "{}?{}={}&{}={}&{}={}".format(
            self.url,
            "partner_vat",
            self.partner.vat,
            "sortBy",
            "name",
            "sortOrder",
            "DESCENDENT",
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        codes = [c["code"] for c in result["contracts"]]
        self.assertEqual(codes, expected_contracts_sorted)
        self.assertIn("paging", result)
        self.assertIn("sortBy", result["paging"])
        self.assertEqual(result["paging"]["sortBy"], "name")
        self.assertIn("sortOrder", result["paging"])
        self.assertEqual(result["paging"]["sortOrder"], "DESCENDENT")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_bad_sort_order(self, *args):
        url = "{}?{}={}&{}={}&{}={}".format(
            self.url,
            "partner_vat",
            self.partner.vat,
            "sortBy",
            "name",
            "sortOrder",
            "XXX",
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "sortOrder must be ASCENDING or DESCENDING")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_pagination_offset_without_limit(self, *args):
        num_contracts = self.env["contract.contract"].search_count(
            [("partner_id", "=", self.partner.id)],
        )
        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "offset", "1"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertIn("contracts", result)
        self.assertEqual(len(result["contracts"]), 10)
        self.assertIn("paging", result)
        self.assertIn("offset", result["paging"])
        self.assertEqual(result["paging"]["offset"], 1)
        self.assertIn("totalNumberOfRecords", result["paging"])
        self.assertEqual(result["paging"]["totalNumberOfRecords"], num_contracts)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_contract_search_partner_pagination_sort_order_without_by(
        self, *args
    ):
        url = "{}?{}={}&{}={}".format(
            self.url, "partner_vat", self.partner.vat, "sortOrder", "DESCENDENT"
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")
