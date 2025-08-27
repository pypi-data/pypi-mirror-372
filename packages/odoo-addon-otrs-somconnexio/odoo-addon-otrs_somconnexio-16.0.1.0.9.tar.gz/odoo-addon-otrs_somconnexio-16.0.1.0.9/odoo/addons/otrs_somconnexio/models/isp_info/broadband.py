from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fiber import MMFiberCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fiber import VdfFiberCoverage
from otrs_somconnexio.otrs_models.coverage.asociatel_fiber import AsociatelFiberCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fiber import OrangeFiberCoverage

from odoo import models, fields


class BroadbandISPInfo(models.Model):
    _inherit = "broadband.isp.info"

    mm_fiber_coverage = fields.Selection(
        MMFiberCoverage.VALUES,
        "MM Fiber Coverage",
    )
    vdf_fiber_coverage = fields.Selection(
        VdfFiberCoverage.VALUES,
        "Vdf Fiber Coverage",
    )
    asociatel_fiber_coverage = fields.Selection(
        AsociatelFiberCoverage.VALUES,
        "Asociatel Fiber Coverage",
    )
    orange_fiber_coverage = fields.Selection(
        OrangeFiberCoverage.VALUES, "Orange Fiber Coverage"
    )
    adsl_coverage = fields.Selection(
        ADSLCoverage.VALUES,
        "ADSL Coverage",
    )
