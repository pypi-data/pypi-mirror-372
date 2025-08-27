from datetime import date, datetime

from mock import patch

from ...services.mobile_activation_date_service import MobileActivationDateService
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


@patch(
    "odoo.addons.otrs_somconnexio.services.mobile_activation_date_service.datetime",
    spec=["now"],
)
class MobileActivationDateServiceTests(SCTestCase):
    def test_dates_without_holidays(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 6, 17, 0, 0)

        dates_service = MobileActivationDateService(self.env, False)

        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 7))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 7))

    def test_dates_with_holidays(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 6, 17, 0, 0)
        self.env["resource.calendar.leaves"].create(
            {"name": "holiday 5", "date_from": "2023-03-09", "date_to": "2023-03-09"}
        )

        dates_service = MobileActivationDateService(self.env, False)
        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 7))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 7))

    def test_dates_weekend(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 9, 17, 0, 0)

        dates_service = MobileActivationDateService(self.env, False)

        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 10))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 10))

    def test_dates_with_portability(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 6, 17, 0, 0)

        dates_service = MobileActivationDateService(self.env, True)

        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 7))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 9))

    def test_dates_before_max_time_day(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 6, 10, 0, 0)

        dates_service = MobileActivationDateService(self.env, False)

        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 6))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 6))

    def test_dates_after_max_time_day(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 3, 6, 18, 0, 0)

        dates_service = MobileActivationDateService(self.env, False)

        self.assertEqual(dates_service.get_introduced_date(), date(2023, 3, 7))
        self.assertEqual(dates_service.get_activation_date(), date(2023, 3, 7))
