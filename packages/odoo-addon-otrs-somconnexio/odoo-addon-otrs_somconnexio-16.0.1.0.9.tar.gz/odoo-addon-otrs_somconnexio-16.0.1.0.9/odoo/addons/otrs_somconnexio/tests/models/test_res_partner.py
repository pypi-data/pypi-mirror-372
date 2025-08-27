from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.helper_service import (
    crm_lead_create,
    contract_fiber_create_data,
)


class TestResPartner(SCTestCase):
    def test_has_active_provisioning(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner.has_lead_in_provisioning)
        crm_lead_id = (
            self.env["crm.lead"]
            .create(
                [
                    {
                        "name": "Test Lead",
                        "partner_id": partner.id,
                    }
                ]
            )[0]
            .id
        )
        broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "phone_number": "666666666",
                "type": "new",
            }
        )
        broadband_adsl_product_tmpl_args = {
            "name": "ADSL 20Mb",
            "type": "service",
            "categ_id": self.ref("somconnexio.broadband_adsl_service"),
        }
        product_adsl_broadband_tmpl = self.env["product.template"].create(
            broadband_adsl_product_tmpl_args
        )
        product_broadband_adsl = product_adsl_broadband_tmpl.product_variant_id

        ticket_number = "1234"
        crm_lead_line_args = {
            "lead_id": crm_lead_id,
            "broadband_isp_info": broadband_isp_info.id,
            "product_id": product_broadband_adsl.id,
            "name": "666666666",
        }
        crm_lead_line = self.env["crm.lead.line"].create([crm_lead_line_args])
        self.assertTrue(partner.has_lead_in_provisioning)
        crm_lead_line.write({"ticket_number": ticket_number})
        vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": "654321123",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
            }
        )
        service_partner = self.env["res.partner"].create(
            {"parent_id": partner.id, "name": "Service partner", "type": "service"}
        )
        partner_id = partner.id
        vals_contract = {
            "code": 1234,
            "name": "Test Contract Broadband",
            "partner_id": partner_id,
            "service_partner_id": service_partner.id,
            "invoice_partner_id": partner_id,
            "service_technology_id": self.ref("somconnexio.service_technology_fiber"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_vodafone"),
            "vodafone_fiber_service_contract_info_id": (
                vodafone_fiber_contract_service_info.id
            ),
            "ticket_number": ticket_number,
        }
        self.env["contract.contract"].create(vals_contract)
        self.assertFalse(partner.has_lead_in_provisioning)

    def test_has_active_provisioning_many_leads(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner.has_lead_in_provisioning)
        crm_lead = crm_lead_create(self.env, partner, "adsl")
        other_crm_lead = crm_lead_create(self.env, partner, "adsl")
        ticket_number = "1234"
        other_ticket_number = "5678"
        crm_lead.lead_line_ids[0].write(
            {
                "ticket_number": ticket_number,
            }
        )
        other_crm_lead.lead_line_ids[0].write(
            {
                "ticket_number": other_ticket_number,
            }
        )

        self.assertTrue(partner.has_lead_in_provisioning)
        contract = self.env.ref("somconnexio.contract_adsl")
        contract.write(
            {
                "ticket_number": ticket_number,
            }
        )
        self.assertTrue(partner.has_lead_in_provisioning)

    def test_has_active_provisioning_many_contracts(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner.has_lead_in_provisioning)
        crm_lead_id = (
            self.env["crm.lead"]
            .create(
                [
                    {
                        "name": "Test Lead",
                        "partner_id": partner.id,
                    }
                ]
            )[0]
            .id
        )
        broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "phone_number": "666666666",
                "type": "new",
            }
        )
        broadband_adsl_product_tmpl_args = {
            "name": "ADSL 20Mb",
            "type": "service",
            "categ_id": self.ref("somconnexio.broadband_adsl_service"),
        }
        product_adsl_broadband_tmpl = self.env["product.template"].create(
            broadband_adsl_product_tmpl_args
        )
        product_broadband_adsl = product_adsl_broadband_tmpl.product_variant_id

        ticket_number = "1234"
        other_ticket_number = "5678"
        crm_lead_line_args = {
            "lead_id": crm_lead_id,
            "broadband_isp_info": broadband_isp_info.id,
            "product_id": product_broadband_adsl.id,
            "name": "666666666",
            "ticket_number": ticket_number,
        }
        self.env["crm.lead.line"].create([crm_lead_line_args])
        self.assertTrue(partner.has_lead_in_provisioning)
        vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": "654321123",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
            }
        )
        service_partner = self.env["res.partner"].create(
            {"parent_id": partner.id, "name": "Service partner", "type": "service"}
        )
        partner_id = partner.id
        vals_contract = {
            "code": 1234,
            "name": "Test Contract Broadband",
            "partner_id": partner_id,
            "service_partner_id": service_partner.id,
            "invoice_partner_id": partner_id,
            "service_technology_id": self.ref("somconnexio.service_technology_fiber"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_vodafone"),
            "vodafone_fiber_service_contract_info_id": (
                vodafone_fiber_contract_service_info.id
            ),
            "ticket_number": ticket_number,
        }
        other_vals_contract = vals_contract.copy()
        other_vals_contract.update({"code": 5678, "ticket_number": other_ticket_number})
        self.env["contract.contract"].create(vals_contract)
        self.assertFalse(partner.has_lead_in_provisioning)

    def test_has_active_provisioning_many_contracts_many_leads_match(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner.has_lead_in_provisioning)
        crm_lead = crm_lead_create(self.env, partner, "adsl")
        other_crm_lead = crm_lead_create(self.env, partner, "adsl")
        ticket_number = "1234"
        other_ticket_number = "5678"
        crm_lead.lead_line_ids[0].write(
            {
                "ticket_number": ticket_number,
            }
        )
        other_crm_lead.lead_line_ids[0].write(
            {
                "ticket_number": other_ticket_number,
            }
        )

        self.assertTrue(partner.has_lead_in_provisioning)
        vals_contract = contract_fiber_create_data(self.env, partner)
        vals_contract.update({"code": 1234, "ticket_number": ticket_number})
        other_vals_contract = vals_contract.copy()
        other_vals_contract.update({"code": 5678, "ticket_number": other_ticket_number})
        self.env["contract.contract"].create(vals_contract)
        self.env["contract.contract"].create(other_vals_contract)
        self.assertFalse(partner.has_lead_in_provisioning)
