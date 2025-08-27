from odoo.addons.contract_api_somconnexio.tests.services.contract_process.base_test_contract_process.sc_test_case import (  # noqa
    BaseContractProcessTestCase as BaseTestCase,
)


class BaseContractProcessTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ticket_number = "1234"
