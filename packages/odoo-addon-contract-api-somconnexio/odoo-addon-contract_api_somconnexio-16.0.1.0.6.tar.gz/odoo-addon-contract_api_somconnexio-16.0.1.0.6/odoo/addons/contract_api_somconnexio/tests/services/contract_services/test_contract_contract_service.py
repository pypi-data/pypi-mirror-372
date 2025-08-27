import json
import odoo
from datetime import date, timedelta

from faker import Faker
from odoo.exceptions import UserError
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from ....services.contract_contract_process import (
    ErrorUnsuportedTechnology,
)


class TestContractController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.router_product = self.env["product.product"].search(
            [
                ("default_code", "=", "HG8245Q2"),
            ]
        )
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner_ref = partner.ref
        self.iban = partner.bank_ids[0].acc_number
        self.email = partner.email
        fake = Faker("es-ES")
        self.mandate = self.browse_ref("somconnexio.demo_mandate_partner_2_demo")
        self.service_address = {
            "street": fake.street_address() + " " + fake.secondary_address(),
            "zip_code": fake.postcode(),
            "city": fake.city(),
            "state": self.browse_ref("base.state_es_m").code,
            "country": self.browse_ref("base.es").code,
        }
        self.ContractContractProcess = self.env["contract.contract.process"]

    def test_route_right_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["mobile_contract_service_info"]["phone_number"]
        )
        self.assertEqual(
            contract.partner_id, self.browse_ref("somconnexio.res_partner_2_demo")
        )
        self.assertEqual(
            contract.journal_id,
            self.browse_ref("somconnexio.consumption_invoices_journal"),
        )
        self.assertEqual(
            contract.invoice_partner_id,
            self.browse_ref("somconnexio.res_partner_2_demo"),
        )
        self.assertEqual(
            contract.service_technology_id,
            self.browse_ref("somconnexio.service_technology_mobile"),
        )
        self.assertEqual(
            contract.service_supplier_id,
            self.browse_ref("somconnexio.service_supplier_masmovil"),
        )
        self.assertTrue(contract.mobile_contract_service_info_id)
        self.assertEqual(
            contract.mobile_contract_service_info_id.icc,
            data["mobile_contract_service_info"]["icc"],
        )
        self.assertEqual(
            contract.mobile_contract_service_info_id.phone_number,
            data["mobile_contract_service_info"]["phone_number"],
        )
        self.assertEqual(contract.mandate_id, self.mandate)

    def test_route_bad_partner_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": "666",
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": "IBAN",
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_bad_tech_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "XXXX",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(
            ErrorUnsuportedTechnology, self.ContractContractProcess.create, **data
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_supplier_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "XXXX",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_fiber_signal_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Fiber",
            "service_supplier": "MásMóvil",
            "mm_fiber_contract_service_info": {
                "phone_number": "654123456",
                "mm_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_combination_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Fiber",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_right_contract_lines(self, *args):
        yesterday = date.today() + timedelta(days=-1)
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": yesterday.strftime("%Y-%m-%d %H:%M:%S"),
                },
                {
                    "product_code": (
                        self.browse_ref("somconnexio.EnviamentSIM").default_code
                    ),
                    "date_start": yesterday.strftime("%Y-%m-%d %H:%M:%S"),
                },
            ],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["mobile_contract_service_info"]["phone_number"]
        )
        self.assertEqual(
            contract.partner_id, self.browse_ref("somconnexio.res_partner_2_demo")
        )
        self.assertEqual(
            contract.invoice_partner_id,
            self.browse_ref("somconnexio.res_partner_2_demo"),
        )
        self.assertEqual(
            contract.service_technology_id,
            self.browse_ref("somconnexio.service_technology_mobile"),
        )
        self.assertEqual(
            contract.service_supplier_id,
            self.browse_ref("somconnexio.service_supplier_masmovil"),
        )
        self.assertIn(
            self.browse_ref("somconnexio.150Min1GB"),
            [c.product_id for c in contract.contract_line_ids],
        )
        self.assertIn(
            self.browse_ref("somconnexio.EnviamentSIM"),
            [c.product_id for c in contract.contract_line_ids],
        )
        self.assertEqual(
            [yesterday, yesterday],
            contract.contract_line_ids.mapped("date_start"),
        )
        self.assertEqual(
            contract.tariff_contract_line.product_id,
            self.env.ref("somconnexio.150Min1GB")
        )
        self.assertEqual(contract.date_start, yesterday)

    def test_route_right_contract_line(self, *args):
        tomorrow = date.today() + timedelta(days=1)
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": tomorrow.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertIn(
            self.browse_ref("somconnexio.150Min1GB"),
            [c.product_id for c in contract.contract_line_ids],
        )
        self.assertEqual(
            [tomorrow],
            contract.contract_line_ids.mapped("date_start"),
        )

    def test_route_contract_without_active_tariff(self, *args):
        url = "/public-api/contract"
        tomorrow = date.today() + timedelta(days=1)
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": tomorrow.strftime("%Y-%m-%d %H:%M:%S"),
                },
                {
                    "product_code": (
                        self.browse_ref("somconnexio.EnviamentSIM").default_code
                    ),
                    "date_start": tomorrow.strftime("%Y-%m-%d %H:%M:%S"),
                },
            ],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertFalse(contract.current_tariff_contract_line)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_call_both_contract_lines(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_line": {},
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_date_start(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": "6666-66-66 66:66:66",
                }
            ],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                },
                {"product_code": "SC_0", "date_start": "2020-01-01 00:00:00"},
            ],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_format_product(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.150Min1GB").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                },
                {"product_code": 666, "date_start": "2020-01-01 00:00:00"},
            ],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_icc(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_phone_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_right_adsl(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["adsl_contract_service_info"]["phone_number"]
        )

        self.assertTrue(contract.adsl_service_contract_info_id)
        contract_service_info = contract.adsl_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "654123456")
        self.assertEqual(contract_service_info.administrative_number, "123")
        self.assertEqual(
            contract_service_info.router_lot_id.product_id.id, self.router_product.id
        )
        self.assertEqual(contract_service_info.router_lot_id.name, "4637")
        # self.assertEqual(
        #     contract_service_info.router_lot_id.router_mac_address,
        #     "AA:BB:CC:22:33:11"
        # )
        self.assertEqual(contract_service_info.ppp_user, "ringo")
        self.assertEqual(contract_service_info.ppp_password, "rango")
        self.assertEqual(contract_service_info.endpoint_user, "connection")
        self.assertEqual(contract_service_info.endpoint_password, "password")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:XX",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_hyphen_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "-",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_empty_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_missing_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": 0,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:44",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_not_found_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": "XXX",
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:44",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_right_vodafone_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["vodafone_fiber_contract_service_info"]["phone_number"]
        )
        self.assertTrue(contract.vodafone_fiber_service_contract_info_id)
        contract_service_info = contract.vodafone_fiber_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "654123456")
        self.assertEqual(contract_service_info.vodafone_id, "123")
        self.assertEqual(contract_service_info.vodafone_offer_code, "offer")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )
        self.assertEqual(contract.fiber_signal_type_id.code, "NEBAFTTH")

    def test_route_right_mm_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "MásMóvil",
            "mm_fiber_contract_service_info": {
                "phone_number": "654123456",
                "mm_id": "123",
            },
            "fiber_signal_type": "fibraIndirecta",
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["mm_fiber_contract_service_info"]["phone_number"]
        )
        self.assertTrue(contract.mm_fiber_service_contract_info_id)
        contract_service_info = contract.mm_fiber_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "654123456")
        self.assertEqual(contract_service_info.mm_id, "123")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )
        self.assertEqual(contract.fiber_signal_type_id.code, "fibraIndirecta")

    def test_route_right_orange_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Orange",
            "orange_fiber_contract_service_info": {"suma_id": "123"},
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(contract.name, "-")
        self.assertTrue(contract.orange_fiber_service_contract_info_id)
        contract_service_info = contract.orange_fiber_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "-")
        self.assertEqual(contract_service_info.suma_id, "123")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )

    def test_route_wrong_orange_fiber_without_service_info(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Orange",
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_right_xoln_fiber_la_borda(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["xoln_fiber_contract_service_info"]["phone_number"]
        )
        self.assertTrue(contract.xoln_fiber_service_contract_info_id)
        contract_service_info = contract.xoln_fiber_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "654123456")
        self.assertEqual(contract_service_info.external_id, "123")
        self.assertEqual(contract_service_info.id_order, "456")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )
        self.assertEqual(
            contract_service_info.router_lot_id.product_id.id, self.router_product.id
        )
        self.assertEqual(contract_service_info.router_lot_id.name, "4637")
        # self.assertEqual(
        #     contract_service_info.router_lot_id.router_mac_address,
        #     "AA:BB:CC:22:33:11"
        # )

    def test_route_right_xoln_fiber_xarxa_greta(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_greta").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "fiber_signal_type": "",
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name, data["xoln_fiber_contract_service_info"]["phone_number"]
        )
        self.assertTrue(contract.xoln_fiber_service_contract_info_id)
        contract_service_info = contract.xoln_fiber_service_contract_info_id
        self.assertEqual(contract_service_info.phone_number, "654123456")
        self.assertEqual(contract_service_info.external_id, "123")
        self.assertEqual(contract_service_info.id_order, "456")
        self.assertEqual(
            contract_service_info.router_lot_id.product_id.id, self.router_product.id
        )
        self.assertEqual(contract_service_info.router_lot_id.name, "4637")
        # self.assertEqual(
        #     contract_service_info.router_lot_id.router_mac_address,
        #     "AA:BB:CC:22:33:11"
        # )
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )
        self.assertFalse(contract.fiber_signal_type_id)

    def test_route_right_vodafone_4G(self, *args):
        router_product_code = "ADOC_R45"
        router_product = self.env["product.product"].search(
            [("default_code", "=", router_product_code)]
        )
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "4G",
            "service_supplier": "Vodafone",
            "router_4G_contract_service_info": {
                "phone_number": "-",
                "vodafone_id": "34564",
                "vodafone_offer_code": "2882582",
                "previous_id": "0004",
                "router_product_id": router_product_code,
                "icc": "82828",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(contract.name, "-")
        self.assertEqual(
            contract.service_partner_id.street, self.service_address["street"]
        )
        self.assertEqual(
            contract.service_partner_id.zip, self.service_address["zip_code"]
        )
        self.assertEqual(
            contract.service_partner_id.city, self.service_address["city"]
        )
        self.assertEqual(
            contract.service_partner_id.state_id.code, self.service_address["state"]
        )
        contract_service_info = contract.router_4G_service_contract_info_id
        self.assertTrue(contract_service_info)
        self.assertEqual(contract_service_info.phone_number, "-")
        self.assertEqual(contract_service_info.vodafone_id, "34564")
        self.assertEqual(contract_service_info.vodafone_offer_code, "2882582")
        self.assertEqual(contract_service_info.router_product_id, router_product)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_missing_service_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.ref("base.res_partner_12"),
            "email": self.email,
            "service_technology": "ADSL",
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                "administrative_number": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "connection",
                "endpoint_password": "password",
            },
            "contract_lines": [],
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    def test_route_right_create_with_code(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(contract.code, "1234")

    def test_route_right_create_without_code(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        contract_code = self.browse_ref(
            "somconnexio.sequence_contract"
        ).number_next_actual
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(contract.code, str(contract_code))

    def test_route_right_create_with_new_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": "new_email@test.coop",
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(len(contract.email_ids), 1)
        self.assertEqual(contract.email_ids[0].email, "new_email@test.coop")
        self.assertEqual(
            contract.email_ids[0].parent_id.id,
            self.browse_ref("somconnexio.res_partner_2_demo").id,
        )

    def test_route_right_empty_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": "",
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(contract.email_ids[0].email, self.email)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_missing_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_missing_mandate(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": "ES6920854617166897440377",
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_id_order(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_external_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_phone_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_project(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_not_valid_project(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                "id_order": "456",
                "project": "XXX",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "phone_number": "654123456",
                "router_serial_number": "4637",
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_router_serial_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "phone_number": "654123456",
                "router_product_id": self.router_product.default_code,
                "router_mac_address": "AA:BB:CC:22:33:11",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        self.assertRaises(UserError, self.ContractContractProcess.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "phone_number": "654123456",
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    def test_route_right_xoln_empty_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    def test_route_right_xoln_hyphen_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "-",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})
        content = self.ContractContractProcess.create(**data)
        self.assertIn("id", content)
        self.assertTrue(content["id"])

    def test_route_right_fiber_with_related_mobile_contracts(self, *args):
        mobile_data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": "Mobile",
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }

        content = self.ContractContractProcess.create(**mobile_data)
        mobile_contract = self.env["contract.contract"].browse(content["id"])

        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                "id_order": "456",
                "project": self.browse_ref("somconnexio.xoln_project_borda").code,
                "router_product_id": self.router_product.default_code,
                "router_serial_number": "4637",
                "router_mac_address": "-",
            },
            "contract_lines": [],
            "iban": self.iban,
            "mobile_pack_contracts": mobile_contract.code,
        }
        response = self.http_public_post(url, data=data)
        self.assertEqual(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(decoded_response, {"result": "OK"})

        content = self.ContractContractProcess.create(**data)
        fiber_contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(fiber_contract.children_pack_contract_ids, mobile_contract)
