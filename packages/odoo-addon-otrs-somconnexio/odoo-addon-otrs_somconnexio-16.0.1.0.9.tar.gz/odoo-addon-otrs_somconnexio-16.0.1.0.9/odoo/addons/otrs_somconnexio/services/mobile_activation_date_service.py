from datetime import datetime, time, timedelta


class MobileActivationDateService:
    # TIME_LIMIT is the time limit to define the introduced_date the same day or
    # the next working day.
    # Is the execution time is before the TIME_LIMIT we assign the same day,
    # if is after we assign the next working day
    TIME_LIMIT = time(16, 00, 00)

    def __init__(self, env, portability):
        self.env = env
        self.portability = portability
        self.holidays = zip(
            self.env["resource.calendar.leaves"].sudo().search([]).mapped("date_to"),
            self.env["resource.calendar.leaves"].sudo().search([]).mapped("date_from")
        )
        self.introduced_date = None

    def _next_working_day(self, day):

        while (
                any(h[0].date() >= day >= h[1].date() for h in self.holidays)
                or not day.weekday() < 5  # 5 Sat, 6 Sun
        ):
            day += timedelta(days=1)
        return day

    def _is_before_max_time_day(self):
        return datetime.now().time() <= self.TIME_LIMIT

    # Used from SIM shipment process
    def get_introduced_date(self):
        """
        If is before the TIME_LIMIT, return today.
        After the TIME_LIMIT, the first next working day.
        """
        if self.introduced_date:
            return self.introduced_date
        now = datetime.now()
        introduced_date = (
            now.date()
            if self._is_before_max_time_day()
            else now.date() + timedelta(days=1)
        )
        self.introduced_date = self._next_working_day(introduced_date)
        return self.introduced_date

    def get_activation_date(self):
        """
        The next working day after the introduced date.
        In case of portability add 2 days more.

        """
        if not self.portability:
            return self.get_introduced_date()
        return self._next_working_day(self.get_introduced_date() + timedelta(days=2))
