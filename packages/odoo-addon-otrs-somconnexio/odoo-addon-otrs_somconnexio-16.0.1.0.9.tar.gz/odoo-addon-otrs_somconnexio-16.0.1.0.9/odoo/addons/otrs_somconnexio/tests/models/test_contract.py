from mock import Mock, patch, call

from datetime import timedelta, date

from ..helpers import (
    FakeOTRSTicket,
)
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.helpers.date import date_to_str

from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)


class TestContract(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]

    @patch(
        "odoo.addons.otrs_somconnexio.models.contract.ActivateChangeTariffMobileTickets"  # noqa
    )
    @patch("odoo.addons.otrs_somconnexio.models.contract.SearchTicketsService")
    def test_contract_cron_execute_OTRS_tariff_change_tickets(
        self, MockSearchService, MocActivateOTRSTickets, *args
    ):
        ticket_1 = FakeOTRSTicket()
        ticket_2 = FakeOTRSTicket()
        ticket_3 = FakeOTRSTicket()

        CT_tickets = [ticket_1, ticket_2]
        SB_tickets = [ticket_3]

        mock_CT_tickets_service = Mock(spec=["search"])
        mock_CT_tickets_service.search.return_value = CT_tickets
        mock_SB_tickets_service = Mock(spec=["search"])
        mock_SB_tickets_service.search.return_value = SB_tickets

        def mock_search_service_side_effect(conf):
            if conf == ChangeTariffTicketConfiguration:
                return mock_CT_tickets_service
            elif conf == ChangeTariffSharedBondTicketConfiguration:
                return mock_SB_tickets_service

        MockSearchService.side_effect = mock_search_service_side_effect

        self.Contract.cron_execute_OTRS_tariff_change_tickets()

        mock_SB_tickets_service.search.assert_called_once_with(
            df_dct={"creadorAbonament": "1"}
        )
        mock_CT_tickets_service.search.assert_called_once_with()
        MocActivateOTRSTickets.assert_has_calls(
            [
                call(ticket_1.number),
                call(ticket_2.number),
                call(ticket_3.number),
            ],
            any_order=True,
        )
        self.assertEqual(MocActivateOTRSTickets.return_value.run.call_count, 3)

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ContractMobileTariffChangeWizard.create",  # noqa
        return_value=Mock(spec=["button_change"]),
    )
    def test_break_contracts_in_pack(self, mock_change_tariff_create, *args):
        parent_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        parent_contract.terminate_date = date.today() - timedelta(days=2)
        parent_contract.break_packs()

        mock_change_tariff_create.assert_called_once_with(
            {
                "new_tariff_product_id": self.env.ref(
                    "somconnexio.TrucadesIllimitades5GB"
                ).id,
                "exceptional_change": True,
                "otrs_checked": True,
                "send_notification": False,
                "fiber_contract_to_link": False,
                "start_date": parent_contract.terminate_date,
            }
        )
        mock_change_tariff_create.return_value.button_change.assert_called_once_with()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch("odoo.addons.otrs_somconnexio.services.fiber_contract_to_pack.SearchTicketsService") # noqa
    def test_break_contract_sharing_data_from_2_to_1(
        self, MockSearchTicketsService, MockChangeTariffTicket, *args
    ):
        """
        Contract 1 from 2 sharing contract terminates,
        breaking the sharing bond pack, so the other needs to change
        its tariff to single mobile pack with same fiber.
        """

        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_2"
        )
        contract._compute_contracts_in_pack()
        pack_mobile_product = self.env.ref("somconnexio.TrucadesIllimitades30GBPack")

        # Terminate contract
        terminate_date = date.today() - timedelta(days=2)
        contract.write(
            {
                "date_end": terminate_date,
                "terminate_date": terminate_date,
                "is_terminated": True,
            }
        )
        MockSearchTicketsService.search.return_value = []

        contract.break_packs()

        # Sharing contract automatic change
        MockChangeTariffTicket.assert_called_once_with(
            sharing_contract.partner_id.vat,
            sharing_contract.partner_id.ref,
            {
                "phone_number": sharing_contract.phone_number,
                "new_product_code": pack_mobile_product.default_code,
                "current_product_code": (
                    sharing_contract.current_tariff_product.default_code
                ),
                "effective_date": date_to_str(contract.terminate_date),
                "subscription_email": sharing_contract.email_ids[0].email,
                "language": sharing_contract.partner_id.lang,
                "fiber_linked": sharing_contract.parent_pack_contract_id.code,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    def test_break_contract_sharing_data_from_3_to_2(
        self, MockChangeTariffTicket, *args
    ):
        """
        Contract 1 from 3 sharing contract terminates,
        breaking the sharing bond pack.
        No tariff change otrs tickets are required.
        """

        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_3")

        # Terminate contract
        terminate_date = date.today() - timedelta(days=2)
        contract.write(
            {
                "date_end": terminate_date,
                "terminate_date": terminate_date,
                "is_terminated": True,
            }
        )

        contract.break_packs()

        MockChangeTariffTicket.assert_not_called()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch("odoo.addons.otrs_somconnexio.services.fiber_contract_to_pack.SearchTicketsService") # noqa
    def test_quit_pack_and_update_mobile_tariffs_from_2_to_1(
        self, MockSearchTicketsService, MockChangeTariffTicket, *args
    ):
        """
        Contract 1 from 2 sharing contract changes its tariff,
        quitting the pack, so the other also has its tariff changed.
        """

        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        contract._compute_contracts_in_pack()
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_2"
        )
        pack_mobile_product = self.env.ref("somconnexio.TrucadesIllimitades30GBPack")

        # Tariff change out of pack
        new_tariff_product_id = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        today = date.today()
        new_tariff_line_dct = {
            "name": new_tariff_product_id.name,
            "product_id": new_tariff_product_id.id,
            "date_start": today,
        }
        contract.write(
            {
                "contract_line_ids": [
                    (0, 0, new_tariff_line_dct),
                    (
                        1,
                        contract.current_tariff_contract_line.id,
                        {"date_end": today - timedelta(days=1)},
                    ),
                ]
            }
        )
        MockSearchTicketsService.search.return_value = []
        contract.quit_pack_and_update_mobile_tariffs()

        self.assertFalse(contract.shared_bond_id)
        self.assertFalse(sharing_contract.shared_bond_id)

        # Sharing contract automatic change
        MockChangeTariffTicket.assert_called_once_with(
            sharing_contract.partner_id.vat,
            sharing_contract.partner_id.ref,
            {
                "phone_number": sharing_contract.phone_number,
                "new_product_code": pack_mobile_product.default_code,
                "current_product_code": (
                    sharing_contract.current_tariff_product.default_code
                ),
                "effective_date": date_to_str(today),
                "subscription_email": sharing_contract.email_ids[0].email,
                "language": sharing_contract.partner_id.lang,
                "fiber_linked": sharing_contract.parent_pack_contract_id.code,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()
