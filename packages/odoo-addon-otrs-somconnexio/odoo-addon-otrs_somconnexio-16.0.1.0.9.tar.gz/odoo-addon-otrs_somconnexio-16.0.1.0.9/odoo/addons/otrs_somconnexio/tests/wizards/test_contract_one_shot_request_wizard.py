from unittest.mock import patch
from datetime import date
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractOneShotService(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp()
        self.contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.product = self.env.ref("somconnexio.DadesAddicionals500MB")
        self.user_admin = self.env.ref("base.user_admin")
        self.start_date = date.today()

    @patch(
        "odoo.addons.somconnexio.wizards.contract_one_shot_request.contract_one_shot_request.ContractOneShotRequestWizard._create_activity"  # noqa
    )
    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_one_shot_request.contract_one_shot_request.AddDataTicket"  # noqa
    )
    def test_create_additional_data_otrs_ticket(
        self, MockAddDataTicket, mock_create_activity
    ):
        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": self.product.id,
                    "summary": "Test OTRS tiquet Summary",
                    "done": False,
                }
            )
        )

        wizard.onchange_one_shot_product_id()
        wizard.button_add()

        mock_create_activity.assert_not_called()
        MockAddDataTicket.assert_called_with(
            self.contract.partner_id.vat,
            self.contract.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.product.default_code,
                "subscription_email": self.contract.email_ids[0].email,
                "language": self.contract.partner_id.lang,
            },
        )
        MockAddDataTicket.return_value.create.assert_called_once_with()
