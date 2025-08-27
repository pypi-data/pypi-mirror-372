from odoo import models
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)
from otrs_somconnexio.services.search_tickets_service import SearchTicketsService


class FiberContractToPackService(models.AbstractModel):
    _inherit = "fiber.contract.to.pack.service"

    def _filter_already_used_contracts(self, contracts):
        contracts = super()._filter_already_used_contracts(contracts)
        contracts = self._filter_out_fibers_used_in_OTRS_tickets(contracts)
        return contracts

    def _filter_out_fibers_used_in_OTRS_tickets(self, contracts):
        """
        From a list of fiber contracts, search if any of their codes are
        already referenced in OTRS new mobile change tariff tickets
        (DF OdooContractRefRelacionat).
        If so, that fiber contract is about to be linked to a mobile offer,
        and shouldn't be available for others.
        Returns the original contract list excluding, if found,
        those referenced in OTRS.
        """

        if not contracts:
            return []

        partner = contracts[0].partner_id
        service = SearchTicketsService(
            [
                ChangeTariffTicketConfiguration,
                ChangeTariffSharedBondTicketConfiguration,
            ]
        )
        df_dct = {"OdooContractRefRelacionat": [c.code for c in contracts]}
        tickets_found = service.search(partner.ref, df_dct=df_dct)

        fiber_contracts_used_otrs = []
        for ticket in tickets_found:
            code = ticket.fiber_contract_code
            fiber_contracts_used_otrs.append(code)

        return contracts.filtered(lambda c: c.code not in fiber_contracts_used_otrs)
