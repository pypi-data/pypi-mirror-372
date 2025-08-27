from odoo.exceptions import UserError

from odoo.addons.somconnexio.tests.helper_service import crm_lead_create
from .base_test_contract_process import BaseContractProcessTestCase


class TestMobileContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.data.update(
            {
                "ticket_number": self.ticket_number,
            }
        )
        self.mobile_ticket_number = "123454321"
        self.fiber_ticket_number = "543212345"

        self.fiber_contract_data.update(
            {
                "ticket_number": self.fiber_ticket_number,
            }
        )
        self.sharing_mobile_data.update(
            {
                "ticket_number": self.ticket_number,
            }
        )

    def test_create_mobile_pack_contract_link_parent_contract(self, *args):
        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number

        fiber_content = self.FiberContractProcess.create(**self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])
        mobile_content = self.data
        mobile_content.update(
            {
                "ticket_number": self.mobile_ticket_number,
                "contract_lines": [
                    {
                        "product_code": self.pack_code,
                        "date_start": "2020-01-01 00:00:00",
                    }
                ],
            }
        )
        mobile_content = self.MobileContractProcess.create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    def test_create_mobile_pack_contract_link_with_contract_line(self, *args):
        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number

        fiber_content = self.FiberContractProcess.create(**self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])
        mobile_content = self.data

        # Substitute a "contract_lines" list for a "contract_line" dict
        mobile_content.update(
            {
                "ticket_number": self.mobile_ticket_number,
                "contract_line": {
                    "product_code": self.pack_code,
                    "date_start": "2020-01-01 00:00:00",
                },
            }
        )
        mobile_content.pop("contract_lines")

        mobile_content = self.MobileContractProcess.create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    def test_raise_error_if_not_found_parent_pack_contract(self, *args):
        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number
        mobile_content = self.data
        mobile_content.update(
            {
                "ticket_number": self.mobile_ticket_number,
                "contract_lines": [
                    {
                        "product_code": self.pack_code,
                        "date_start": "2020-01-01 00:00:00",
                    }
                ],
            }
        )
        self.assertRaisesRegex(
            UserError,
            "Fiber contract of CRMLead ID = {}, ticket = {} not found".format(
                crm_lead.id,
                self.fiber_ticket_number,
            ),
            self.MobileContractProcess.create,
            **mobile_content
        )

    def test_create_mobile_pack_contract_link_known_fiber_contract(self, *args):
        self.fiber_contract_data.update({"ticket_number": "867846"})
        fiber_content = self.FiberContractProcess.create(**self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])

        mobile_content = self.data
        mobile_content.update(
            {
                "ticket_number": "34215134",
                "contract_lines": [
                    {
                        "product_code": self.pack_code,
                        "date_start": "2020-01-01 00:00:00",
                    }
                ],
                "parent_pack_contract_id": fiber_contract.code,
            }
        )
        mobile_content = self.MobileContractProcess.create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    def test_raise_error_if_not_found_parent_pack_contract_with_code(self, *args):
        parent_contract_code = "272281"
        mobile_content = self.data
        mobile_content.update(
            {
                "ticket_number": "",
                "contract_lines": [
                    {
                        "product_code": self.pack_code,
                        "date_start": "2020-01-01 00:00:00",
                    }
                ],
                "parent_pack_contract_id": parent_contract_code,
            }
        )
        self.assertRaisesRegex(
            UserError,
            "Fiber contract with ref = {} not found".format(
                parent_contract_code,
            ),
            self.MobileContractProcess.create,
            **mobile_content
        )
