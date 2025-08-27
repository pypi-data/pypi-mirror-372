from odoo import models, fields

from otrs_somconnexio.otrs_models.ticket_factory import TicketFactory
from otrs_somconnexio.services.update_process_ticket_with_coverage_tickets_info_service import (  # noqa
    UpdateProcessTicketWithCoverageTicketsInfoService,
)

from ..otrs_factories.customer_data_from_res_partner import CustomerDataFromResPartner
from ..otrs_factories.service_data_from_crm_lead_line import ServiceDataFromCRMLeadLine


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    ticket_number = fields.Char(string="Ticket Number")

    def create_ticket(self):
        ticket = TicketFactory(
            ServiceDataFromCRMLeadLine(self).build(),
            CustomerDataFromResPartner(self.lead_id.partner_id).build(),
        ).build()
        ticket.create()
        self.write({"ticket_number": ticket.number})
        self.update_ticket_with_coverage_info(ticket.id)

    def update_ticket_with_coverage_info(self, ticket_id):
        # Do not add coverage tickets in mobile ones
        if self.is_mobile:
            return

        # Search all the emails of partner
        contract_emails = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_id.id),
                ("type", "=", "contract-email"),
            ]
        )
        emails = [c.email for c in contract_emails]
        emails.append(self.partner_id.email)

        update_ticket_service = UpdateProcessTicketWithCoverageTicketsInfoService(
            ticket_id
        )
        for email in emails:
            update_ticket_service.run(email)
