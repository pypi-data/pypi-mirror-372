from mock import patch
from datetime import date, datetime, timedelta

from odoo.exceptions import ValidationError, MissingError

from odoo.addons.somconnexio.helpers.date import first_day_next_month, date_to_str
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractTariffChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.user_admin = self.browse_ref("base.user_root")
        self.partner_id = self.browse_ref("somconnexio.res_partner_1_demo")
        partner_id = self.partner_id.id
        masmovil_mobile_contract_service_info = self.env[
            "mobile.service.contract.info"
        ].create(
            {
                "phone_number": "654321123",
                "icc": "123",
            }
        )
        product = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        self.new_product = self.env.ref("somconnexio.150Min1GB")
        contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": datetime.now() - timedelta(days=12),
        }
        self.vals_contract = {
            "name": "Test Contract Mobile",
            "partner_id": partner_id,
            "invoice_partner_id": partner_id,
            "service_technology_id": self.ref("somconnexio.service_technology_mobile"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_masmovil"),
            "mobile_contract_service_info_id": (
                masmovil_mobile_contract_service_info.id
            ),
            "contract_line_ids": [(0, 0, contract_line)],
            "email_ids": [(6, 0, [partner_id])],
            "mandate_id": self.partner_id.bank_ids[0].mandate_ids[0].id,
        }
        self.contract = self.env["contract.contract"].create(self.vals_contract)

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_tariff_change_ok(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockExceptionalChangeTariffTicket,
        MockChangeTariffTicket,
    ):
        mock_fiber_contract_to_pack_service_create.side_effect = MissingError("")
        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "new_tariff_product_id": self.new_product.id,
                    "otrs_checked": True,
                }
            )
        )
        wizard.onchange_pack_options()
        wizard._compute_available_products()

        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner_id.id)]
        )
        wizard.button_change()

        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner_id.id)],
        )

        expected_start_date = first_day_next_month()
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_tariff_change"),
        )
        self.assertEqual(created_activity.done, True)
        self.assertEqual(
            created_activity.summary,
            " ".join(["Tariff change", self.new_product.showed_name]),
        )

        pack_product = self.env.ref("somconnexio.TrucadesIllimitades20GBPack")
        sharing_data_product = self.env.ref("somconnexio.50GBCompartides3mobils")
        company_product = self.env.ref("somconnexio.TrucadesIllimitades50GBPackEiE")

        # Check bonified product NOT available
        self.assertNotIn(pack_product, wizard.available_products)
        # Check sharing data product NOT available
        self.assertNotIn(sharing_data_product, wizard.available_products)
        # Check company produt NOT available
        self.assertNotIn(company_product, wizard.available_products)

        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.new_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(expected_start_date),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()
        MockExceptionalChangeTariffTicket.assert_not_called()

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_tariff_change_not_checked(
        self, mock_fiber_contract_to_pack_service_create
    ):
        mock_fiber_contract_to_pack_service_create.side_effect = MissingError("")
        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "new_tariff_product_id": self.new_product.id,
                }
            )
        )

        self.assertRaisesRegex(
            ValidationError,
            "You must check if any previous tariff change is found in OTRS",
            wizard.button_change,
        )

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_exceptional_tariff_change_ok(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockExceptionalChangeTariffTicket,
        MockChangeTariffTicket,
    ):
        mock_fiber_contract_to_pack_service_create.side_effect = MissingError("")
        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "exceptional_change": True,
                    "new_tariff_product_id": self.new_product.id,
                    "send_notification": True,
                    "otrs_checked": True,
                }
            )
        )

        wizard.button_change()

        expected_start_date = date.today()

        self.assertEqual(wizard.start_date, expected_start_date)
        MockExceptionalChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.new_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(expected_start_date),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": True,
            },
        )
        MockExceptionalChangeTariffTicket.return_value.create.assert_called_once()
        MockChangeTariffTicket.assert_not_called()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_exceptional_tariff_with_date(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockExceptionalChangeTariffTicket,
        MockChangeTariffTicket,
    ):
        mock_fiber_contract_to_pack_service_create.side_effect = MissingError("")
        expected_start_date = date.today() - timedelta(days=1)
        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "exceptional_change": True,
                    "new_tariff_product_id": self.new_product.id,
                    "send_notification": True,
                    "otrs_checked": True,
                    "start_date": expected_start_date,
                }
            )
        )

        wizard.button_change()

        self.assertEqual(wizard.start_date, expected_start_date)
        MockExceptionalChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.new_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(expected_start_date),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": True,
            },
        )
        MockExceptionalChangeTariffTicket.return_value.create.assert_called_once()
        MockChangeTariffTicket.assert_not_called()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_tariff_change_bonified_product_ok(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockExceptionalChangeTariffTicket,
        MockChangeTariffTicket,
    ):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        pack_product = self.env.ref("somconnexio.TrucadesIllimitades20GBPack")

        # Bonified mobile product available
        mock_fiber_contract_to_pack_service_create.return_value = fiber_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "pinya_mobile_tariff",
                    "new_tariff_product_id": pack_product.id,
                }
            )
        )
        wizard.onchange_pack_options()

        self.assertEqual(wizard.available_fiber_contracts, fiber_contract)

        wizard.write(
            {
                "fiber_contract_to_link": fiber_contract.id,
            }
        )

        wizard.button_change()

        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )
        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": pack_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_contract.code,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()
        MockExceptionalChangeTariffTicket.assert_not_called()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicketSharedBond"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_new_shared_bond_tariff_change_all_new(
        self, mock_fiber_contract_to_pack_service_create, MockSharedChangeTariffTicket
    ):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        mobile_2_contract = self.env.ref("somconnexio.contract_mobile_il_20_pack")
        shared_2_product = self.env.ref("somconnexio.50GBCompartides2mobils")
        mobile_contract_conserva = self.env.ref(
            "somconnexio.contract_mobile_t_conserva"
        )

        mock_fiber_contract_to_pack_service_create.return_value = fiber_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "new_shared_bond",
                }
            )
        )
        wizard.onchange_pack_options()

        self.assertEqual(
            wizard.mobile_contracts_available_to_pack,
            mobile_contract + mobile_contract_conserva + mobile_2_contract,
        )
        self.assertIn(
            fiber_contract,
            wizard.available_fiber_contracts,
        )
        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

        wizard.write(
            {
                "fiber_contract_to_link": fiber_contract.id,
            }
        )
        wizard.onchange_fiber_contract_to_link()

        wizard.write(
            {
                "mobile_contracts_in_pack": [(4, mobile_contract.id, 0)],
                "new_tariff_product_id": shared_2_product.id,
            }
        )

        # No other mobile added
        self.assertEqual(
            wizard.mobile_contracts_in_pack, self.contract + mobile_contract
        )

        wizard.button_change()

        MockSharedChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": shared_2_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_contract.code,
                "send_notification": False,
                "contracts": [
                    {
                        "phone_number": contract.phone_number,
                        "current_product_code": contract.current_tariff_product.code,
                        "subscription_email": contract.email_ids[0].email,
                    }
                    for contract in wizard.mobile_contracts_in_pack
                ],
            },
        )

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicketSharedBond"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_new_shared_bond_tariff_change_packed_fiber(
        self, mock_fiber_contract_to_pack_service_create, MockSharedChangeTariffTicket
    ):
        fiber_pack_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        mobile_pack_contract = self.env.ref("somconnexio.contract_mobile_il_20_pack")
        shared_3_product = self.env.ref("somconnexio.50GBCompartides3mobils")

        mock_fiber_contract_to_pack_service_create.return_value = fiber_pack_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "new_shared_bond",
                }
            )
        )
        wizard.onchange_pack_options()

        self.assertEqual(wizard.available_fiber_contracts, fiber_pack_contract)
        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

        wizard.write(
            {
                "fiber_contract_to_link": fiber_pack_contract.id,
            }
        )
        # Pack mobile added automatically (onchange) because is linked to fiber
        wizard.onchange_fiber_contract_to_link()

        wizard.write(
            {
                "mobile_contracts_in_pack": [(4, mobile_contract.id, 0)],
                "new_tariff_product_id": shared_3_product.id,
            }
        )

        self.assertEqual(
            wizard.mobile_contracts_in_pack,
            self.contract + mobile_contract + mobile_pack_contract,
        )

        wizard.button_change()

        MockSharedChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": shared_3_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_pack_contract.code,
                "send_notification": False,
                "contracts": [
                    {
                        "phone_number": contract.phone_number,
                        "current_product_code": contract.current_tariff_product.code,
                        "subscription_email": contract.email_ids[0].email,
                    }
                    for contract in wizard.mobile_contracts_in_pack
                ],
            },
        )

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicketMobilePack"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_new_fiber_300_pack(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockMobilePackChangeTariffTicket,
    ):
        # Fiber must be 300 Mb
        fiber_pack_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        fiber_pack_contract.contract_line_ids[0].product_id = self.env.ref(
            "somconnexio.SenseFixFibra300Mb"
        ).id
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        mobile_pack_contract = self.env.ref("somconnexio.contract_mobile_il_20_pack")
        pack_3_product = self.env.ref("somconnexio.TrucadesIllimitades30GBPack3mbl")

        mock_fiber_contract_to_pack_service_create.return_value = fiber_pack_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "new_pinya_tariff_pack",
                }
            )
        )
        wizard.onchange_pack_options()

        self.assertEqual(wizard.available_fiber_contracts, fiber_pack_contract)
        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

        wizard.write(
            {
                "fiber_contract_to_link": fiber_pack_contract.id,
            }
        )
        # Pack mobile added automatically (onchange) because is linked to fiber
        wizard.onchange_fiber_contract_to_link()

        wizard.write(
            {
                "mobile_contracts_in_pack": [(4, mobile_contract.id, 0)],
                "new_tariff_product_id": pack_3_product.id,
            }
        )

        self.assertEqual(
            wizard.mobile_contracts_in_pack,
            self.contract + mobile_contract + mobile_pack_contract,
        )

        wizard.button_change()

        MockMobilePackChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": pack_3_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_pack_contract.code,
                "send_notification": False,
                "contracts": [
                    {
                        "phone_number": contract.phone_number,
                        "current_product_code": contract.current_tariff_product.code,
                        "subscription_email": contract.email_ids[0].email,
                    }
                    for contract in wizard.mobile_contracts_in_pack
                ],
            },
        )

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_new_shared_bond_tariff_too_many_mobiles(
        self, mock_fiber_contract_to_pack_service_create
    ):
        fiber_pack_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        mobile_pack_contract = self.env.ref("somconnexio.contract_mobile_il_20_pack")
        mobile_contract_conserva = self.env.ref(
            "somconnexio.contract_mobile_t_conserva"
        )

        mock_fiber_contract_to_pack_service_create.return_value = fiber_pack_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "new_shared_bond",
                }
            )
        )
        wizard.onchange_pack_options()

        self.assertEqual(
            wizard.mobile_contracts_available_to_pack,
            mobile_contract + mobile_contract_conserva + mobile_pack_contract,
        )
        self.assertEqual(wizard.available_fiber_contracts, fiber_pack_contract)
        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

        wizard.write(
            {
                "fiber_contract_to_link": fiber_pack_contract.id,
            }
        )
        wizard.onchange_fiber_contract_to_link()

        wizard.write(
            {
                "mobile_contracts_in_pack": [(4, mobile_contract.id, 0)],
            }
        )

        self.assertEqual(len(wizard.mobile_contracts_in_pack), 3)

        other_mobile_contract = self.env["contract.contract"].create(self.vals_contract)

        wizard.write(
            {
                "mobile_contracts_in_pack": [(4, other_mobile_contract.id, 0)],
            }
        )

        self.assertRaisesRegex(
            ValidationError,
            "Maximum 3 mobile contracts to pack",
            wizard.button_change,
        )

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_new_shared_bond_tariff_too_few_mobiles(
        self, mock_fiber_contract_to_pack_service_create
    ):
        fiber_pack_contract = self.env.ref("somconnexio.contract_fibra_600")

        mock_fiber_contract_to_pack_service_create.return_value = fiber_pack_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "new_shared_bond",
                }
            )
        )
        wizard.onchange_pack_options()

        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

        wizard.write(
            {
                "fiber_contract_to_link": fiber_pack_contract.id,
            }
        )
        wizard.onchange_fiber_contract_to_link()

        self.assertRaisesRegex(
            ValidationError,
            "Another mobile is required to create a pack",
            wizard.button_change,
        )

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_add_to_existing_shared_bond(
        self, mock_fiber_contract_to_pack_service_create, MockChangeTariffTicket
    ):
        fiber_sharing_contract = self.env.ref("somconnexio.contract_fibra_600_shared")
        mobile_sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        shared_3_product = self.env.ref("somconnexio.50GBCompartides3mobils")

        mock_fiber_contract_to_pack_service_create.return_value = fiber_sharing_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=mobile_contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "existing_shared_bond_pack",
                    "new_tariff_product_id": shared_3_product.id,
                }
            )
        )
        wizard.onchange_pack_options()

        wizard.write(
            {
                "fiber_contract_to_link": mobile_sharing_contract.parent_pack_contract_id.id,  # noqa
            }
        )
        wizard.onchange_fiber_contract_to_link()

        self.assertEqual(wizard.fiber_contract_to_link, fiber_sharing_contract)
        self.assertFalse(wizard.is_pack_full)

        wizard.button_change()

        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": mobile_contract.phone_number,
                "new_product_code": shared_3_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_sharing_contract.code,
                "send_notification": False,
                "shared_bond_id": mobile_sharing_contract.shared_bond_id,
            },
        )

        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_add_to_existing_full_shared_bond(
        self,
        mock_fiber_contract_to_pack_service_create,
        MockChangeTariffTicket,
        MockChangeTariffExceptionalTicket,
    ):
        fiber_sharing_contract = self.env.ref("somconnexio.contract_fibra_300_shared")
        mobile_sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_3"
        )
        mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        shared_3_product = self.env.ref("somconnexio.50GBCompartides3mobils")

        mock_fiber_contract_to_pack_service_create.return_value = fiber_sharing_contract

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=mobile_contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "existing_shared_bond_pack",
                    "new_tariff_product_id": shared_3_product.id,
                }
            )
        )
        wizard.onchange_pack_options()

        new_product_exchanged_phone = mobile_contract.current_tariff_product

        wizard.write(
            {
                "fiber_contract_to_link": mobile_sharing_contract.parent_pack_contract_id.id,  # noqa
                "phone_to_exchange": mobile_sharing_contract.id,
                "new_tariff_product_id_exchanged_phone": new_product_exchanged_phone.id,
            }
        )

        wizard.onchange_fiber_contract_to_link()
        mobile_sharing_contract._compute_contracts_in_pack()

        self.assertEqual(wizard.fiber_contract_to_link, fiber_sharing_contract)
        self.assertTrue(wizard.is_pack_full)
        self.assertEqual(
            wizard.mobile_contracts_in_pack,
            mobile_sharing_contract.contracts_in_pack
            - mobile_sharing_contract.parent_pack_contract_id
            + mobile_contract,
        )

        wizard.button_change()

        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": mobile_contract.phone_number,
                "new_product_code": shared_3_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": fiber_sharing_contract.code,
                "send_notification": False,
                "shared_bond_id": mobile_sharing_contract.shared_bond_id,
            },
        )
        MockChangeTariffExceptionalTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": mobile_sharing_contract.phone_number,
                "new_product_code": new_product_exchanged_phone.default_code,
                "current_product_code": shared_3_product.default_code,
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": False,
            },
        )
        mock_fiber_contract_to_pack_service_create.assert_called_with(
            partner_ref=self.partner_id.ref, all="true"
        )

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_no_shared_bond_options(
        self, mock_fiber_contract_to_pack_service_create
    ):
        # No fiber available
        mock_fiber_contract_to_pack_service_create.side_effect = MissingError("")

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)  # noqa
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                }
            )
        )

        self.assertFalse(wizard.available_fiber_contracts)
        self.assertRaises(ValueError, wizard.write, {"pack_options": "new_shared_bond"})

    def test_will_force_other_mobiles_to_quit_pack_2_shared_mobiles(self):
        mbl_contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        mbl_contract._compute_contracts_in_pack()

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=mbl_contract.id)
            .create(
                {
                    "new_tariff_product_id": self.new_product.id,
                }
            )
        )

        self.assertTrue(wizard.will_force_other_mobiles_to_quit_pack)

    @patch(
        'odoo.addons.otrs_somconnexio.services.fiber_contract_to_pack.SearchTicketsService' # noqa
    )
    def test_will_force_other_mobiles_to_quit_pack_less_than_2_shared_mobiles(self, _):
        mbl_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        mbl_contract._compute_contracts_in_pack()

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=mbl_contract.id)
            .create(
                {
                    "new_tariff_product_id": self.new_product.id,
                }
            )
        )

        self.assertFalse(wizard.will_force_other_mobiles_to_quit_pack)

    @patch(
        "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
    )
    def test_wizard_mobile_tariff_change_company_products(
        self, mock_fiber_contract_to_pack_service_create
    ):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")

        # Bonified mobile product available
        mock_fiber_contract_to_pack_service_create.return_value = fiber_contract

        self.partner_id.is_company = True

        company_contract = self.env["contract.contract"].create(self.vals_contract)
        company_product = self.env.ref("somconnexio.TrucadesIllimitades50GBPackEiE")

        wizard = (
            self.env["contract.mobile.tariff.change.wizard"]
            .with_context(active_id=company_contract.id)
            .sudo()
            .create(
                {
                    "otrs_checked": True,
                    "pack_options": "pinya_mobile_tariff",
                    "new_tariff_product_id": company_product.id,
                }
            )
        )
        wizard.onchange_pack_options()
        wizard._compute_available_products()

        # Check company produt available
        self.assertIn(company_product, wizard.available_products)
