from .listeners import test_crm_lead_listener
from .models import (
    test_contract,
    test_res_partner,
    test_crm_lead,
    test_crm_lead_line,
)
from .services import (
    test_mobile_activation_date_service,
    test_contract_get_fiber_contracts_to_pack_service,
)
from .services.contract_process import test_fiber_contract_process
from .wizards import (
    test_contract_address_change_wizard,
    test_contract_iban_change_wizard,
    test_contract_mobile_tariff_change_wizard,
    test_contract_one_shot_request_wizard,
)
from .otrs_factories import (
    test_adsl_data_from_crm_lead_line,
    test_customer_data_from_res_partner,
    test_fiber_data_from_crm_lead_line,
    test_mobile_data_from_crm_lead_line,
    test_router_4G_data_from_crm_lead_line,
    test_service_data_from_crm_lead_line,
    test_switchboard_data_from_crm_lead_line,
)
from .otrs_services import test_update_ticket_with_error