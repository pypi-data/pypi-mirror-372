from datetime import datetime, timedelta
import json
import odoo

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.somconnexio.helpers.date import date_to_str


class TestContractTerminateController(BaseRestCaseAdmin):
    def setUp(self):
        super(TestContractTerminateController, self).setUp()
        self.url = "/api/contract/terminate"
        group_can_terminate_contract = self.env.ref("contract.can_terminate_contract")
        group_can_terminate_contract.users |= self.env.user

    def test_terminate_contract_success(self, *args):
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")

        future_end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        terminate_data = {
            "code": self.contract.code,
            "terminate_reason": "TR001",
            "terminate_comment": "Termination comment",
            "terminate_date": future_end_date,
            "terminate_user_reason": "TUR003",
        }

        response = self.http_post(self.url, data=terminate_data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(decoded_response, {"result": "OK"})
        self.contract.invalidate_recordset()
        self.assertTrue(self.contract.is_terminated)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_terminate_contract_not_found(self, *args):
        code = "invented"
        terminate_data = {
            "code": code,
            "terminate_reason": "TR001",
            "terminate_comment": "Termination comment",
            "terminate_date": "2023-09-18",
            "terminate_user_reason": "TUR003",
        }

        response = self.http_post(self.url, data=terminate_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_terminate_terminate_reason_not_found(self, *args):
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        terminate_data = {
            "code": self.contract.code,
            "terminate_reason": "NonExistentReason",
            "terminate_comment": "Termination comment",
            "terminate_date": "2023-09-18",
            "terminate_user_reason": "TUR003",
        }

        response = self.http_post(self.url, data=terminate_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_terminate_terminate_user_reason_not_found(self, *args):
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        terminate_data = {
            "code": self.contract.code,
            "terminate_reason": "TR001",
            "terminate_comment": "Termination comment",
            "terminate_date": "2023-09-18",
            "terminate_user_reason": "NonExistentUserReason",
        }

        response = self.http_post(self.url, data=terminate_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_terminate_terminate_before_date_start(self, *args):
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        terminate_date = self.contract.date_start - timedelta(days=2)
        terminate_data = {
            "code": self.contract.code,
            "terminate_reason": "TR001",
            "terminate_comment": "Termination comment",
            "terminate_date": date_to_str(terminate_date),
            "terminate_user_reason": "TUR003",
        }

        response = self.http_post(self.url, data=terminate_data)

        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "<p>A contract can&#x27;t be terminated before it started</p>"
        )
