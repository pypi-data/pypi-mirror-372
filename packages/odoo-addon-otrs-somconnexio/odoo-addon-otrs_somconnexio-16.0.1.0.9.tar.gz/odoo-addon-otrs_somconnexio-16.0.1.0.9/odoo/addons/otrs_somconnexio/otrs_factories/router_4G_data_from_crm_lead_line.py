from otrs_somconnexio.otrs_models.router_4G_data import Router4GData

from .broadband_data_from_crm_lead_line import BroadbandDataFromCRMLeadLine


class Router4GDataFromCRMLeadLine(BroadbandDataFromCRMLeadLine):
    DataModel = Router4GData

    def _get_data(self):
        router_4G_data = super()._get_data()
        router_4G_data.update({"technology": router_4G_data.get("technology") or "4G"})
        return router_4G_data
