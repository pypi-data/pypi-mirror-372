from datetime import datetime, timedelta
from mock import Mock, patch, ANY

from .base_test_contract_process import BaseContractProcessTestCase


class TestFiberContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.FiberContractProcess = self.env["fiber.contract.process"]
        self.data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra100Mb").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
            "mandate": self.mandate,
        }
        mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades17GB")
        mobile_contract_service_info = self.env["mobile.service.contract.info"].create(
            {"phone_number": "654321123", "icc": "123"}
        )
        contract_line = {
            "name": mobile_product.showed_name,
            "product_id": mobile_product.id,
            "date_start": "2020-01-01 00:00:00",
        }
        self.vals_mobile_contract = {
            "name": "New Contract Mobile",
            "partner_id": self.partner.id,
            "invoice_partner_id": self.partner.id,
            "service_technology_id": self.ref("somconnexio.service_technology_mobile"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_masmovil"),
            "mobile_contract_service_info_id": (mobile_contract_service_info.id),
            "contract_line_ids": [(0, 0, contract_line)],
            "mandate_id": self.mandate.id,
        }
        self.mbl_contract_linked_email_template = self.browse_ref(
            "somconnexio.mobile_linked_with_fiber_email_template"
        )
        self.mbl_contract_to_link_email_template = self.browse_ref(
            "somconnexio.mobile_to_link_with_fiber_email_template"
        )
        self.mobile_pack_product = self.browse_ref(
            "somconnexio.TrucadesIllimitades30GBPack"
        )

    def test_create_fiber(self, *args):
        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            self.data["vodafone_fiber_contract_service_info"]["phone_number"],
        )

    def test_create_fiber_asociatel(self, *args):
        self.data.update(
            {
                "service_supplier": "Asociatel VDF",
            }
        )
        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            self.data["vodafone_fiber_contract_service_info"]["phone_number"],
        )

    def test_create_fiber_wo_vodafone_offer_code(self, *args):
        self.data["vodafone_fiber_contract_service_info"]["vodafone_offer_code"] = ""

        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertTrue(contract)

    def test_create_fiber_xoln(self, *args):
        data_xoln = self.data.copy()
        del data_xoln["vodafone_fiber_contract_service_info"]
        data_xoln["service_supplier"] = "XOLN"
        data_xoln["xoln_fiber_contract_service_info"] = {
            "phone_number": "962911963",
            "external_id": "123",
            "id_order": "1",
            "project": self.browse_ref("somconnexio.xoln_project_borda").code,
            "router_product_id": self.browse_ref("somconnexio.Fibra100Mb").default_code,
            "router_serial_number": "XXX",
        }
        content = self.FiberContractProcess.create(**data_xoln)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            data_xoln["xoln_fiber_contract_service_info"]["phone_number"],
        )

    def test_create_fiber_relate_with_mobile_pack(self, *args):
        # Crear un Contrato de mobil
        contract_product = self.env.ref("somconnexio.TrucadesIllimitades20GBPack")
        mobile_contract_service_info = self.env["mobile.service.contract.info"].create(
            {"phone_number": "654987654", "icc": "123"}
        )
        contract_line = {
            "name": contract_product.name,
            "product_id": contract_product.id,
            "date_start": datetime.now() - timedelta(days=12),
        }
        vals_contract = {
            "name": "Test Contract Mobile",
            "code": "12345",
            "partner_id": self.partner.id,
            "invoice_partner_id": self.partner.id,
            "service_technology_id": self.ref("somconnexio.service_technology_mobile"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_masmovil"),
            "mobile_contract_service_info_id": mobile_contract_service_info.id,
            "contract_line_ids": [(0, 0, contract_line)],
            "email_ids": [(6, 0, [self.partner.id])],
        }
        mobile_contract = self.env["contract.contract"].create(vals_contract)

        # Añadir al data el contrato vinculado
        data = self.data.copy()
        data["mobile_pack_contracts"] = mobile_contract.code

        content = self.FiberContractProcess.create(**data)
        contract = self.env["contract.contract"].browse(content["id"])

        # Revisar que el contrato de fibra tiene como childs al contrato de mobil
        self.assertEqual(
            mobile_contract,
            contract.children_pack_contract_ids,
        )

    def test_relate_with_mobile_pack_change_address(self, *args):
        """
        Check that with change address process, mobile products are
        linked to new fiber contract
        """

        mbl_contract_1 = self.env["contract.contract"].create(self.vals_mobile_contract)
        mbl_contract_2 = self.env["contract.contract"].create(self.vals_mobile_contract)

        self.assertFalse(mbl_contract_1.parent_pack_contract_id)
        self.assertFalse(mbl_contract_2.parent_pack_contract_id)

        self.data["mobile_pack_contracts"] = "{},{}".format(
            mbl_contract_1.code, mbl_contract_2.code
        )

        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])

        self.assertEqual(mbl_contract_1.parent_pack_contract_id, contract)
        self.assertEqual(mbl_contract_2.parent_pack_contract_id, contract)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._change_related_mobile_contract_tariff"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.with_context")
    def test_relate_with_one_existing_mobile_contract(
        self, mock_with_context, mock_change_related_mobile_contract_tariff, *args
    ):
        """
        Check if a fiber is created with an existing unpacked mobile
        contract with an appropiate tariff to become pack, a mail is sent
        """
        mock_template_with_context = Mock()
        mock_with_context.return_value = mock_template_with_context

        # Create packable mobile contract
        mbl_contract = self.env["contract.contract"].create(self.vals_mobile_contract)
        self.FiberContractProcess.create(**self.data)

        pricelist = (
            self.env["product.pricelist"].sudo().search([("code", "=", "21IVA")])
        )
        context_call = mock_with_context.call_args[0][0]
        self.assertEqual(
            context_call.get("mobile_price"),
            pricelist._get_product_price(self.mobile_pack_product, 1),
        )
        product_MB = self.mobile_pack_product.get_catalog_name("Data")
        self.assertEqual(
            context_call.get("mobile_data"),
            int(product_MB) // 1024,
        )
        mock_change_related_mobile_contract_tariff.assert_called_once_with(
            mbl_contract.id,
            ANY,
        )
        mock_template_with_context.sudo.return_value.send_mail.assert_called_with(
            mbl_contract.id,
        )  # TODO: how to check from which mail template is called?

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._change_related_mobile_contract_tariff"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.with_context")
    def test_relate_with_more_than_one_existing_mobile_contract(
        self, mock_with_context, mock_change_related_mobile_contract_tariff, *args
    ):
        """
        Check if a fiber is created with more than one unpacked mobile
        contract with an appropiate tariff to become pack, another
        mail is send
        """

        mock_template_with_context = Mock()
        mock_with_context.return_value = mock_template_with_context

        # Create 2 packable mobile contract
        self.env["contract.contract"].create(self.vals_mobile_contract)
        self.env["contract.contract"].create(self.vals_mobile_contract)

        self.FiberContractProcess.create(**self.data)

        pricelist = (
            self.env["product.pricelist"].sudo().search([("code", "=", "21IVA")])
        )
        context_call = mock_with_context.call_args[0][0]
        self.assertEqual(
            context_call.get("mobile_price"),
            pricelist._get_product_price(self.mobile_pack_product, 1),
        )
        product_MB = self.mobile_pack_product.get_catalog_name("Data")
        self.assertEqual(
            context_call.get("mobile_data"),
            int(product_MB) // 1024,
        )

        mock_change_related_mobile_contract_tariff.assert_not_called()
        mock_template_with_context.sudo.return_value.send_mail.assert_called_with(
            self.partner.id,
        )  # TODO: how to check from which mail template is called?

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._change_related_mobile_contract_tariff"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_relate_with_one_non_packable_mobile_contract(
        self, mock_send_email, mock_change_related_mobile_contract_tariff, *args
    ):
        """
        Check if a fiber is created without any mobile
        contract with an appropiate tariff to become pack,
        no change is done
        """

        non_pack_mbl_product = self.browse_ref("somconnexio.150Min1GB")
        contract = self.env["contract.contract"].create(self.vals_mobile_contract)
        contract.contract_line_ids[0].product_id = non_pack_mbl_product.id

        self.FiberContractProcess.create(**self.data)

        mock_send_email.assert_not_called()
        mock_change_related_mobile_contract_tariff.assert_not_called()
