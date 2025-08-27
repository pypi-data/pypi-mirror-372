from odoo.addons.somconnexio.services.schemas import S_ADDRESS_CREATE
from odoo.addons.base_rest_somconnexio.services.validator_helper import (
    boolean_validator,
)


S_CONTRACT_SERVICE_INFO_CREATE = {
    "phone_number": {"type": "string", "required": True, "empty": False},
}

S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE = {
    "router_mac_address": {
        "type": "string",
        "required": False,
        "empty": True,
        "regex": "-|^[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$",
    },
}

S_MOBILE_CONTRACT_SERVICE_INFO_CREATE = {
    "icc": {"type": "string", "required": True, "empty": False},
    "shared_bond_id": {"empty": True},
}
S_ADSL_CONTRACT_SERVICE_INFO_CREATE = {
    "administrative_number": {"type": "string", "required": True, "empty": False},
    "router_product_id": {"type": "string", "required": True},
    "router_serial_number": {"type": "string", "required": True, "empty": False},
    "ppp_user": {"type": "string", "required": True, "empty": False},
    "ppp_password": {"type": "string", "required": True, "empty": False},
    "endpoint_user": {"type": "string", "required": True, "empty": False},
    "endpoint_password": {"type": "string", "required": True, "empty": False},
}

S_VODAFONE_ROUTER_4G_CONTRACT_SERVICE_INFO_CREATE = {
    "vodafone_id": {"type": "string", "required": True, "empty": False},
    "vodafone_offer_code": {"empty": True},
    "router_product_id": {"type": "string", "required": True},
    "icc": {"type": "string", "required": True},
}

S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "vodafone_id": {"type": "string", "required": True, "empty": False},
    "vodafone_offer_code": {"empty": True},
}

S_MM_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "mm_id": {"type": "string", "required": True, "empty": False},
}

S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "suma_id": {"type": "string", "required": True, "empty": False},
}

S_XOLN_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "external_id": {"type": "string", "required": True, "empty": False},
    "id_order": {"type": "string", "required": True, "empty": False},
    "project": {"type": "string", "required": True, "empty": False},
    "router_product_id": {"type": "string", "required": True},
    "router_serial_number": {"type": "string", "required": True, "empty": False},
}
S_SWITCHBOARD_CONTRACT_SERVICE_INFO_CREATE = {
    "phone_number_2": {"type": "string"},
    "mobile_phone_number": {"type": "string"},
    "icc": {"type": "string"},
    "agent_name": {"type": "string"},
    "agent_email": {"type": "string"},
    "extension": {"type": "string"},
    "MAC_CPE_SIP": {"type": "string"},
    "SIP_channel_name": {"type": "string"},
    "SIP_channel_password": {"type": "string"},
}

S_CONTRACT_CREATE = {
    "code": {"type": "string", "required": False, "empty": False},
    "iban": {"type": "string", "required": True, "empty": False},
    "email": {"type": "string", "required": True, "empty": True},
    "mobile_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_MOBILE_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "adsl_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE,
            **S_ADSL_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "vodafone_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "router_4G_service_contract_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_VODAFONE_ROUTER_4G_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "mm_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_MM_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "orange_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "xoln_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE,
            **S_XOLN_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "switchboard_service_contract_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_SWITCHBOARD_CONTRACT_SERVICE_INFO_CREATE,
        },
    },
    "partner_id": {"type": "string", "required": True},
    "service_address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "service_technology": {"type": "string", "required": True, "empty": False},
    "service_supplier": {"type": "string", "required": True, "empty": False},
    "fiber_signal_type": {
        "type": "string",
        "allowed": ["", "fibraCoaxial", "fibraFTTH", "fibraIndirecta", "NEBAFTTH"],
    },
    "contract_lines": {
        "type": "list",
        "dependencies": {"contract_line": None},
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
                "date_start": {
                    "type": "string",
                    "required": True,
                    "regex": "\\d{4}-[01]\\d-[0-3]\\d [0-2]\\d:[0-5]\\d:[0-5]\\d",
                },
            },
        },
    },
    # We must evaluate the "contract_line" field because OTRS cannot send a list
    # with only one element, so we do this differentiation to know how to treat it.
    "contract_line": {
        "type": "dict",
        "dependencies": {"contract_lines": None},
        "schema": {
            "product_code": {"type": "string", "required": True},
            "date_start": {
                "type": "string",
                "required": True,
                "regex": "\\d{4}-[01]\\d-[0-3]\\d [0-2]\\d:[0-5]\\d:[0-5]\\d",
            },
        },
    },
    # OTRS sends a '{}' as empty value for parent_pack_contract_id.
    # Therefore, we can't restrict this field as string
    # if we want to avoid BadRequest errors
    "parent_pack_contract_id": {"empty": True},
    # OTRS sends a '{}' as empty value for mobile_pack_contracts.
    # Therefore, we can't restrict this field as string
    # if we want to avoid BadRequest errors
    "mobile_pack_contracts": {"empty": True},
}

