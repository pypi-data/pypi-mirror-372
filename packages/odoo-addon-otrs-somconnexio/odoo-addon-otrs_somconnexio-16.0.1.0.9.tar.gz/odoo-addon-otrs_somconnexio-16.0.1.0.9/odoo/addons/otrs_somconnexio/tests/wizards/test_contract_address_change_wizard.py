from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.asociatel_fiber import AsociatelFiberCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fiber import MMFiberCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fiber import OrangeFiberCoverage

from odoo.tests.common import TransactionCase


class TestContractAddressChangeWizard(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.env.ref("somconnexio.res_partner_1_demo")
        self.contract = self.env.ref("somconnexio.contract_fibra_600")

    def test_wizard_address_change_ok(self):
        wizard = (
            self.env["contract.address.change.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "partner_bank_id": self.partner.bank_ids.id,
                    "service_street": "Carrer Nou 123",
                    "service_street2": "Principal A",
                    "service_zip_code": "00123",
                    "service_city": "Barcelona",
                    "service_state_id": self.ref("base.state_es_b"),
                    "service_country_id": self.ref("base.es"),
                    "previous_product_id": self.ref("somconnexio.Fibra600Mb"),
                    "product_id": self.ref("somconnexio.Fibra1Gb"),
                    "mm_fiber_coverage": MMFiberCoverage.VALUES[2][0],
                    "asociatel_fiber_coverage": AsociatelFiberCoverage.VALUES[1][0],
                    "orange_fiber_coverage": OrangeFiberCoverage.VALUES[1][0],
                    "adsl_coverage": ADSLCoverage.VALUES[6][0],
                    "notes": "This is a random note",
                }
            )
        )
        crm_lead_action = wizard.button_change()

        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            crm_lead_line.broadband_isp_info.adsl_coverage, ADSLCoverage.VALUES[6][0]
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.asociatel_fiber_coverage,
            AsociatelFiberCoverage.VALUES[1][0],
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.mm_fiber_coverage,
            MMFiberCoverage.VALUES[2][0],
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.orange_fiber_coverage,
            OrangeFiberCoverage.VALUES[1][0],
        )
