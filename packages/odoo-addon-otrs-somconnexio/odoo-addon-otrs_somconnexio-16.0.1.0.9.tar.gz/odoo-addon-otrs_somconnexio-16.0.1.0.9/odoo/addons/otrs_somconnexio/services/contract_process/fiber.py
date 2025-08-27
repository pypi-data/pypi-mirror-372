from otrs_somconnexio.services.set_fiber_contract_code_mobile_ticket import (
    SetFiberContractCodeMobileTicket,
)
from otrs_somconnexio.services.unblock_mobile_pack_ticket import UnblockMobilePackTicket

from ..mobile_activation_date_service import MobileActivationDateService

from odoo.models import AbstractModel


class FiberContractProcess(AbstractModel):
    _inherit = "fiber.contract.process"
    _description = """
        Fiber Contract creation
    """

    def create(self, **params):
        contract_dict = super(FiberContractProcess, self).create(**params)
        # Update mobile tiquets
        self._update_pack_mobile_tickets(contract_dict)

        return contract_dict

    def _update_pack_mobile_tickets(self, contract_dict):
        crm_lead_line = (
            self.env["crm.lead.line"]
            .sudo()
            .search([("ticket_number", "=", contract_dict["ticket_number"])])
        )
        mobile_lines = crm_lead_line.lead_id.lead_line_ids.filtered("is_mobile")
        if not mobile_lines:
            return True

        dates_service = MobileActivationDateService(
            self.env, crm_lead_line.is_portability()
        )
        introduced_date = dates_service.get_introduced_date()
        activation_date = dates_service.get_activation_date()

        for line in mobile_lines:
            UnblockMobilePackTicket(
                line.ticket_number,
                activation_date=str(activation_date),
                introduced_date=str(introduced_date),
            ).run()

        mobile_pack_lines = mobile_lines.filtered("is_from_pack")

        for line in mobile_pack_lines:
            SetFiberContractCodeMobileTicket(
                line.ticket_number,
                fiber_contract_code=contract_dict["code"],
            ).run()

    def _get_related_crm_lead_line(self, contract_dict):
        return (
            self.env["crm.lead.line"]
            .sudo()
            .search([("ticket_number", "=", contract_dict["ticket_number"])])
        )

    def _change_related_mobile_contract_tariff(self, mbl_contract_id, contract_dict):
        pack_mobile_product_id = self.env.ref("somconnexio.TrucadesIllimitades30GBPack")
        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=mbl_contract_id)
            .sudo()
            .create(
                {
                    "new_tariff_product_id": pack_mobile_product_id.id,
                    "fiber_contract_to_link": contract_dict["id"],
                    "exceptional_change": True,
                    "otrs_checked": True,
                    "send_notification": False,
                }
            )
        )
        wizard.button_change()
