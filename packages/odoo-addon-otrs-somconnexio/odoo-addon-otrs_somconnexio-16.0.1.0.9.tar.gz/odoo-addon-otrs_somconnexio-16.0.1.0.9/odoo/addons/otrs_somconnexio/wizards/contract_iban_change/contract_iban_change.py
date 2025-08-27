from odoo import models
from odoo.exceptions import ValidationError

from odoo.addons.otrs_somconnexio.otrs_services.update_ticket_with_error import (
    UpdateTicketWithError,
)


class ContractIbanChangeWizard(models.TransientModel):
    _inherit = "contract.iban.change.wizard"

    def run_from_api(self, **params):
        try:
            super().run_from_api(**params)
        except ValidationError as error:
            ticket_id = params["ticket_id"]
            error = {
                "title": "Error en el canvi d'IBAN",
                "body": "Banc del nou IBAN desconegut: {}.".format(params.get("iban"))
                + "\nDesprés d'afegir el seu banc corresponent al registre "
                + "d'ODOO, torna a intentar aquesta petició.",
            }
            dynamic_fields_dct = {"ibanKO": 1}
            update_ticket = UpdateTicketWithError(ticket_id, error, dynamic_fields_dct)

            update_ticket.run()
