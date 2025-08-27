from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.addons.component.core import Component
from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.base_rest.components.service import skip_secure_params
from odoo.exceptions import MissingError
from datetime import datetime
from werkzeug.exceptions import BadRequest
from ..services import (
    contract_iban_change_service,
    contract_one_shot_service,
    contract_change_tariff_service,
    contract_email_change_service,
)
from . import schemas
import logging

try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")


class ContractService(Component):
    _inherit = "base.rest.service"
    _name = "contract.service"
    _usage = "contract"
    _collection = "sc.api.key.services"
    _description = """
        Service to manage contracts
    """

    def _validator_search(self):
        # Double validation is necessary to allow double schema
        return {
            "customer_ref": {
                "type": "string",
                "excludes": ["code", "partner_vat"],
            },
            "code": {
                "type": "string",
                "excludes": ["partner_vat", "phone_number", "customer_ref"],
            },
            "partner_vat": {
                "type": "string",
                "excludes": ["code", "phone_number", "customer_ref"],
            },
            "phone_number": {
                "type": "string",
                "excludes": ["partner_vat", "code"],
            },
            "subscription_type": {
                "type": "string",
                "dependencies": "customer_ref",
                "allowed": ["mobile", "broadband"],
            },
            **schemas.S_CONTRACT_PAGING,
        }

    def search(self, **params):
        v = Validator()
        if not (
            v.validate(
                params,
                self.validator_search_contract(),
            )
            or v.validate(
                params,
                self.validator_search_multi_filter_contract(),
                )
        ):
            raise ValidationError(_('BadRequest {}').format(v.errors))
        return self.env['contract.service'].search(**params)

    @staticmethod
    def validator_search_contract():
        return schemas.S_CONTRACT_SEARCH

    @staticmethod
    def validator_search_multi_filter_contract():
        return schemas.S_CUSTOMER_CONTRACT_MULTI_FILTER_SEARCH


class ContractServiceModel(models.Model):
    _name = 'contract.service'

    def terminate(self, **params):
        contract_code = params["code"]
        terminate_reason_code = params["terminate_reason"]
        terminate_comment = params.get("terminate_comment")
        terminate_date = datetime.strptime(params["terminate_date"], "%Y-%m-%d").date()
        terminate_user_reason_code = params["terminate_user_reason"]

        contract = self.env["contract.contract"].search([("code", "=", contract_code)])
        terminate_reason = self.env["contract.terminate.reason"].search(
            [("code", "=", terminate_reason_code)]
        )
        terminate_user_reason = self.env["contract.terminate.user.reason"].search(
            [("code", "=", terminate_user_reason_code)]
        )

        if not contract:
            raise MissingError(
                _("Contract with code {} not found.".format(contract_code))
            )
        if not terminate_reason:
            raise MissingError(
                _(
                    "Terminate reason with code {} not found.".format(
                        terminate_reason_code
                    )
                )
            )
        if not terminate_user_reason:
            raise MissingError(
                _(
                    "Terminate user reason with code {} not found.".format(
                        terminate_user_reason_code
                    )
                )
            )

        contract.sudo().terminate_contract(
            terminate_reason, terminate_comment, terminate_date, terminate_user_reason
        )
        return {"result": "OK"}

    def _add_customer_domain_filters(
        self, domain, search_params, phone_number=None, subscription_type=None, **_
    ):
        if phone_number:
            domain += [("phone_number", "ilike", phone_number)]
            search_params += ["phone_number"]
        if subscription_type:
            domain += [
                (
                    "service_technology_id",
                    "=" if subscription_type == "mobile" else "!=",
                    self.env.ref("somconnexio.service_technology_mobile").id,
                )
            ]
            search_params += ["subscription_type"]

    def get_fiber_contracts_to_pack(self, **params):
        contracts = self.env["fiber.contract.to.pack.service"].create(**params)

        result = [self._to_dict(contract) for contract in contracts]

        return result

    def search(self, **params):
        limit = params.get("limit", 10)
        offset = params.get("offset", 0)
        sortBy = params.get("sortBy", "")
        sortOrder = params.get("sortOrder", "")
        if limit:
            if isinstance(limit, int) or isinstance(limit, str) and limit.isdigit():
                limit = int(limit)
            else:
                raise wrapJsonException(
                    BadRequest("Limit must be numeric"),
                    include_description=True,
                )
        if offset:
            if isinstance(offset, int) or isinstance(offset, str) and offset.isdigit():
                offset = int(offset)
            else:
                raise wrapJsonException(
                    BadRequest("Offset must be numeric"),
                    include_description=True,
                )
        if sortBy:
            if sortBy not in self.env["contract.contract"].fields_get():
                raise wrapJsonException(
                    BadRequest("Invalid field to sortBy"), include_description=True
                )
        if sortOrder:
            if sortOrder == "ASCENDENT":
                pass
            elif sortOrder == "DESCENDENT":
                sortOrder = " DESC"
            else:
                raise wrapJsonException(
                    BadRequest("sortOrder must be ASCENDING or DESCENDING"),
                    include_description=True,
                )
        domain, search_params = self._get_search_domain(**params)
        contracts = (
            self.env["contract.contract"]
            .sudo()
            .search(domain, limit=limit, offset=offset, order=sortBy + sortOrder)
        )
        if not contracts:
            raise MissingError(
                _(
                    "No contract with {} could be found".format(
                        " - ".join(
                            [
                                ": ".join([search_param, params.get(search_param)])
                                for search_param in search_params
                            ]
                        )
                    )
                )
            )

        ret = {"contracts": [contract._to_dict() for contract in contracts]}
        if limit or offset or sortBy:
            ret["paging"] = {
                "limit": limit,
                "offset": offset,
                "totalNumberOfRecords": self.env["contract.contract"]
                .sudo()
                .search_count(domain),
            }
            if sortBy:
                ret["paging"].update(
                    {
                        "sortBy": sortBy,
                        "sortOrder": "DESCENDENT"
                        if sortOrder == " DESC"
                        else "ASCENDENT",
                    }
                )
        return ret

    def count(self):
        domain = [("is_terminated", "=", False)]
        contracts_number = self.env["contract.contract"].sudo().search_count(domain)
        return {"contracts": contracts_number}

    def get_terminate_reasons(self):
        terminate_reasons = self.env["contract.terminate.reason"].search([])
        user_terminate_reasons = self.env["contract.terminate.user.reason"].search([])

        return {
            "terminate_reasons": [
                {"code": reason.code, "name": reason.name}
                for reason in terminate_reasons
            ],
            "terminate_user_reasons": [
                {"code": reason.code, "name": reason.name}
                for reason in user_terminate_reasons
            ],
        }

    def _get_search_domain(
        self,
        code=None,
        phone_number=None,
        partner_vat=None,
        customer_ref=None,
        **params
    ):
        domain = [("is_terminated", "=", False)]
        search_params = []
        if code:
            domain += [("code", "=", code)]
            search_params = ["code"]
        elif customer_ref:
            domain += [("partner_id.ref", "=", customer_ref)]
            search_params = ["customer_ref"]
            self._add_customer_domain_filters(
                domain, search_params, phone_number, **params
            )
        elif phone_number:
            domain += [("phone_number", "=", phone_number)]
            search_params = ["phone_number"]
        elif partner_vat:
            domain += [
                ("partner_id.vat", "=", partner_vat),
                ("partner_id.parent_id", "=", False),
            ]
            search_params = ["partner_vat"]
        return domain, search_params


