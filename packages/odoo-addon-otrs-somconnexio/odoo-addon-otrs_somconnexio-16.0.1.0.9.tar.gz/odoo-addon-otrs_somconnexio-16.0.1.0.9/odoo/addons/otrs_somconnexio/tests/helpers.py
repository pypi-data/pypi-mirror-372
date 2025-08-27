from faker import Faker
from datetime import datetime
import random
from odoo.addons.somconnexio.tests.helper_service import random_ref

faker = Faker("es_CA")


class FakeOTRSTicket:
    """Represents a Fake OTRSTicket instance"""

    def __init__(self, ticket_number=False):
        self.id = random_ref()
        self.number = ticket_number or datetime.now().strftime("%Y%m%d%H%M%S") + str(
            random.randint(0, 9)
        )
