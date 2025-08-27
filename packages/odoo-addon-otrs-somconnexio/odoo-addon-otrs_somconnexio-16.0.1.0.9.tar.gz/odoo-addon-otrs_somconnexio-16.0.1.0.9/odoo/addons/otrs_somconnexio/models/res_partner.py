from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    has_lead_in_provisioning = fields.Boolean(
        string="Has service in provisioning",
        compute="_compute_lead_in_provisioning",
        readonly=True,
    )

    @api.depends(
        "opportunity_ids.stage_id",
        "opportunity_ids.lead_line_ids",
        "opportunity_ids.lead_line_ids.ticket_number",
        "contract_ids.ticket_number",
    )
    def _compute_lead_in_provisioning(self):
        provisioning_crm_stages = [
            self.env.ref("crm.stage_lead1"),  # New
            self.env.ref("crm.stage_lead3"),  # Remesa
            self.env.ref("crm.stage_lead4"),  # Won
        ]
        for record in self:
            crm_in_provisioning = record.opportunity_ids.filtered(
                lambda cl: cl.stage_id in provisioning_crm_stages
            )
            contract_ticket_numbers = {
                cc.ticket_number for cc in record.contract_ids if cc.ticket_number
            }
            crm_in_provisioning = {
                ll
                for cl in crm_in_provisioning
                for ll in cl.lead_line_ids
                if not ll.ticket_number
                or ll.ticket_number not in contract_ticket_numbers
            }
            record.has_lead_in_provisioning = crm_in_provisioning
