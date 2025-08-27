from mock import Mock, patch
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractGetFiberContractsNotPackedService(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.FiberContractsToPack = self.env["fiber.contract.to.pack.service"]
        self.fiber_contract_1 = self.env.ref("somconnexio.contract_fibra_600")
        self.fiber_contract_2 = self.env.ref("somconnexio.contract_fibra_600_pack")
        self.fiber_contract_3 = self.env.ref("somconnexio.contract_fibra_600_shared")

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService._filter_already_used_contracts"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.fiber_contract_to_pack.FiberContractToPackService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    def test_filter_already_used_contracts(
        self, mock_filter_OTRS_tickets, mock_filter_sc_already_used_contracts
    ):
        """
        Test that the method _filter_already_used_contracts calls the original one
        and then filters out the contracts that are already used in OTRS tickets
        """
        original_contracts = (
            self.fiber_contract_1 + self.fiber_contract_2 + self.fiber_contract_3
        )

        mock_filter_sc_already_used_contracts.return_value = (
            self.fiber_contract_1 + self.fiber_contract_2
        )
        mock_filter_OTRS_tickets.return_value = self.fiber_contract_1

        result = self.FiberContractsToPack._filter_already_used_contracts(
            original_contracts
        )

        self.assertEqual(result, self.fiber_contract_1)
        mock_filter_sc_already_used_contracts.assert_called_once_with(
            original_contracts
        )
        mock_filter_OTRS_tickets.assert_called_once_with(
            self.fiber_contract_1 + self.fiber_contract_2
        )

    @patch(
        "odoo.addons.otrs_somconnexio.services.fiber_contract_to_pack.SearchTicketsService",  # noqa
        return_value=Mock(spec=["search"]),
    )
    def test_filter_out_fibers_used_in_OTRS_tickets(self, MockSearchTicketsService):
        """
        Test that the method _filter_out_fibers_used_in_OTRS_tickets filters out
        the contracts with their code found in the DF OdooContractRefRelacionat
        of their partner's Tickets in OTRS, through an OTRS service SearchTicketsService
        """

        expected_dct = {
            "OdooContractRefRelacionat": [
                self.fiber_contract_1.code,
                self.fiber_contract_2.code,
            ]
        }

        mock_ticket = Mock(spec=["fiber_contract_code"])
        mock_ticket.fiber_contract_code = self.fiber_contract_2.code

        MockSearchTicketsService.return_value.search.return_value = [mock_ticket]

        result = self.FiberContractsToPack._filter_out_fibers_used_in_OTRS_tickets(
            self.fiber_contract_1 + self.fiber_contract_2
        )

        MockSearchTicketsService.assert_called_once_with(
            [
                ChangeTariffTicketConfiguration,
                ChangeTariffSharedBondTicketConfiguration,
            ]
        )
        MockSearchTicketsService.return_value.search.assert_called_once_with(
            self.fiber_contract_1.partner_id.ref, df_dct=expected_dct
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result, self.fiber_contract_1)

    def test_filter_out_fibers_used_in_OTRS_tickets_empty(self):
        result = self.FiberContractsToPack._filter_out_fibers_used_in_OTRS_tickets([])

        self.assertFalse(result)
