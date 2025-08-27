import json
import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.somconnexio.tests.helper_service import contract_fiber_create_data

from ...services.contract_iban_change_process import ContractIbanChangeProcess


class TestContractIBANChangeService(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp()
        self.Contract = self.env["contract.contract"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner_ref = self.partner.ref
        partner_id = self.partner.id
        self.bank_b = self.env["res.partner.bank"].create(
            {"acc_number": "ES1720852066623456789011", "partner_id": partner_id}
        )
        self.iban = "ES6700751951971875361545"
        self.bank_new = self.env["res.partner.bank"].create(
            {"acc_number": self.iban, "partner_id": partner_id}
        )
        self.env['account.banking.mandate'].create({
            'partner_bank_id': self.bank_new.id,
            'signature_date': datetime.date.today(),
        })
        self.banking_mandate = self.partner.bank_ids[0].mandate_ids[0]
        self.banking_mandate_new = self.env["account.banking.mandate"].search(
            [
                ("partner_bank_id", "=", self.bank_new.id),
            ]
        )
        vals_contract = contract_fiber_create_data(self.env, self.partner)
        self.contract = self.env["contract.contract"].create(vals_contract)
        vals_contract_same_partner = vals_contract.copy()
        vals_contract_same_partner.update(
            {
                "name": "Test Contract Broadband B",
                "code": "contract2test",
            }
        )
        self.contract_same_partner = (
            self.env["contract.contract"]
            .with_context(tracking_disable=True)
            .create(vals_contract_same_partner)
        )
        self.url = "/public-api/contract-iban-change"

    def test_route_right_run_wizard_all_contracts(self):
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEqual(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEqual(
            self.contract_same_partner.mandate_id, self.banking_mandate_new
        )

    def test_route_right_run_wizard_one_contract(self):
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{}".format(self.contract.code),
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEqual(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEqual(self.contract_same_partner.mandate_id, self.banking_mandate)

    def test_route_right_run_wizard_many_contracts(self):
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{};{}".format(
                self.contract.code, self.contract_same_partner.code
            ),
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEqual(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEqual(
            self.contract_same_partner.mandate_id, self.banking_mandate_new
        )

    def test_route_right_new_iban_existing_bank(self):
        missing_iban = "ES9121000418450200051332"
        data = {
            "partner_id": self.partner_ref,
            "iban": missing_iban,
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        acc_number = self.contract.mandate_id.partner_bank_id.acc_number
        self.assertEqual(acc_number.replace(" ", "").upper(), missing_iban)
        acc_number = self.contract_same_partner.mandate_id.partner_bank_id.acc_number
        self.assertEqual(acc_number.replace(" ", "").upper(), missing_iban)

    def test_route_right_new_iban_inexisting_bank(self):
        missing_bank_iban = "LB913533I8Z6LY1FA76J5FYR3V5L"
        data = {
            "partner_id": self.partner_ref,
            "iban": missing_bank_iban,
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaisesRegex(
            ValidationError, "Invalid bank", process.run_from_api, **data
        )

    def test_route_bad_iban(self):
        data = {
            "partner_id": self.partner_ref,
            "iban": "XXX",
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})

        with self.assertRaises(ValidationError):
            process = ContractIbanChangeProcess(self.env)
            process.run_from_api(**data)

    def test_route_bad_bank_inactive(self):
        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": False})
        data = {
            "partner_id": self.partner_ref,
            "iban": "ES6621000418401234567891",
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaisesRegex(
            ValidationError, "Invalid bank", process.run_from_api, **data
        )

    def test_route_bad_contract(self):
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{};XXX".format(self.contract),
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_missing_iban(self):
        data = {
            "partner_id": self.partner_ref,
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_missing_partner_id(self):
        data = {
            "iban": self.iban,
        }
        response = self.http_public_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)


class TestContractIBANChangeServiceJob(BaseRestCaseAdmin):
    def test_route_enqueue_job_change_iban(self):
        jobs_domain = [
            ("method_name", "=", "run_from_api"),
            ("model_name", "=", "contract.iban.change.wizard"),
        ]
        queued_jobs_before = self.env["queue.job"].search(jobs_domain)
        self.assertFalse(queued_jobs_before)

        url = "/public-api/contract-iban-change"
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        data = {
            "partner_id": partner.ref,
            "iban": "ES1720852066623456789011",
        }
        response = self.http_public_post(url, data=data)

        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})

        queued_jobs_after = self.env["queue.job"].search(jobs_domain)
        self.assertEqual(len(queued_jobs_after), 1)
