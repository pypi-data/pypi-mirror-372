from unittest.mock import patch
import json
from odoo.exceptions import UserError
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from ...services.contract_one_shot_process import ContractOneShotProcess


class TestContractOneShotService(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp()
        self.Contract = self.env["contract.contract"]

        self.phone = "654321123"
        self.mobile_one_shot = self.browse_ref("somconnexio.DadesAddicionals1GB")
        self.data = {
            "product_code": self.mobile_one_shot.default_code,
            "phone_number": self.phone,
        }

        self.mobile_contract_service_info = self.env[
            "mobile.service.contract.info"
        ].create({"phone_number": self.phone, "icc": "123"})
        self.partner = self.browse_ref("base.partner_demo")
        self.mobile_contract = self.Contract.create(
            {
                "name": "Test Contract Mobile",
                "partner_id": self.partner.id,
                "service_partner_id": self.partner.id,
                "invoice_partner_id": self.partner.id,
                "service_technology_id": self.ref(
                    "somconnexio.service_technology_mobile"
                ),
                "service_supplier_id": self.ref(
                    "somconnexio.service_supplier_masmovil"
                ),
                "mobile_contract_service_info_id": (
                    self.mobile_contract_service_info.id
                ),
            }
        )
        self.url = "/public-api/add-one-shot"

    @patch(
        "odoo.addons.somconnexio.wizards.contract_one_shot_request.contract_one_shot_request.ContractOneShotRequestWizard.add_one_shot_to_contract"  # noqa
    )
    def test_route_right_run_wizard(self, mock_add_one_shot_to_contract):
        response = self.http_public_post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        process.run_from_api(**self.data)

        mock_add_one_shot_to_contract.assert_called_once()

    def test_route_bad_phone(self):
        wrong_phone = "8383838"
        self.data.update({"phone_number": wrong_phone})

        response = self.http_public_post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        self.assertRaisesRegex(
            UserError,
            "Mobile contract not found with phone: {}".format(wrong_phone),
            process.run_from_api,
            **self.data
        )

    def test_route_bad_product(self):
        wrong_product = "FAKE_DEFAULT_CODE"
        self.data.update({"product_code": wrong_product})

        response = self.http_public_post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        self.assertRaisesRegex(
            UserError,
            "Mobile additional bond product not found with code: {}".format(
                wrong_product
            ),
            process.run_from_api,
            **self.data
        )
