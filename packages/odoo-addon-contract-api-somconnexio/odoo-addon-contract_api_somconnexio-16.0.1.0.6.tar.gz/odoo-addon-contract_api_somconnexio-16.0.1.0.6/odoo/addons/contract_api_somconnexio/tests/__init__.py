from .models import test_contract
from .services import (
    test_contract_change_tariff_service,
    test_contract_contract_process,
    test_contract_email_change_service,
    test_contract_iban_change_service,
    test_contract_one_shot_service,
)

from .services.contract_process import (
    test_fiber_contract_process,
    test_mobile_contract_process,
    test_sb_contract_process,
)
from .services.contract_services import (
    test_contract_contract_service,
    test_contract_count_controller,
    test_contract_get_fiber_contracts_to_pack_controller,
    test_contract_get_terminate_reasons,
    test_contract_search_controller,
    test_contract_terminate_controller,
)

from .wizards import (
    test_contract_iban_change,
    test_contract_one_shot_request,
    test_contract_tariff_change,
    test_partner_email_change,
)
