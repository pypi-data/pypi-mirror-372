from odoo.exceptions import UserError

from .ba import BAContractProcess


class FiberContractProcess(BAContractProcess):
    _name = "fiber.contract.process"
    _inherit = "ba.contract.process"
    _description = """
        Fiber Contract creation
    """

    @staticmethod
    def validate_service_technology_deps(params):
        errors = []
        if "service_address" not in params:
            errors.append('Fiber needs "service_address"')
        fiber_suppliers = [
            "Asociatel VDF",
            "Vodafone",
            "Orange",
            "MásMóvil",
            "XOLN",
        ]
        if params["service_supplier"] not in fiber_suppliers:
            errors.append("Fiber needs {} suppliers".format(", ".join(fiber_suppliers)))
        else:
            if params["service_supplier"] in ["Asociatel VDF", "Vodafone"]:
                if "vodafone_fiber_contract_service_info" not in params:
                    errors.append(
                        "Vodafone Fiber needs vodafone_fiber_contract_service_info"
                    )
                if params.get("fiber_signal_type") == "fibraIndirecta":
                    errors.append(
                        'Fiber signal "Fibra Indirecta" needs MásMóvil supplier'
                    )
            elif params["service_supplier"] == "MásMóvil":
                if "mm_fiber_contract_service_info" not in params:
                    errors.append("MásMóvil Fiber needs mm_fiber_contract_service_info")
                if params.get("fiber_signal_type") in ("fibraCoaxial", "NEBAFTTH"):
                    errors.append(
                        'Fiber signal "{}" needs Vodafone supplier'.format(
                            params["fiber_signal_type"]
                        )
                    )
            elif params["service_supplier"] == "XOLN":
                if "xoln_fiber_contract_service_info" not in params:
                    errors.append("XOLN Fiber needs mm_fiber_contract_service_info")
            elif params["service_supplier"] == "Orange":
                if "orange_fiber_contract_service_info" not in params:
                    errors.append(
                        "Orange Fiber needs orange_fiber_contract_service_info"
                    )
        if errors:
            raise UserError("\n".join(errors))

    def _create_vodafone_fiber_contract_service_info(self, params):
        if not params:
            return False
        return (
            self.env["vodafone.fiber.service.contract.info"]
            .sudo()
            .create(
                {
                    "phone_number": params["phone_number"],
                    "vodafone_id": params["vodafone_id"],
                    "vodafone_offer_code": params["vodafone_offer_code"],
                }
            )
        )

    def _create_mm_fiber_contract_service_info(self, params):
        if not params:
            return False
        return (
            self.env["mm.fiber.service.contract.info"]
            .sudo()
            .create(
                {
                    "phone_number": params["phone_number"],
                    "mm_id": params["mm_id"],
                }
            )
        )

    def _create_orange_fiber_contract_service_info(self, params):
        if not params:
            return False
        return (
            self.env["orange.fiber.service.contract.info"]
            .sudo()
            .create(
                {
                    "suma_id": params["suma_id"],
                }
            )
        )

    def _create_xoln_fiber_contract_service_info(self, params):
        if not params:
            return False
        router_product = self._get_router_product_id(params["router_product_id"])
        router_lot_id = self._create_router_lot_id(
            params["router_serial_number"],
            router_product,
        )
        project_id = self._get_project_xoln_id_by_code(params["project"])

        return (
            self.env["xoln.fiber.service.contract.info"]
            .sudo()
            .create(
                {
                    "phone_number": params["phone_number"],
                    "external_id": params["external_id"],
                    "id_order": params["id_order"],
                    "project_id": project_id,
                    "router_product_id": router_product.id,
                    "router_lot_id": router_lot_id.id,
                }
            )
        )

    def create(self, **params):
        contract_dict = super().create(**params)
        if params.get("mobile_pack_contracts"):
            self._relate_with_CU_former_mobile_contracts(
                contract_dict["id"], params.get("mobile_pack_contracts")
            )
        else:
            self._relate_new_fiber_with_existing_mobile_contracts(contract_dict)
        return contract_dict

    def _relate_with_CU_former_mobile_contracts(self, _id, mobile_pack_contracts):
        """
        When we create a contract from an address change petition (CU),
        we need to relate the mobile contracts linked with the
        former fiber contract with the new one
        """
        if mobile_pack_contracts:
            mobile_contracts = (
                self.env["contract.contract"]
                .sudo()
                .search([("code", "in", mobile_pack_contracts.split(","))])
            )
            for contract in mobile_contracts:
                contract.parent_pack_contract_id = _id

    def _get_related_crm_lead_line(self, contract_dict):
        # To be implemented in the OTRS module
        return self.env["crm.lead.line"]

    def _change_related_mobile_contract_tariff(self, mbl_contract_id, contract_dict):
        # To be implemented in the OTRS module
        pass

    def _relate_new_fiber_with_existing_mobile_contracts(self, contract_dict):
        """
        Link new fiber to an existing mobile contract, except:
          - New fiber contract comes from location_change
          - Within the fiber CRMLead there is a mobile with
            pack product (the fiber contract is needed to be
            packed with that mobile).
          - No existing mobile contract is found with appropiate
            mobile tariffs to be packed.
        """

        # Check that fiber contract does not come from a location change
        if contract_dict["create_reason"] == "location_change":
            return

        # Check if fiber CRMLead has mobile with pack product
        crm_lead_line = self._get_related_crm_lead_line(contract_dict)
        mobile_lines = crm_lead_line.lead_id.lead_line_ids.filtered(
            "is_mobile"
        ).filtered("is_from_pack")
        if mobile_lines:
            return

        # Check existing mobile contracts
        mobile_products_appropiate_to_pack = self._mobile_products_appropiate_to_pack()

        mobile_tech_id = self.env.ref("somconnexio.service_technology_mobile").id

        mobile_contracts = (
            self.env["contract.contract"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", contract_dict["partner_id"]),
                    ("service_technology_id", "=", mobile_tech_id),
                    ("date_end", "=", False),
                    ("parent_pack_contract_id", "=", False),
                    (
                        "current_tariff_product",
                        "in",
                        mobile_products_appropiate_to_pack,
                    ),
                ]
            )
        )

        if not mobile_contracts:
            return

        # pinya pack notification
        pack_mobile_product_id = self.env.ref("somconnexio.TrucadesIllimitades30GBPack")
        pack_mobile_product_price = self._product_price(pack_mobile_product_id)
        pack_mobile_product_data = pack_mobile_product_id.get_catalog_name("Data")
        product_ctx = {
            "mobile_price": pack_mobile_product_price,
            "mobile_data": int(pack_mobile_product_data) // 1024,  # To GB
        }

        if len(mobile_contracts) == 1:
            mbl_contract = mobile_contracts[0]

            # Change mobile tariff
            self._change_related_mobile_contract_tariff(mbl_contract.id, contract_dict)

            # Send mail
            template = self.env.ref(
                "somconnexio.mobile_linked_with_fiber_email_template"
            )
            template.with_context(product_ctx).sudo().send_mail(mbl_contract.id)

        else:
            # Send mail
            template = self.env.ref(
                "somconnexio.mobile_to_link_with_fiber_email_template"
            )
            template.with_context(product_ctx).sudo().send_mail(
                contract_dict["partner_id"]
            )

    def _mobile_products_appropiate_to_pack(self):
        """
        Return mobile products that have the same or less data
        (those without any data not included) than the pinya to be packed,
        but with a higher price
        """

        return [
            self.env.ref("somconnexio.TrucadesIllimitades30GB").id,
            self.env.ref("somconnexio.TrucadesIllimitades20GB").id,
            self.env.ref("somconnexio.TrucadesIllimitades17GB").id,
            self.env.ref("somconnexio.TrucadesIllimitades12GB").id,
            self.env.ref("somconnexio.TrucadesIllimitades5GB").id,
        ]

    def _product_price(self, product):
        pricelist = self.env["product.pricelist"].search([("code", "=", "21IVA")])
        return pricelist._get_product_price(product, 1)
