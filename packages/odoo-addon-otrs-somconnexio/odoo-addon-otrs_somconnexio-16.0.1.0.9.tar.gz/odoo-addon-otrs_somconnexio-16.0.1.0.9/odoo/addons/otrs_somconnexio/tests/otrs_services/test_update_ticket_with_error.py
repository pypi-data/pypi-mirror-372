from mock import patch

from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ...otrs_services.update_ticket_with_error import UpdateTicketWithError


@patch(
    "otrs_somconnexio.services.update_ticket_with_provider_info.UpdateTicketWithProviderInfo.run"  # noqa
)
class UpdateTicketWithErrorTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.error = {
            "title": "Unexpected error ocurred with this ticket",
            "body": "test body",
        }
        self.ticket_id = "123424"

    def test_custom_error_wth_df(self, mock_run):
        df_dct = {"df_key": "df_value", "df_second_key": "df_second_value"}

        update_ticket_with_error = UpdateTicketWithError(
            self.ticket_id, self.error, df_dct
        )

        self.assertEqual(update_ticket_with_error.ticket_id, self.ticket_id)
        self.assertEqual(update_ticket_with_error.df_dct, df_dct)
        self.assertIsInstance(update_ticket_with_error.article, AbstractArticle)
        self.assertEqual(update_ticket_with_error.article.subject, self.error["title"])
        self.assertEqual(update_ticket_with_error.article.body, self.error["body"])

        update_ticket_with_error.run()

        mock_run.assert_called_once_with()

    def test_custom_error_wo_df(self, mock_run):
        update_ticket_with_error = UpdateTicketWithError(self.ticket_id, self.error)

        self.assertFalse(update_ticket_with_error.df_dct)

        update_ticket_with_error.run()

        mock_run.assert_called_once_with()
