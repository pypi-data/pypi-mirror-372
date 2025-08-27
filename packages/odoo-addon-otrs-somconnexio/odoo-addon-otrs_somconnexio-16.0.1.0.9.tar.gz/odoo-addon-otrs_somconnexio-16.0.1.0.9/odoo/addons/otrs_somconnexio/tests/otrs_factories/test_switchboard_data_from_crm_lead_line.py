from odoo.addons.switchboard_somconnexio.tests.helper_service import crm_lead_create
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase

from ...otrs_factories.switchboard_data_from_crm_lead_line import (
    SwitchboardDataFromCRMLeadLine,
)


class SwitchboardDataFromCRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.tecnology = self.env.ref(
            "switchboard_somconnexio.service_technology_switchboard"
        )

    def test_build(self):
        sb_crm_lead = crm_lead_create(self.env, self.partner_id, "switchboard")
        crm_lead_line = sb_crm_lead.lead_line_ids[0]
        switchboard_isp_info = crm_lead_line.switchboard_isp_info

        switchboard_data = SwitchboardDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(
            switchboard_data.technology,
            self.tecnology.name,
        )
        self.assertEqual(
            switchboard_data.type,
            switchboard_isp_info.type,
        )
        self.assertEqual(
            switchboard_data.icc,
            switchboard_isp_info.icc,
        )
        self.assertEqual(
            switchboard_data.has_sim,
            switchboard_isp_info.has_sim,
        )
        self.assertEqual(
            switchboard_data.extension,
            switchboard_isp_info.extension,
        )
        self.assertEqual(
            switchboard_data.landline,
            switchboard_isp_info.phone_number,
        )
        self.assertEqual(
            switchboard_data.landline_2,
            switchboard_isp_info.phone_number_2,
        )
        self.assertEqual(
            switchboard_data.agent_name,
            switchboard_isp_info.agent_name,
        )
        self.assertEqual(
            switchboard_data.agent_email,
            switchboard_isp_info.agent_email,
        )
        self.assertEqual(
            switchboard_data.shipment_address,
            switchboard_isp_info.delivery_full_street,
        )
        self.assertEqual(
            switchboard_data.shipment_city,
            switchboard_isp_info.delivery_city,
        )
        self.assertEqual(
            switchboard_data.shipment_zip,
            switchboard_isp_info.delivery_zip_code,
        )
        self.assertEqual(
            switchboard_data.shipment_subdivision,
            switchboard_isp_info.delivery_state_id.name,
        )
