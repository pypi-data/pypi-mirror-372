import json
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.somconnexio.tests.helper_service import contract_fiber_create_data


class TestContractCountController(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]
        self.Partner = self.env["res.partner"]
        self.url = "/public-api/contract-count"
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.vals_contract = contract_fiber_create_data(self.env, partner)

    def test_route_count_one_contract_active(self, *args):
        count_contract = self.env["contract.contract"].search_count([])
        self.Contract.create(self.vals_contract)
        response = self.http_get(self.url)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"contracts": count_contract + 1})

    def test_route_doesnt_count_one_contract_terminated(self, *args):
        count_contract = self.env["contract.contract"].search_count([])
        self.vals_contract["is_terminated"] = True
        self.Contract.create(self.vals_contract)
        response = self.http_get(self.url)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"contracts": count_contract})
