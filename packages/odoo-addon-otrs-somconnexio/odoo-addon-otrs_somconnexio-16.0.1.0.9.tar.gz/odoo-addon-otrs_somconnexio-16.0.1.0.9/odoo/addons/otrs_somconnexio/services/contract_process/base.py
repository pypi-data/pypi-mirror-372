from odoo.models import AbstractModel
from odoo.exceptions import UserError
from odoo import _
from .. import schemas
from odoo.addons.contract_api_somconnexio.services.contract_process.base import (
    BaseContractProcess as SuperBaseContractProcess,
)


class BaseContractProcess(AbstractModel):
    _inherit = "base.contract.process"

    @staticmethod
    def _to_dict(contract):
        result = SuperBaseContractProcess._to_dict(contract)
        result.update(
            {
                "ticket_number": contract.ticket_number,
            }
        )
        return result

    def _prepare_create(self, params):
        response = super()._prepare_create(params)
        if (
            self.env["contract.contract"]
            .sudo()
            .search(
                [
                    ("ticket_number", "=", params["ticket_number"]),
                ]
            )
        ):
            raise UserError(
                _("Duplicated Ticket Number #{}").format(params["ticket_number"])
            )
        response.update(
            {
                "ticket_number": params["ticket_number"],
            }
        )
        return response

    @staticmethod
    def validator_create():
        schema = SuperBaseContractProcess.validator_create()
        schema.update(schemas.S_CONTRACT_CREATE_TICKET_NUMBER)
        return schema
