from mock import patch

from odoo.exceptions import ValidationError
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractIBANChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.partner_mandate = self.browse_ref(
            "somconnexio.demo_mandate_partner_1_demo"
        )
        self.user_admin = self.browse_ref("base.user_admin")
        self.contract = self.browse_ref("somconnexio.contract_mobile_il_20")
        self.wizard = (
            self.env["contract.iban.change.wizard"]
            .with_context(active_id=self.partner.id)
            .sudo()
            .create(
                {
                    "contract_ids": [(6, 0, [self.contract.id])],
                    "account_banking_mandate_id": self.partner_mandate.id,
                }
            )
        )

    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.contract_iban_change.contract_iban_change.ContractIbanChangeProcess"  # noqa
    )
    def test_wizard_from_api_ok(self, MockContractIbanChangeProcess):
        self.wizard.run_from_api()

        MockContractIbanChangeProcess.assert_called_once()
        MockContractIbanChangeProcess.return_value.run_from_api.assert_called_once()

    @patch(
        "odoo.addons.otrs_somconnexio.wizards.contract_iban_change.contract_iban_change.UpdateTicketWithError"  # noqa
    )
    @patch(
        "odoo.addons.contract_api_somconnexio.wizards.contract_iban_change.contract_iban_change.ContractIbanChangeProcess"  # noqa
    )
    def test_wizard_run_from_api_validation_error_update_ticket(
        self, MockContractIbanChangeProcess, MockUpdateTicketWithError
    ):
        MockContractIbanChangeProcess.return_value.run_from_api.side_effect = (
            ValidationError("")
        )
        ticket_id = ("1234",)
        params = {
            "ticket_id": ticket_id,
            "iban": "ESXXXXX",
        }
        error = {
            "title": "Error en el canvi d'IBAN",
            "body": "Banc del nou IBAN desconegut: ESXXXXX."
            + "\nDesprés d'afegir el seu banc corresponent al registre "
            + "d'ODOO, torna a intentar aquesta petició.",
        }
        dynamic_fields_dct = {"ibanKO": 1}

        self.wizard.run_from_api(**params)

        MockUpdateTicketWithError.assert_called_once_with(
            ticket_id,
            error,
            dynamic_fields_dct,
        )
        MockUpdateTicketWithError.return_value.run.assert_called_once()
