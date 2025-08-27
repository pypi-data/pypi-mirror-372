from odoo.models import Model

from odoo.addons.somconnexio.helpers.address_service import AddressService


class Contract(Model):
    _inherit = "contract.contract"

    def create_contract(self, **params):
        self.env["contract.contract.process"].create(**params)

    def _to_dict(self):
        self.ensure_one()

        fiber_signal = (
            self.fiber_signal_type_id and self.fiber_signal_type_id.code or False
        )
        subscription_type_map = {
            "mobile": "mobile",
            "broadband": "broadband",
            "switchboard": "switchboard",
        }

        return {
            "id": self.id,
            "code": self.code,
            "email": self.partner_id.email or "",
            "customer_firstname": self.partner_id.firstname or "",
            "customer_lastname": self.partner_id.lastname or "",
            "customer_ref": self.partner_id.ref or "",
            "customer_vat": self.partner_id.vat or "",
            "phone_number": self.phone_number,
            "current_tariff_product": self.current_tariff_product.default_code,
            "description": self.current_tariff_product.with_context(
                lang=self.lang
            ).showed_name,
            "technology": self.service_technology_id.name,
            "supplier": self.service_supplier_id.name,
            "lang": self.lang,
            "iban": self.mandate_id.partner_bank_id.sanitized_acc_number,
            "is_terminated": self.is_terminated,
            "date_start": self.date_start,
            "date_end": self.date_end,
            "fiber_signal": fiber_signal,
            "subscription_type": subscription_type_map.get(
                self.service_contract_type, "broadband"
            ),
            "address": AddressService(self.env, self.service_partner_id).__dict__,
            "subscription_technology": self._get_subscription_tech(),
            "parent_contract": self.parent_pack_contract_id.code
            if self.parent_pack_contract_id
            else "",
            "shared_bond_id": self.shared_bond_id,
            "has_landline_phone": not bool(self.current_tariff_product.without_fix)
            if self.service_contract_type != "mobile"
            else False,
            "available_operations": self._get_available_operations(),
            "price": self._product_price(self.current_tariff_product),
            "bandwidth": self._get_bandwidth(),
            "data": self._get_data(),
            "minutes": self._get_minutes(),
        }

    def _get_mobile_available_operations(self):
        if self.shared_bond_id:
            return ["AddOneShotMobile"]  # mobile is sharing data
        else:
            mobile_available_operations = ["ChangeTariffMobile"]
            # check is contract with T-Conserva
            if (
                not self.current_tariff_product.id
                == self.env.ref("somconnexio.TarifaConserva").id
            ):
                mobile_available_operations.append("AddOneShotMobile")
            # check bonified mobile with assocciated fiber
            if not self.parent_pack_contract_id:
                mobile_available_operations.append("ChangeContractHolder")
            return mobile_available_operations

    def _get_broadband_available_operations(self):
        if self.service_contract_type == "router4G":
            return ["ChangeContractHolder"]
        elif self.service_contract_type == "adsl":
            adsl_available_operations = ["ChangeContractHolder"]
            if self.current_tariff_product.without_fix:
                adsl_available_operations.append("ChangeTariffFiberOutLandline")
            else:
                adsl_available_operations.append("ChangeTariffFiberLandline")
            return adsl_available_operations
        else:
            fiber_available_operations = []
            # Fiber
            if (
                not self.current_tariff_product.without_fix
                and self._get_bandwidth() <= 300
            ):
                # Fiber 100/300 without landline
                fiber_available_operations.append("ChangeTariffFiberOutLandline")
            if not self.number_contracts_in_pack:
                # Fiber without mobiles associated
                fiber_available_operations.append("ChangeContractHolder")
            return fiber_available_operations

    def _get_available_operations(self):
        """
        Resolve available operations to contract detail in somoffice
        """
        available_operations = []
        if self.service_contract_type == "mobile":
            available_operations = self._get_mobile_available_operations()
        elif self.service_contract_type != "switchboard":
            available_operations = self._get_broadband_available_operations()
        return available_operations

    def _product_price(self, product):
        if not product:
            return 0.0
        pricelist = self.env["product.pricelist"].search([("code", "=", "21IVA")])
        return pricelist._get_product_price(product, 1)

    def _get_bandwidth(self):
        return int(
            self.current_tariff_product.without_lang().get_catalog_name("Bandwidth")
            or 0
        )

    def _get_minutes(self):
        if self.service_contract_type == "mobile":
            minutes = self.current_tariff_product.without_lang().get_catalog_name(
                "Min"
            )
            return 99999 if minutes == "UNL" else int(minutes)
        return 0

    def _get_data(self):
        return int(
            self.current_tariff_product.without_lang().get_catalog_name("Data") or 0
        )

    def _get_subscription_tech(self):
        return (
            self.service_contract_type
            if self.service_contract_type in ("adsl", "mobile", "router4G")
            else "fiber"
        )