S_CONTRACT_RETURN_CREATE = {"id": {"type": "integer"}}

S_PREVIOUS_PROVIDER_REQUEST_SEARCH = {
    "mobile": {"type": "string", "check_with": boolean_validator},
    "broadband": {"type": "string", "check_with": boolean_validator},
}

S_PREVIOUS_PROVIDER_RETURN_SEARCH = {
    "count": {"type": "integer"},
    "providers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True},
            },
        },
    },
}

S_CONTRACT_ONE_SHOT_ADDITION = {
    "product_code": {"type": "string", "required": True},
    "phone_number": {"type": "string", "required": True},
}

S_CONTRACT_CHANGE_TARIFF = {
    "product_code": {"type": "string", "required": True},
    "phone_number": {"type": "string", "empty": True},
    "code": {"type": "string", "empty": True},
    "start_date": {"empty": True},
    # OTRS sends a '{}' as empty value for parent_pack_contract_id.
    # Therefore, we can't restrict this field as string
    # if we want to avoid BadRequest errors
    "parent_pack_contract_id": {"empty": True},
    "shared_bond_id": {"empty": True},
}

S_CONTRACT_IBAN_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "iban": {"type": "string", "required": True},
    "contracts": {"type": "string", "required": False},
}

S_CONTRACT_EMAIL_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "email": {"type": "string", "required": True},
    "contracts": {"type": ["dict", "string"], "required": True},
    "start_date": {"type": "string"},
    "summary": {"type": "string"},
    "done": {"type": "boolean"},
}

S_CONTRACT_PAGING = {
    "limit": {
        "type": "string",
    },
    "offset": {
        "type": "string",
    },
    "sortBy": {
        "type": "string",
    },
    "sortOrder": {"type": "string", "dependencies": ["sortBy"]},
}

S_CUSTOMER_CONTRACT_MULTI_FILTER_SEARCH = {
    "customer_ref": {"type": "string", "required": True},
    "phone_number": {
        "type": "string",
        "dependencies": "customer_ref",
    },
    "subscription_type": {
        "type": "string",
        "dependencies": "customer_ref",
        "allowed": ["mobile", "broadband"],
    },
    **S_CONTRACT_PAGING,
}

S_CONTRACT_SEARCH = {
    "customer_ref": {
        "type": "string",
        "excludes": ["code", "partner_vat", "phone_number"],
        "required": True,
    },
    "code": {
        "type": "string",
        "excludes": ["partner_vat", "phone_number", "customer_ref"],
        "required": True,
    },
    "partner_vat": {
        "type": "string",
        "excludes": ["code", "phone_number", "customer_ref"],
        "required": True,
    },
    "phone_number": {
        "type": "string",
        "excludes": ["partner_vat", "code", "customer_ref"],
        "required": True,
    },
    **S_CONTRACT_PAGING,
}

S_CONTRACT_GET_FIBER_CONTRACTS_TO_PACK = {
    "partner_ref": {
        "type": "string",
        "required": True,
    },
    "mobiles_sharing_data": {
        "type": "string",
        "excludes": ["all"],
        "check_with": boolean_validator,
    },
    "all": {
        "type": "string",
        "excludes": ["mobiles_sharing_data"],
        "check_with": boolean_validator,
    },
}

S_TERMINATE_CONTRACT = {
    "code": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_date": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_reason": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_user_reason": {
        "type": "string",
        "required": False,
    },
    "terminate_comment": {
        "type": "string",
        "required": False,
    },
}
