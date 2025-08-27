from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.asociatel_fiber import AsociatelFiberCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fiber import MMFiberCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fiber import VdfFiberCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fiber import OrangeFiberCoverage

from odoo.addons.somconnexio.tests.helper_service import crm_lead_create
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase

from ...otrs_factories.router_4G_data_from_crm_lead_line import (
    Router4GDataFromCRMLeadLine,
)


class Router4GDataFromCRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

    def test_build(self):
        ba_crm_lead = crm_lead_create(self.env, self.partner_id, "4G")
        crm_lead_line = ba_crm_lead.lead_line_ids[0]
        broadband_isp_info = crm_lead_line.broadband_isp_info

        router_4G_data = Router4GDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(router_4G_data.order_id, crm_lead_line.id)
        self.assertEqual(router_4G_data.technology, "4G")
        self.assertEqual(router_4G_data.sales_team, ba_crm_lead.team_id.name)
        self.assertEqual(router_4G_data.phone_number, "-")
        self.assertEqual(
            router_4G_data.service_address, broadband_isp_info.service_full_street
        )
        self.assertEqual(router_4G_data.service_city, broadband_isp_info.service_city)
        self.assertEqual(
            router_4G_data.service_zip, broadband_isp_info.service_zip_code
        )
        self.assertEqual(
            router_4G_data.service_subdivision, broadband_isp_info.service_state_id.name
        )
        self.assertEqual(router_4G_data.service_subdivision_code, "B")
        self.assertEqual(
            router_4G_data.shipment_address, broadband_isp_info.delivery_full_street
        )
        self.assertEqual(router_4G_data.shipment_city, broadband_isp_info.delivery_city)
        self.assertEqual(
            router_4G_data.shipment_zip, broadband_isp_info.delivery_zip_code
        )
        self.assertEqual(
            router_4G_data.shipment_subdivision,
            broadband_isp_info.delivery_state_id.name,
        )
        self.assertEqual(router_4G_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(router_4G_data.iban, crm_lead_line.iban)
        self.assertEqual(router_4G_data.email, crm_lead_line.lead_id.email_from)
        self.assertEqual(router_4G_data.product, crm_lead_line.product_id.default_code)
        self.assertEqual(
            router_4G_data.shipment_address, broadband_isp_info.delivery_full_street
        )
        self.assertEqual(router_4G_data.shipment_city, broadband_isp_info.delivery_city)
        self.assertEqual(
            router_4G_data.shipment_zip, broadband_isp_info.delivery_zip_code
        )
        self.assertEqual(
            router_4G_data.shipment_subdivision,
            broadband_isp_info.delivery_state_id.name,
        )

    def test_change_address_build(self):
        service_supplier = self.browse_ref("somconnexio.service_supplier_vodafone")
        ba_crm_lead = crm_lead_create(self.env, self.partner_id, "4G", portability=True)
        crm_lead_line = ba_crm_lead.lead_line_ids[0]
        broadband_isp_info = crm_lead_line.broadband_isp_info
        broadband_isp_info.write(
            {
                "type": "location_change",
                "service_supplier_id": service_supplier.id,
                "mm_fiber_coverage": MMFiberCoverage.VALUES[2][0],
                "asociatel_fiber_coverage": AsociatelFiberCoverage.VALUES[1][0],
                "vdf_fiber_coverage": VdfFiberCoverage.VALUES[3][0],
                "orange_fiber_coverage": OrangeFiberCoverage.VALUES[1][0],
                "adsl_coverage": ADSLCoverage.VALUES[6][0],
                "previous_contract_phone": "966666666",
                "previous_contract_address": "Calle Teper",
            }
        )

        router_4G_data = Router4GDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(
            router_4G_data.previous_internal_provider, service_supplier.ref
        )
        self.assertEqual(router_4G_data.mm_fiber_coverage, MMFiberCoverage.VALUES[2][0])
        self.assertEqual(
            router_4G_data.asociatel_fiber_coverage, AsociatelFiberCoverage.VALUES[1][0]
        )
        self.assertEqual(
            router_4G_data.orange_fiber_coverage, OrangeFiberCoverage.VALUES[1][0]
        )
        self.assertEqual(router_4G_data.adsl_coverage, ADSLCoverage.VALUES[6][0])
        self.assertEqual(router_4G_data.previous_contract_phone, "966666666")
        self.assertEqual(router_4G_data.previous_contract_address, "Calle Teper")
        self.assertEqual(router_4G_data.type, "location_change")
