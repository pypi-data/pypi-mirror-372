from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.helper_service import crm_lead_create

from ...otrs_factories.mobile_data_from_crm_lead_line import MobileDataFromCRMLeadLine


class MobileDataFromCRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

    def test_build(self):
        activation_notes = "<p>Mbl activation notes to consider</p>"

        mbl_crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")
        # TODO: Remove correos reference from tracking code
        mbl_crm_lead.correos_tracking_code = "XYZ54321"
        crm_lead_line = mbl_crm_lead.lead_line_ids[0]
        crm_lead_line.notes = activation_notes
        mobile_isp_info = crm_lead_line.mobile_isp_info
        mobile_isp_info.shared_bond_id = "AAA"

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(mobile_data.type, mobile_isp_info.type)
        self.assertEqual(mobile_data.order_id, crm_lead_line.id)
        self.assertEqual(mobile_data.technology, "Mobil")
        self.assertEqual(mobile_data.sales_team, crm_lead_line.lead_id.team_id.name)
        self.assertEqual(mobile_data.iban, crm_lead_line.iban)
        self.assertEqual(mobile_data.email, crm_lead_line.lead_id.email_from)
        self.assertEqual(mobile_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(mobile_data.activation_notes, activation_notes)
        self.assertEqual(mobile_data.product, crm_lead_line.product_id.default_code)
        self.assertEqual(mobile_data.delivery_street, mobile_isp_info.delivery_street)
        self.assertEqual(mobile_data.delivery_city, mobile_isp_info.delivery_city)
        self.assertEqual(
            mobile_data.delivery_zip_code, mobile_isp_info.delivery_zip_code
        )
        self.assertEqual(
            mobile_data.delivery_state, mobile_isp_info.delivery_state_id.name
        )
        self.assertEqual(
            mobile_data.sim_delivery_tracking_code, mbl_crm_lead.correos_tracking_code
        )
        self.assertEqual(mobile_data.shared_bond_id, mobile_isp_info.shared_bond_id)
        self.assertFalse(mobile_data.is_grouped_with_fiber)
        self.assertFalse(mobile_data.fiber_linked)

    def test_portability_build(self):
        mbl_crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )

        crm_lead_line = mbl_crm_lead.lead_line_ids[0]
        mobile_isp_info = crm_lead_line.mobile_isp_info
        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(mobile_data.type, mobile_isp_info.type)
        self.assertEqual(mobile_data.phone_number, mobile_isp_info.phone_number)
        self.assertEqual(
            mobile_data.previous_owner_vat, mobile_isp_info.previous_owner_vat_number
        )
        self.assertEqual(
            mobile_data.previous_owner_name, mobile_isp_info.previous_owner_first_name
        )
        self.assertEqual(
            mobile_data.previous_owner_surname, mobile_isp_info.previous_owner_name
        )
        self.assertEqual(
            mobile_data.previous_provider, mobile_isp_info.previous_provider.code
        )
        self.assertEqual(mobile_data.sc_icc, mobile_isp_info.icc)
        self.assertEqual(mobile_data.icc, mobile_isp_info.icc_donor)
        self.assertFalse(mobile_data.is_grouped_with_fiber)
        self.assertFalse(mobile_data.sim_delivery_tracking_code)
        self.assertFalse(mobile_data.is_from_pack)

    def test_has_lead_fiber_service_actual_pack(self):
        pack_crm_lead = crm_lead_create(
            self.env,
            self.partner_id,
            "pack",
        )

        mbl_pack_lead_line = pack_crm_lead.lead_line_ids.filtered(
            lambda line: line.is_mobile
        )

        mobile_data_pack_line = MobileDataFromCRMLeadLine(mbl_pack_lead_line).build()

        self.assertTrue(mobile_data_pack_line.is_grouped_with_fiber)
        self.assertTrue(mobile_data_pack_line.is_from_pack)
        self.assertEqual(mobile_data_pack_line.technology, "Mixta")

    def test_has_lead_fiber_service(self):
        fiber_crm_lead = crm_lead_create(
            self.env,
            self.partner_id,
            "fiber",
        )

        mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "new",
                "delivery_street": "Carrer Nogal",
                "delivery_zip_code": "08008",
                "delivery_city": "Barcelona",
                "delivery_state_id": self.ref("base.state_es_b"),
            }
        )
        extra_mbl_lead_line = self.env["crm.lead.line"].create(
            {
                "name": "New CRMLeadLine",
                "product_id": self.ref("somconnexio.150Min1GB"),
                "mobile_isp_info": mobile_isp_info.id,
                "broadband_isp_info": None,
            }
        )

        fiber_crm_lead.write({"lead_line_ids": [(4, extra_mbl_lead_line.id, False)]})

        mobile_data_with_fiber_lead = MobileDataFromCRMLeadLine(
            extra_mbl_lead_line
        ).build()

        self.assertTrue(mobile_data_with_fiber_lead.is_grouped_with_fiber)
        self.assertEqual(mobile_data_with_fiber_lead.technology, "Mixta")

    def test_linked_fiber_contract_id(self):
        # Create fiber contract reference
        vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": "954321123",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
            }
        )
        contract_fiber_args = {
            "name": "Contract w/service technology to fiber",
            "service_technology_id": self.ref("somconnexio.service_technology_fiber"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_vodafone"),
            "vodafone_fiber_service_contract_info_id": (
                vodafone_fiber_contract_service_info.id
            ),
            "partner_id": self.partner_id.id,
            "service_partner_id": self.partner_id.id,
            "invoice_partner_id": self.partner_id.id,
        }
        fiber_contract = self.env["contract.contract"].create(contract_fiber_args)

        mbl_crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")

        crm_lead_line = mbl_crm_lead.lead_line_ids[0]
        mobile_isp_info = crm_lead_line.mobile_isp_info
        mobile_isp_info.write({"linked_fiber_contract_id": fiber_contract.id})

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(mobile_data.fiber_linked, fiber_contract.code)
