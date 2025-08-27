from odoo import models, _
from otrs_somconnexio.otrs_models.ticket_types.add_data_ticket import AddDataTicket


class ContractOneShotRequestWizard(models.TransientModel):
    _inherit = "contract.one.shot.request.wizard"

    def button_add(self):
        self.ensure_one()
        if self.one_shot_product_id.product_tmpl_id == self.env.ref(
            "somconnexio.DadesAddicionals_product_template"
        ):
            self.with_delay().create_additional_data_otrs_ticket()
            return True
        else:
            return super().button_add()

    def create_additional_data_otrs_ticket(self):
        """Create an OTRS additional data ticket"""

        fields_dict = {
            "phone_number": self.contract_id.phone_number,
            "new_product_code": self.one_shot_product_id.default_code,
            "subscription_email": self.contract_id.email_ids[0].email,
            "language": self.contract_id.partner_id.lang,
        }

        AddDataTicket(
            self.contract_id.partner_id.vat,
            self.contract_id.partner_id.ref,
            fields_dict,
        ).create()

        message = _("OTRS add data ticket created. Added additional data bond: '{}'")
        self.contract_id.message_post(
            message.format(self.one_shot_product_id.showed_name)
        )
