from itertools import combinations

from odoo import models, _
from odoo.exceptions import MissingError, ValidationError

from otrs_somconnexio.client import OTRSClient


class CRMLead(models.Model):
    _inherit = "crm.lead"

    def link_pack_tickets(self):
        fiber_ticket = None
        fiber_ticket_number = ""
        OTRS_client = OTRSClient()
        mobile_ticket_numbers = {
            line.id: line.ticket_number for line in self.lead_line_ids if line.is_mobile
        }
        mobile_tickets = {
            mobile_ticket_number: OTRS_client.get_ticket_by_number(mobile_ticket_number)
            for mobile_ticket_number in mobile_ticket_numbers.values()
            if mobile_ticket_number
        }
        for line in [line for line in self.lead_line_ids if line.ticket_number]:
            if line.is_fiber:
                fiber_ticket_number = line.ticket_number
                fiber_ticket = OTRS_client.get_ticket_by_number(fiber_ticket_number)

        if not all(mobile_ticket_numbers.values()) or not fiber_ticket_number:
            raise MissingError(
                _(
                    "Either mobile or fiber ticket numbers where not found among "
                    "the lines of this pack CRMLead"
                )
            )
        if not all(mobile_tickets.values()):
            raise MissingError(
                _("Mobile tickets not found in OTRS with ticket_numbers {}").format(
                    ",".join(
                        number
                        for number in mobile_tickets
                        if not mobile_tickets[number]
                    )
                )
            )
        elif not fiber_ticket:
            raise MissingError(
                _("Fiber ticket not found in OTRS with ticket_number {}").format(
                    fiber_ticket_number
                )
            )
        for mobile_ticket in mobile_tickets.values():
            OTRS_client.link_tickets(
                fiber_ticket.tid, mobile_ticket.tid, link_type="ParentChild"
            )

    def link_mobile_tickets_in_pack(self):
        OTRS_client = OTRSClient()

        # Either 2 or 3 lines
        sharing_data_mobile_lines = self.mobile_lead_line_ids.filtered(
            lambda l: (l.product_id.has_sharing_data_bond)
        )
        if len(sharing_data_mobile_lines) not in [2, 3]:
            raise ValidationError(_("We cannot build packs with <2 or >3 mobiles"))

        sharing_data_mobile_tickets = [
            OTRS_client.get_ticket_by_number(line.ticket_number)
            for line in sharing_data_mobile_lines
        ]
        tickets_paired = combinations(sharing_data_mobile_tickets, 2)
        for pair_combination in tickets_paired:
            paired_tickets = list(pair_combination)
            OTRS_client.link_tickets(
                paired_tickets[0].tid, paired_tickets[1].tid, link_type="Normal"
            )
