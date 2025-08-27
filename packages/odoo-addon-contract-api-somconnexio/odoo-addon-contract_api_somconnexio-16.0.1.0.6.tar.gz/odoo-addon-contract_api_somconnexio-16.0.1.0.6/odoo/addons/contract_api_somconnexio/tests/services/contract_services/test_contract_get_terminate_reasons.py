import json

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin


class TestContractTerminateReasonsController(BaseRestCaseAdmin):
    def setUp(self):
        super(TestContractTerminateReasonsController, self).setUp()
        self.url = "/api/contract/terminate_reasons"

    def test_get_terminate_reasons(self):
        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertIn("terminate_reasons", content)
        self.assertIn("terminate_user_reasons", content)