class ContractAvailableFibersToLinkWithMobileService(Component):
    _inherit = "base.rest.service"
    _name = "contract.available.fibers.to.link.with.mobile.service"
    _usage = "contract/available-fibers-to-link-with-mobile"
    _collection = "sc.api.key.services"
    _description = """
        Service to get contract which have available fibers to link
        with mobile service
    """

    def search(self, **params):
        contracts = self.env['fiber.contract.to.pack.service'].create(**params)
        result = [contract._to_dict() for contract in contracts]
        return result

    def _validator_search(self):
        return {"partner_ref": {"type": "string", "required": True}}


class ContractPublicService(Component):
    _inherit = "base.rest.service"
    _name = "contract.public.service"
    _usage = "contract"
    _collection = "sc.public.services"
    _description = """
        Service to create contracts
    """

    @skip_secure_params
    # pylint: disable=W8106
    def create(self, **params):
        self.env["contract.contract"].with_delay().create_contract(**params)
        return {"result": "OK"}


class ContractPublicCountService(Component):
    _inherit = "base.rest.service"
    _name = "contract.public.count.service"
    _usage = "contract-count"
    _collection = "sc.public.services"
    _description = """
        Service to count contracts
    """

    # pylint: disable=W8106
    def get(self):
        return self.env['contract.service'].count()

    def _validator_return_get(self):
        return {"contracts": {"type": "integer", "required": True}}


class ContractPublicOneShotService(Component):
    _inherit = "base.rest.service"
    _name = "contract.one.shot.public.service"
    _usage = "add-one-shot"
    _collection = "sc.public.services"
    _description = """
        Create One Shot product
    """

    @skip_secure_params
    # pylint: disable=W8106
    def create(self, **params):
        service = contract_one_shot_service.ContractOneShotAdditionService(self.env)
        return service.run_from_api(**params)


class ContractPublicChangeTariffService(Component):
    _inherit = "base.rest.service"
    _name = "contract.change.tariff.public.service"
    _usage = "change-tariff"
    _collection = "sc.public.services"
    _description = """
        Change tariff in contract
    """

    @skip_secure_params
    # pylint: disable=W8106
    def create(self, **params):
        service = contract_change_tariff_service.ContractChangeTariffService(self.env)
        return service.run_from_api(**params)


class ContractPublicEmailChangeService(Component):
    _inherit = "base.rest.service"
    _name = "contract.change.email.public.service"
    _usage = "contract-email-change"
    _collection = "sc.public.services"
    _description = """
        Change tariff in contract
    """

    @skip_secure_params
    # pylint: disable=W8106
    def create(self, **params):
        service = contract_email_change_service.PartnerEmailChangeService(self.env)
        return service.run_from_api(**params)


class ContractIbanChangeService(Component):
    _inherit = "base.rest.service"
    _name = "contract.change.iban.public.service"
    _usage = "contract-iban-change"
    _collection = "sc.public.services"
    _description = """
        Change tariff in contract
    """

    @skip_secure_params
    # pylint: disable=W8106
    def create(self, **params):
        service = contract_iban_change_service.ContractIbanChangeService(self.env)
        return service.run_from_api(**params)


class ContractTerminateService(Component):
    _inherit = "base.rest.service"
    _name = "contract.terminate.service"
    _usage = "contract/terminate"
    _collection = "sc.api.key.services"
    _description = """
        Terminate contract
    """

    # pylint: disable=W8106
    def create(self, **params):
        response = self.env["contract.service"].terminate(**params)
        return response

    def _validator_create(self):
        return schemas.S_TERMINATE_CONTRACT


class ContractTerminateReason(Component):
    _inherit = "base.rest.service"
    _name = "contract.terminate.reason.service"
    _usage = "contract/terminate_reasons"
    _collection = "sc.api.key.services"
    _description = """
        Terminate contract
    """

    def get(self):
        response = self.env["contract.service"].get_terminate_reasons()
        return response
