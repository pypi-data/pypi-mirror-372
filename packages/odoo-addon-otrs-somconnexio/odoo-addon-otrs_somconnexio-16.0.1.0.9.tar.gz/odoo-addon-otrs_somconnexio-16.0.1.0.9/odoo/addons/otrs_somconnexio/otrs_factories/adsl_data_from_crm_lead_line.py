from otrs_somconnexio.otrs_models.adsl_data import ADSLData

from .broadband_data_from_crm_lead_line import BroadbandDataFromCRMLeadLine


class ADSLDataFromCRMLeadLine(BroadbandDataFromCRMLeadLine):
    DataModel = ADSLData

    def _get_data(self):
        adsl_data = super()._get_data()
        adsl_data.update(
            {
                "landline_phone_number": self._keep_landline_phone_number(),
                "technology": adsl_data.get("technology") or "ADSL",
            }
        )
        return adsl_data

    def _keep_landline_phone_number(self):
        if self.crm_lead_line.broadband_isp_info.keep_phone_number:
            return "current_number"
        else:
            return "new_number"
