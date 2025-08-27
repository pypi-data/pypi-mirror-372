from datetime import date

from mock import Mock, patch, call

from odoo.addons.somconnexio.tests.helper_service import crm_lead_create
from odoo.addons.contract_api_somconnexio.tests.services.contract_process.base_test_contract_process import (  # noqa
    BaseContractProcessTestCase,
)


class TestFiberContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.FiberContractProcess = self.env["fiber.contract.process"]
        self.ticket_number = "423234"
        self.data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra100Mb").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number,
            "mandate": self.mandate,
        }
        mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades17GB")
        mobile_contract_service_info = self.env["mobile.service.contract.info"].create(
            {"phone_number": "654321123", "icc": "123"}
        )
        contract_line = {
            "name": mobile_product.showed_name,
            "product_id": mobile_product.id,
            "date_start": "2020-01-01 00:00:00",
        }
        self.vals_mobile_contract = {
            "name": "New Contract Mobile",
            "partner_id": self.partner.id,
            "invoice_partner_id": self.partner.id,
            "service_technology_id": self.ref("somconnexio.service_technology_mobile"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_masmovil"),
            "mobile_contract_service_info_id": (mobile_contract_service_info.id),
            "contract_line_ids": [(0, 0, contract_line)],
            "mandate_id": self.mandate.id,
        }
        self.mobile_pack_product = self.browse_ref(
            "somconnexio.TrucadesIllimitades30GBPack"
        )

    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.MobileActivationDateService"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.SetFiberContractCodeMobileTicket"  # noqa
    )
    def test_create_fiber_unblock_mobile_ticket(
        self,
        SetFiberContractCodeMock,
        UnblockMobilePackTicketMock,
        MobileActivationDateServiceMock,
        *args
    ):
        expected_date = date(2023, 10, 10)
        MobileActivationDateServiceMock.return_value.get_activation_date.return_value = (  # noqa
            expected_date
        )
        MobileActivationDateServiceMock.return_value.get_introduced_date.return_value = (  # noqa
            expected_date
        )
        pack_code = self.browse_ref(
            "somconnexio.TrucadesIllimitades30GBPack"
        ).default_code
        new_ticket_number = "123454321"
        crm_lead = crm_lead_create(self.env, self.partner, "pack", portability=False)
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == pack_code:
                line.ticket_number = new_ticket_number
            else:
                line.ticket_number = self.ticket_number

        content = self.FiberContractProcess.create(**self.data)

        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            self.data["vodafone_fiber_contract_service_info"]["phone_number"],
        )

        UnblockMobilePackTicketMock.assert_called_once_with(
            new_ticket_number,
            activation_date=str(expected_date),
            introduced_date=str(expected_date),
        )
        UnblockMobilePackTicketMock.return_value.run.assert_called_once_with()

        SetFiberContractCodeMock.assert_called_once_with(
            new_ticket_number, fiber_contract_code=contract.code
        )

    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.SetFiberContractCodeMobileTicket"  # noqa
    )
    def test_create_fiber_unblock_mobile_ticket_without_set_fiber_contract_code(
        self, SetFiberContractCodeMock, UnblockMobilePackTicketMock, *args
    ):
        no_pack_product = self.browse_ref("somconnexio.TrucadesIllimitades20GB")
        new_ticket_number = "123454321"
        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        for line in crm_lead.lead_line_ids:
            if line.is_mobile:
                line.product_id = no_pack_product.id
                line.ticket_number = new_ticket_number
            else:
                line.ticket_number = self.ticket_number

        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            self.data["vodafone_fiber_contract_service_info"]["phone_number"],
        )
        UnblockMobilePackTicketMock.return_value.run.assert_called_once_with()

        SetFiberContractCodeMock.assert_not_called()

    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.MobileActivationDateService"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.SetFiberContractCodeMobileTicket"  # noqa
    )
    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._relate_new_fiber_with_existing_mobile_contracts"  # noqa
    )
    def test_create_fiber_unblock_shared_mobile_tickets(
        self,
        mock_relate_with_mobile,
        SetFiberContractCodeMock,
        UnblockMobilePackTicketMock,
        MobileActivationDateServiceMock,
        *args
    ):
        expected_date = date(2023, 10, 10)
        MobileActivationDateServiceMock.return_value.get_activation_date.return_value = (  # noqa
            expected_date
        )
        MobileActivationDateServiceMock.return_value.get_introduced_date.return_value = (  # noqa
            expected_date
        )
        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        crm_lead_line = crm_lead.lead_line_ids.filtered("is_mobile").copy()
        crm_lead.write({"lead_line_ids": [(4, crm_lead_line.id, 0)]})
        shared_product = self.browse_ref("somconnexio.50GBCompartides2mobils")
        first_ticket_number = "123456"
        second_ticket_number = "234567"

        mobile_lines = crm_lead.lead_line_ids.filtered("is_mobile")
        mobile_lines[0].product_id = shared_product.id
        mobile_lines[0].ticket_number = first_ticket_number
        mobile_lines[1].product_id = shared_product.id
        mobile_lines[1].ticket_number = second_ticket_number
        fiber_line = crm_lead.lead_line_ids.filtered("is_fiber")
        fiber_line.ticket_number = self.ticket_number

        content = self.FiberContractProcess.create(**self.data)
        contract = self.env["contract.contract"].browse(content["id"])
        self.assertEqual(
            contract.name,
            self.data["vodafone_fiber_contract_service_info"]["phone_number"],
        )

        UnblockMobilePackTicketMock.assert_has_calls(
            [
                call(
                    first_ticket_number,
                    activation_date=str(expected_date),
                    introduced_date=str(expected_date),
                ),
                call(
                    second_ticket_number,
                    activation_date=str(expected_date),
                    introduced_date=str(expected_date),
                ),
            ],
            any_order=True,
        )

        SetFiberContractCodeMock.assert_has_calls(
            [
                call(first_ticket_number, fiber_contract_code=contract.code),
                call(second_ticket_number, fiber_contract_code=contract.code),
            ],
            any_order=True,
        )

        mock_relate_with_mobile.assert_called_once()
        args, _ = mock_relate_with_mobile.call_args

        self.assertEqual(args[0]["id"], contract.id)

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ContractMobileTariffChangeWizard.button_change"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.FiberContractProcess._update_pack_mobile_tickets"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_relate_with_one_mobile_contract_having_CRM_with_pack_product(
        self,
        mock_send_email,
        mock_update_pack_mobile_tickets,
        mock_change_tariff_create,
        *args
    ):
        """
        Check if a fiber is created with an existing unpacked mobile
        contract with an appropiate tariff to become pack, if fiber
        CRM also has a mobile pack petition, no change is done
        """

        # Create packable mobile contract
        self.env["contract.contract"].create(self.vals_mobile_contract)

        crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "pack",
            portability=False,
        )
        fiber_lead_line = crm_lead.lead_line_ids.filtered("is_fiber")
        fiber_lead_line.ticket_number = self.ticket_number

        self.FiberContractProcess.create(**self.data)

        mock_send_email.assert_not_called()
        mock_change_tariff_create.assert_not_called()
        mock_update_pack_mobile_tickets.assert_called_once()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ContractMobileTariffChangeWizard.create",  # noqa
        return_value=Mock(spec=["button_change"]),
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.FiberContractProcess._update_pack_mobile_tickets"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_relate_with_one_mobile_contract_having_CRM_wo_pack_product(
        self,
        mock_send_email,
        mock_update_pack_mobile_tickets,
        mock_change_tariff_create,
        *args
    ):
        """
        Check if a fiber is created with an existing unpacked mobile
        contract with an appropiate tariff to become pack, if fiber
        CRM does not have a mobile pack petition, a mobile change
        tariff wizard is created with the fiber contract code
        """

        non_pack_mbl_product = self.browse_ref("somconnexio.150Min1GB")
        pack_mobile_product_id = self.browse_ref(
            "somconnexio.TrucadesIllimitades30GBPack"
        ).id

        # Create packable mobile contract
        mbl_contract = self.env["contract.contract"].create(self.vals_mobile_contract)
        crm_lead = crm_lead_create(self.env, self.partner, "pack", portability=False)
        fiber_lead_line = crm_lead.lead_line_ids.filtered("is_fiber")
        fiber_lead_line.ticket_number = self.ticket_number
        mobile_lead_line = crm_lead.lead_line_ids.filtered("is_mobile").filtered(
            "is_from_pack"
        )
        mobile_lead_line.product_id = non_pack_mbl_product.id

        content = self.FiberContractProcess.create(**self.data)

        mock_change_tariff_create.assert_called_once_with(
            {
                "new_tariff_product_id": pack_mobile_product_id,
                "fiber_contract_to_link": content["id"],
                "exceptional_change": True,
                "otrs_checked": True,
                "send_notification": False,
            }
        )
        mock_change_tariff_create.return_value.button_change.assert_called_once_with()  # noqa
        mock_update_pack_mobile_tickets.assert_called_once()

        mock_send_email.assert_called_with(
            mbl_contract.id,
        )  # TODO: how to check from which mail template is called?

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ContractMobileTariffChangeWizard.button_change"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.services.contract_process.fiber.FiberContractProcess._update_pack_mobile_tickets"  # noqa
    )
    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_relate_with_one_mobile_contract_location_change_case(
        self,
        mock_send_email,
        mock_update_pack_mobile_tickets,
        mock_change_tariff_create,
        *args
    ):
        """
        Check that if a location_change fiber is created no mobile contract
        is related with it
        """

        crm_lead = crm_lead_create(self.env, self.partner, "pack", portability=False)
        fiber_lead_line = crm_lead.lead_line_ids.filtered("is_fiber")
        fiber_lead_line.ticket_number = self.ticket_number
        fiber_lead_line.create_reason = "location_change"

        # Create packable mobile contract
        self.env["contract.contract"].create(self.vals_mobile_contract)

        contract = self.FiberContractProcess.create(**self.data)

        mock_send_email.assert_not_called()
        mock_change_tariff_create.assert_not_called()
        mock_update_pack_mobile_tickets.assert_called_once()
        self.assertEqual(contract["create_reason"], "location_change")

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ContractMobileTariffChangeWizard.create",  # noqa
        return_value=Mock(spec=["button_change"]),
    )
    def test_change_related_mobile_contract_tariff(self, mock_change_tariff_create):
        mobile_contract = self.env["contract.contract"].create(
            self.vals_mobile_contract
        )
        contract_dict = {"id": 1234}

        self.FiberContractProcess._change_related_mobile_contract_tariff(
            mobile_contract.id, contract_dict
        )

        mock_change_tariff_create.assert_called_once_with(
            {
                "new_tariff_product_id": self.mobile_pack_product.id,
                "fiber_contract_to_link": contract_dict["id"],
                "exceptional_change": True,
                "otrs_checked": True,
                "send_notification": False,
            }
        )
        mock_change_tariff_create.return_value.button_change.assert_called_once_with()  # noqa
