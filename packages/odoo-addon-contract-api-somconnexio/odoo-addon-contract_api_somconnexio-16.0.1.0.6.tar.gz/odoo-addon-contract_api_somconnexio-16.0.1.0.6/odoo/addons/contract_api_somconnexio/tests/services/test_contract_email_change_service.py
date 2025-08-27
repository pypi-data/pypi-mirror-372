from mock import patch
import json
from datetime import date
from odoo.exceptions import UserError
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.somconnexio.tests.helper_service import contract_fiber_create_data

from ...services.contract_email_change_process import ContractEmailChangeProcess


class TestContractEmailChangeService(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp()
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner.ref = "1234test"
        self.partner_ref = self.partner.ref
        self.email = "test@example.org"
        self.ResPartner = self.env["res.partner"]
        self.partner_email_b = self.ResPartner.create(
            {
                "name": "Email b",
                "email": self.email,
                "type": "contract-email",
                "parent_id": self.partner.id,
            }
        )
        vals_contract = contract_fiber_create_data(self.env, self.partner)
        self.Contract = self.env["contract.contract"]
        self.contract = self.Contract.create(vals_contract)
        vals_contract_same_partner = vals_contract.copy()
        vals_contract_same_partner.update(
            {"name": "Test Contract Broadband B", "code": "1234b"}
        )
        self.contract_same_partner = self.Contract.create(vals_contract_same_partner)
        self.user_admin = self.browse_ref("base.user_admin")
        self.expected_activity_args = {
            "res_model_id": self.env.ref("contract.model_contract_contract").id,
            "user_id": 1,
            "activity_type_id": self.env.ref(
                "somconnexio.mail_activity_type_contract_data_change"
            ).id,
            "date_done": date.today(),
            "date_deadline": date.today(),
            "summary": "Email change",
            "done": True,
        }

    @patch(
        "odoo.addons.contract_group_somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_route_right_run_wizard_contract_emails_change(
        self, mock_change_contracts_emails
    ):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "contracts": {},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        process.run_from_api(**data)
        mock_change_contracts_emails.assert_called_once_with(
            self.partner,
            self.Contract.search([("partner_id", "=", self.partner.id)]),
            self.ResPartner.browse(self.partner_email_b.id),
            self.expected_activity_args,
            contract_group_id=self.env["contract.group"],
            create_contract_group=True,
        )

    @patch(
        "odoo.addons.contract_group_somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_route_right_run_wizard_one_contract_emails_change(
        self, mock_change_contracts_emails
    ):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "contracts": self.contract.code,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        process.run_from_api(**data)
        mock_change_contracts_emails.assert_called_once_with(
            self.partner,
            self.Contract.browse(self.contract.id),
            self.ResPartner.browse(self.partner_email_b.id),
            self.expected_activity_args,
            contract_group_id=self.env["contract.group"],
            create_contract_group=True,
        )

    @patch(
        "odoo.addons.contract_group_somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_route_right_run_wizard_many_contracts_emails_change(
        self, mock_change_contracts_emails
    ):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "contracts": "{};{}".format(
                self.contract.code, self.contract_same_partner.code
            ),
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        process.run_from_api(**data)
        mock_change_contracts_emails.assert_called_once_with(  # noqa
            self.partner,
            self.Contract.browse([self.contract.id, self.contract_same_partner.id]),
            self.ResPartner.browse(self.partner_email_b.id),
            self.expected_activity_args,
            contract_group_id=self.env["contract.group"],
            create_contract_group=True,
        )

    def test_route_bad_run_wizard_contract_code_not_found(self):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "contracts": "XXX",
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_create_email_partner(self):
        email = "test123@example.org"
        process = ContractEmailChangeProcess(self.env)
        partner = process._create_email_partner(self.partner, email)
        self.assertEqual(partner.parent_id, self.partner)
        self.assertEqual(partner.email, email)
        self.assertEqual(partner.type, "contract-email")

    @patch(
        "odoo.addons.contract_group_somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_route_right_run_wizard_email_not_found(self, mock_change_contracts_emails):
        email = "test123@example.org"
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": email,
            "contracts": {},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        process.run_from_api(**data)
        new_email = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner.id),
                ("email", "=", email),
                ("type", "=", "contract-email"),
            ]
        )
        mock_change_contracts_emails.assert_called_once_with(  # noqa
            self.partner,
            self.Contract.search([("partner_id", "=", self.partner.id)]),
            new_email,
            self.expected_activity_args,
            contract_group_id=self.env["contract.group"],
            create_contract_group=True,
        )

    def test_route_bad_run_wizard_missing_partner_id(self):
        url = "/public-api/contract-email-change"
        data = {
            "email": self.email,
            "contracts": {},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_run_wizard_missing_email(self):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "contracts": {},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_run_wizard_partner_id_not_found(self):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": "XXX",
            "email": self.email,
            "contracts": {},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_run_wizard_contracts_missing(self):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_run_wizard_contracts_dict(self):
        url = "/public-api/contract-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "contracts": {"a": "b"},
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractEmailChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)
