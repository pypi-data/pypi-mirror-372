from otrs_somconnexio.services.search_tickets_service import SearchTicketsService
from otrs_somconnexio.services.activate_change_tarriff_mobile_tickets import (
    ActivateChangeTariffMobileTickets,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)
from odoo import api, models, fields


class Contract(models.Model):
    _inherit = "contract.contract"

    ticket_number = fields.Char(string="Ticket Number")

    def _get_crm_lead_line_id(self, values):
        # TODO Rise error if exists more than one crm_lead_line
        # with the same ticket_number
        result = super()._get_crm_lead_line_id(values)
        if result:
            return result
        ticket_number = values.get("ticket_number")
        if not ticket_number:
            return
        return (
            self.env["crm.lead.line"]
            .search([("ticket_number", "=", ticket_number)], limit=1)
            .id
        )

    @api.model
    def cron_execute_OTRS_tariff_change_tickets(self):
        """
        Get all Change Tariff tickets from OTRS and trigger them to be sent to MM
        """
        service = SearchTicketsService(ChangeTariffTicketConfiguration)
        change_tariff_tickets = service.search()
        sb_service = SearchTicketsService(ChangeTariffSharedBondTicketConfiguration)
        shared_bond_tickets = sb_service.search(df_dct={"creadorAbonament": "1"})
        for ticket in change_tariff_tickets + shared_bond_tickets:
            ActivateChangeTariffMobileTickets(ticket.number).run()

    def _create_change_tariff_ticket(
        self, new_product, fiber_contract_id=False, start_date=None
    ):
        """Create CRMLead for the mobile with another product"""
        self.ensure_one()

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.id)
            .sudo()
            .create(
                {
                    "new_tariff_product_id": new_product.id,
                    "exceptional_change": True,
                    "otrs_checked": True,
                    "send_notification": False,
                    "fiber_contract_to_link": fiber_contract_id,
                    "start_date": start_date,
                }
            )
        )
        wizard.button_change()

    def quit_pack_and_update_mobile_tariffs(self):
        """
        Update the mobile tariff of mobile left from pack
        """
        mbl_pack_contracts = self.contracts_in_pack.filtered("is_mobile") - self

        if len(mbl_pack_contracts) == 1:
            # Single mobile pack product correspondance can not be computed by getting
            # variants, since the Data attributes do not mach, so it is hardcoded here

            contract = mbl_pack_contracts[0]
            current_product = contract.current_tariff_product
            company_pt_attr = self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", current_product.product_tmpl_id.id),
                    (
                        "product_attribute_value_id",
                        "=",
                        self.env.ref("somconnexio.CompanyExclusive").id,
                    ),
                ]
            )

            if company_pt_attr in current_product.product_template_attribute_value_ids:
                new_product = self.env.ref("somconnexio.TrucadesIllimitades50GBPackEiE")
            else:
                new_product = self.env.ref("somconnexio.TrucadesIllimitades30GBPack")

            contract._create_change_tariff_ticket(
                new_product,
                fiber_contract_id=contract.parent_pack_contract_id.id,
                start_date=self.terminate_date,
            )
        super().quit_pack_and_update_mobile_tariffs()

    def break_packs(self):
        if self.is_fiber:
            for contract in self.children_pack_contract_ids:
                new_product = self.env.ref("somconnexio.TrucadesIllimitades5GB")
                contract._create_change_tariff_ticket(
                    new_product, start_date=self.terminate_date
                )
        super().break_packs()

    def _to_dict(self):
        self.ensure_one()

        contract_dict = super()._to_dict()
        contract_dict.update(
            {
                "ticket_number": self.ticket_number,
            }
        )
        return contract_dict
