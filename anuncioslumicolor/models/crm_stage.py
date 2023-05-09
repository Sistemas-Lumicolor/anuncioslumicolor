from odoo import fields, models


class Stage(models.Model):
    _inherit = "crm.stage"

    stage_type = fields.Selection(
        [("opportunity", "Opportunity"), ("lead", "Lead")],
        help="It helps to filter where you want to display the stage, by default they appear in Lead",
    )
