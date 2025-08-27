from .base_data_from_crm_lead_line import BaseDataFromCRMLeadLine


class BroadbandDataFromCRMLeadLine(BaseDataFromCRMLeadLine):
    def __init__(self, crm_lead_line):
        super().__init__(crm_lead_line)
        self.isp_info = crm_lead_line.broadband_isp_info

    def _get_data(self):
        ba_data = super()._get_data()
        ba_data.update(
            {
                "phone_number": (
                    "REVISAR FIX"
                    if self.crm_lead_line.check_phone_number
                    else self.isp_info.previous_phone_number
                    or self.isp_info.phone_number
                ),
                "service_address": self.isp_info.service_full_street,
                "service_city": self.isp_info.service_city,
                "service_zip": self.isp_info.service_zip_code,
                "service_subdivision": self.isp_info.service_state_id.name,
                "service_subdivision_code": "{}".format(
                    self.isp_info.service_state_id.code
                ),
                "shipment_address": self.isp_info.delivery_full_street,
                "shipment_city": self.isp_info.delivery_city,
                "shipment_zip": self.isp_info.delivery_zip_code,
                "shipment_subdivision": self.isp_info.delivery_state_id.name,
                "previous_contract_phone": self.isp_info.previous_contract_phone,
                "previous_contract_address": self.isp_info.previous_contract_address,
                "previous_service": self._previous_service(),
                "previous_internal_provider": self._previous_internal_provider(),
                "mm_fiber_coverage": self.isp_info.mm_fiber_coverage,
                "vdf_fiber_coverage": self.isp_info.vdf_fiber_coverage,
                "asociatel_fiber_coverage": self.isp_info.asociatel_fiber_coverage,
                "orange_fiber_coverage": self.isp_info.orange_fiber_coverage,
                "adsl_coverage": self.isp_info.adsl_coverage,
            }
        )
        return ba_data

    def _previous_internal_provider(self):
        if self.isp_info.service_supplier_id:
            return self.isp_info.service_supplier_id.ref
        else:
            return ""

    def _previous_service(self):
        previous_service = self.crm_lead_line.broadband_isp_info.previous_service
        if not previous_service:
            return "None"

        OTRS_PREVIOUS_SERVICE_MAPPING = {
            "adsl": "ADSL",
            "fiber": "Fibra",
            "4G": "4G",
        }
        return OTRS_PREVIOUS_SERVICE_MAPPING.get(previous_service, "Other")
