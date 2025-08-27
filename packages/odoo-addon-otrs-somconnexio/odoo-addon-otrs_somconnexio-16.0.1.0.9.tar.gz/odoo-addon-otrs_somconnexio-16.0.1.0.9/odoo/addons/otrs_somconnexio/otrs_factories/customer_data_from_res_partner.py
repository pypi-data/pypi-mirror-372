from otrs_somconnexio.otrs_models.customer_data import CustomerData

from .base_data import BaseDataFromOdoo


class CustomerDataFromResPartner(BaseDataFromOdoo):
    DataModel = CustomerData

    def __init__(self, partner):
        self.partner = partner

    def _get_data(self):
        customer_params = {
            "id": self.partner.ref,
            "vat_number": self.partner.vat,
            "first_name": self.partner.firstname,
            "name": self.partner.lastname,
            "street": self.partner.full_street,
            "zip": self.partner.zip,
            "city": self.partner.city,
            "subdivision": "{}".format(self.partner.state_id.code),
            "has_active_contracts": self.partner.has_active_contract,
            "language": self.partner.lang,
        }
        if self.partner.is_company:
            customer_params.update({"first_name": self.partner.lastname, "name": ""})
        return customer_params
