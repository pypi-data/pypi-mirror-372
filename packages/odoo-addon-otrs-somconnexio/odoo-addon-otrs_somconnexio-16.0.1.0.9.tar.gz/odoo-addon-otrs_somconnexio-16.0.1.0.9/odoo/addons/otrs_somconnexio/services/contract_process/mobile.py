from odoo import _
from odoo.exceptions import UserError
from odoo.models import AbstractModel


class MobileContractProcess(AbstractModel):
    _name = "mobile.contract.process"
    _inherit = ["mobile.contract.process", "base.contract.process"]

    def _get_parent_pack_contract(self, contract, parent_pack_contract_id):
        parent_contract = super()._get_parent_pack_contract(
            contract, parent_pack_contract_id
        )
        if not parent_contract:
            # If OTRS already knows the code of the contract fiber to be linked:
            this_crm_lead_l = (
                self.env["crm.lead.line"]
                .sudo()
                .search([("ticket_number", "=", contract.ticket_number)])
            )
            parent_crm_lead_line = this_crm_lead_l.lead_id.lead_line_ids.filtered(
                "is_fiber"
            )
            if not parent_crm_lead_line:
                return True

            parent_contract = (
                self.env["contract.contract"]
                .sudo()
                .search(
                    [("crm_lead_line_id", "=", parent_crm_lead_line.id)],
                )
            )
            if not parent_contract:
                raise UserError(
                    _(
                        "Fiber contract of CRMLead ID = {}, ticket = {} not found"
                    ).format(
                        this_crm_lead_l.lead_id.id,
                        parent_crm_lead_line.ticket_number,
                    )
                )
