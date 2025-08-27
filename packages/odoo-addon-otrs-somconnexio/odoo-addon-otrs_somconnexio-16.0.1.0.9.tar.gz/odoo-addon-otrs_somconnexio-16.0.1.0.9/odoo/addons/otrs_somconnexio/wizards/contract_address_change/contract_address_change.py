from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.asociatel_fiber import AsociatelFiberCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fiber import MMFiberCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fiber import VdfFiberCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fiber import OrangeFiberCoverage

from odoo import fields, models


class ContractAddressChangeWizard(models.TransientModel):
    _inherit = "contract.address.change.wizard"

    mm_fiber_coverage = fields.Selection(
        MMFiberCoverage.VALUES,
        "MM Fiber Coverage",
    )
    asociatel_fiber_coverage = fields.Selection(
        AsociatelFiberCoverage.VALUES,
        "Asociatel Fiber Coverage",
    )
    vdf_fiber_coverage = fields.Selection(
        VdfFiberCoverage.VALUES,
        "Vdf Fiber Coverage",
    )
    orange_fiber_coverage = fields.Selection(
        OrangeFiberCoverage.VALUES,
        "Orange Fiber Coverage",
    )
    adsl_coverage = fields.Selection(
        ADSLCoverage.VALUES,
        "ADSL Coverage",
    )

    def _get_broadband_isp_info_params(self):
        params = super()._get_broadband_isp_info_params()
        params.update(
            {
                "mm_fiber_coverage": self.mm_fiber_coverage or "NoRevisat",
                "asociatel_fiber_coverage": self.asociatel_fiber_coverage
                or "NoRevisat",
                "vdf_fiber_coverage": self.vdf_fiber_coverage or "NoRevisat",
                "orange_fiber_coverage": self.orange_fiber_coverage or "NoRevisat",
                "adsl_coverage": self.adsl_coverage or "NoServei",
            }
        )
        return params
