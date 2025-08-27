import odoo
from mock import patch
import json
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin


class TestContractGetFiberContractsNotPackedController(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.partner = self.fiber_contract.partner_id
        self.params = {"partner_ref": self.partner.ref}
        self.url = "/api/contract/available-fibers-to-link-with-mobile"

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    @patch("odoo.addons.contract_api_somconnexio.models.contract.Contract._to_dict")
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_ref_ok(self, mock_to_dict, mock_create):
        mock_create.return_value = self.fiber_contract
        mock_to_dict.return_value = {"id": self.fiber_contract.id}

        response = self.http_get(self.url, params=self.params)

        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.fiber_contract.id)
        mock_create.assert_called_with(**self.params)
        mock_to_dict.assert_called_with()

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_no_partner(self):
        fake_partner_ref = "234252"
        response = self.http_get(self.url, params={"partner_ref": fake_partner_ref})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_bad_request(self):
        response = self.http_get(self.url, params={"partner_nif": self.partner.ref})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")
