from mock import Mock, call, patch
from odoo.exceptions import MissingError, ValidationError
from odoo.addons.somconnexio.tests.helper_service import (
    crm_lead_create,
    random_icc,
    random_mobile_phone,
)
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TicketMock:
    def __init__(self, tid):
        self.tid = tid


class CRMLeadTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        self.partner_bank = self.env.ref("somconnexio.demo_bank_id_partner_2_demo")
        self.product_mobile = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        self.mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "new",
                "icc": random_icc(self.env),
                "phone_number": random_mobile_phone(),
            }
        )

        self.mobile_lead_line_vals = {
            "name": "TEST",
            "product_id": self.product_mobile.id,
            "mobile_isp_info": self.mobile_isp_info.id,
            "iban": self.partner_bank.sanitized_acc_number,
        }

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_pack_tickets_ok(self, MockOTRSClient):
        fiber_ticket = TicketMock(1234)
        fiber_ticket_number = "23828"
        mobile_ticket = TicketMock(2345)
        mobile_ticket_number = "442352"
        mobile_ticket_2 = TicketMock(6789)
        mobile_ticket_2_number = "253244"
        self.mobile_lead_line_vals.update(
            {
                "ticket_number": mobile_ticket_2_number,
            }
        )
        # Add ticket numbers to pack_crm_lead
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )
        pack_crm_lead.broadband_lead_line_ids[0].ticket_number = fiber_ticket_number
        pack_crm_lead.mobile_lead_line_ids[0].ticket_number = mobile_ticket_number

        # add one mobile lead line with ticket number
        pack_crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        MockOTRSClient.return_value = Mock(
            spec=["get_ticket_by_number", "link_tickets"]
        )

        def side_effect_ticket_get(ticket_number):
            if ticket_number == fiber_ticket_number:
                return fiber_ticket
            elif ticket_number == mobile_ticket_number:
                return mobile_ticket
            elif ticket_number == mobile_ticket_2_number:
                return mobile_ticket_2

        MockOTRSClient.return_value.get_ticket_by_number.side_effect = (
            side_effect_ticket_get
        )
        pack_crm_lead.link_pack_tickets()

        MockOTRSClient.return_value.link_tickets.assert_has_calls(
            [
                call(fiber_ticket.tid, mobile_ticket.tid, link_type="ParentChild"),
                call(fiber_ticket.tid, mobile_ticket_2.tid, link_type="ParentChild"),
            ],
            any_order=True,
        )

    @patch(
        "odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient",
        return_value=Mock(spec=["get_ticket_by_number", "link_tickets"]),
    )
    def test_link_pack_tickets_without_ticket_number(self, _):
        # No ticket numbers by default
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )

        self.assertRaisesRegex(
            MissingError,
            "Either mobile or fiber ticket numbers where not found "
            "among the lines of this pack CRMLead",
            pack_crm_lead.link_pack_tickets,
        )

    @patch(
        "odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient",
        return_value=Mock(spec=["get_ticket_by_number", "link_tickets"]),
    )
    def test_link_pack_tickets_one_ticket_without_ticket_number(self, _):
        self.mobile_lead_line_vals.update(
            {
                "ticket_number": "8888822",
            }
        )
        # No ticket numbers by default
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )

        # add one mobile lead line with ticket number
        pack_crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        self.assertRaisesRegex(
            MissingError,
            "Either mobile or fiber ticket numbers where not found "
            "among the lines of this pack CRMLead",
            pack_crm_lead.link_pack_tickets,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_pack_tickets_ticket_not_found(self, MockOTRSClient):
        fiber_ticket = TicketMock(1234)
        fiber_ticket_number = "23828"
        mobile_ticket_number = "442352"

        # Add ticket numbers to pack_crm_lead
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )
        pack_crm_lead.broadband_lead_line_ids[0].ticket_number = fiber_ticket_number
        pack_crm_lead.mobile_lead_line_ids[0].ticket_number = mobile_ticket_number

        MockOTRSClient.return_value = Mock(
            spec=["get_ticket_by_number", "link_tickets"]
        )

        def side_effect_ticket_get(ticket_number):
            if ticket_number == fiber_ticket_number:
                return fiber_ticket
            elif ticket_number == mobile_ticket_number:
                return False

        MockOTRSClient.return_value.get_ticket_by_number.side_effect = (
            side_effect_ticket_get
        )

        self.assertRaisesRegex(
            MissingError,
            "Mobile tickets not found in OTRS with ticket_numbers {}".format(
                mobile_ticket_number
            ),
            pack_crm_lead.link_pack_tickets,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_pack_tickets_many_tickets_not_found(self, MockOTRSClient):
        fiber_ticket = TicketMock(1234)
        fiber_ticket_number = "23828"
        mobile_ticket_number = "442352"
        mobile_ticket_2_number = "82727"
        self.mobile_lead_line_vals.update(
            {
                "ticket_number": mobile_ticket_2_number,
            }
        )

        # Add ticket numbers to pack_crm_lead
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )
        # add one mobile lead line and set ticket numbers
        pack_crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                    (
                        1,
                        pack_crm_lead.broadband_lead_line_ids[0].id,
                        {"ticket_number": fiber_ticket_number},
                    ),
                    (
                        1,
                        pack_crm_lead.mobile_lead_line_ids[0].id,
                        {"ticket_number": mobile_ticket_number},
                    ),
                ],
            }
        )

        MockOTRSClient.return_value = Mock(
            spec=["get_ticket_by_number", "link_tickets"]
        )

        def side_effect_ticket_get(ticket_number):
            if ticket_number == fiber_ticket_number:
                return fiber_ticket
            elif ticket_number == mobile_ticket_number:
                return False
            elif ticket_number == mobile_ticket_2_number:
                return False

        MockOTRSClient.return_value.get_ticket_by_number.side_effect = (
            side_effect_ticket_get
        )

        self.assertRaisesRegex(
            MissingError,
            "Mobile tickets not found in OTRS with ticket_numbers {},{}".format(
                mobile_ticket_number, mobile_ticket_2_number
            ),
            pack_crm_lead.link_pack_tickets,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_mobile_tickets_in_pack_2(self, MockOTRSClient):
        mobile_ticket = TicketMock(1234)
        mobile_ticket_2 = TicketMock(5678)
        mobile_ticket_number = "442352"
        mobile_ticket_2_number = "82727"

        shared_data_crm_lead = crm_lead_create(
            self.env, self.partner_id, "shared_data", portability=True
        )

        # Remove fiber and add mobile ticket numbers
        shared_data_crm_lead.write(
            {
                "lead_line_ids": [
                    (3, shared_data_crm_lead.broadband_lead_line_ids[0].id, 0),
                    (
                        1,
                        shared_data_crm_lead.mobile_lead_line_ids[0].id,
                        {"ticket_number": mobile_ticket_number},
                    ),
                    (
                        1,
                        shared_data_crm_lead.mobile_lead_line_ids[1].id,
                        {"ticket_number": mobile_ticket_2_number},
                    ),
                ],
            }
        )
        MockOTRSClient.return_value = Mock(
            spec=["get_ticket_by_number", "link_tickets"]
        )

        def side_effect_ticket_get(ticket_number):
            if ticket_number == mobile_ticket_number:
                return mobile_ticket
            elif ticket_number == mobile_ticket_2_number:
                return mobile_ticket_2

        MockOTRSClient.return_value.get_ticket_by_number.side_effect = (
            side_effect_ticket_get
        )

        shared_data_crm_lead.link_mobile_tickets_in_pack()

        MockOTRSClient.return_value.link_tickets.assert_has_calls(
            [
                call(mobile_ticket.tid, mobile_ticket_2.tid, link_type="Normal"),
            ],
            any_order=True,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_mobile_tickets_in_pack_3(self, MockOTRSClient):
        mobile_ticket = TicketMock(1234)
        mobile_ticket_2 = TicketMock(5678)
        mobile_ticket_3 = TicketMock(8765)
        mobile_ticket_number = "442352"
        mobile_ticket_2_number = "82727"
        mobile_ticket_3_number = "82828"
        product_shared_bond_3 = self.env.ref("somconnexio.50GBCompartides3mobils")
        self.mobile_lead_line_vals.update(
            {
                "ticket_number": mobile_ticket_3_number,
                "product_id": product_shared_bond_3.id,
            }
        )
        shared_data_crm_lead = crm_lead_create(
            self.env, self.partner_id, "shared_data", portability=True
        )

        # Remove fiber, add ticket numbers, add new sharing mobile,
        shared_data_crm_lead.write(
            {
                "lead_line_ids": [
                    (3, shared_data_crm_lead.broadband_lead_line_ids[0].id, 0),
                    (
                        1,
                        shared_data_crm_lead.mobile_lead_line_ids[0].id,
                        {"ticket_number": mobile_ticket_number},
                    ),
                    (
                        1,
                        shared_data_crm_lead.mobile_lead_line_ids[1].id,
                        {"ticket_number": mobile_ticket_2_number},
                    ),
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        MockOTRSClient.return_value = Mock(
            spec=["get_ticket_by_number", "link_tickets"]
        )

        def side_effect_ticket_get(ticket_number):
            if ticket_number == mobile_ticket_number:
                return mobile_ticket
            elif ticket_number == mobile_ticket_2_number:
                return mobile_ticket_2
            elif ticket_number == mobile_ticket_3_number:
                return mobile_ticket_3

        MockOTRSClient.return_value.get_ticket_by_number.side_effect = (
            side_effect_ticket_get
        )

        shared_data_crm_lead.link_mobile_tickets_in_pack()

        MockOTRSClient.return_value.link_tickets.assert_has_calls(
            [
                call(mobile_ticket.tid, mobile_ticket_2.tid, link_type="Normal"),
                call(mobile_ticket.tid, mobile_ticket_3.tid, link_type="Normal"),
                call(mobile_ticket_2.tid, mobile_ticket_3.tid, link_type="Normal"),
            ],
            any_order=True,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_mobile_tickets_in_pack_single(self, MockOTRSClient):
        shared_crm_lead = crm_lead_create(
            self.env, self.partner_id, "shared_data", portability=True
        )

        # Remove one sharing mobile
        shared_crm_lead.write(
            {
                "lead_line_ids": [
                    (3, shared_crm_lead.mobile_lead_line_ids[0].id, 0),
                ],
            }
        )

        self.assertEqual(len(shared_crm_lead.mobile_lead_line_ids), 1)
        self.assertRaisesRegex(
            ValidationError,
            "We cannot build packs with <2 or >3 mobiles",
            shared_crm_lead.link_mobile_tickets_in_pack,
        )

    @patch("odoo.addons.otrs_somconnexio.models.crm_lead.OTRSClient")
    def test_link_mobile_tickets_in_pack_4(self, MockOTRSClient):
        product_shared_bond_3 = self.env.ref("somconnexio.50GBCompartides3mobils")
        self.mobile_lead_line_vals.update({"product_id": product_shared_bond_3.id})

        shared_crm_lead = crm_lead_create(
            self.env, self.partner_id, "shared_data", portability=True
        )

        # Add two more sharing mobiles
        shared_crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        self.assertEqual(len(shared_crm_lead.mobile_lead_line_ids), 4)
        self.assertRaisesRegex(
            ValidationError,
            "We cannot build packs with <2 or >3 mobiles",
            shared_crm_lead.link_mobile_tickets_in_pack,
        )
