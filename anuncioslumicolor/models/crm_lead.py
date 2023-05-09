from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    stage_id = fields.Many2one(
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id),  ('stage_type', '=', stage_type)]"
    )
    stage_type = fields.Selection(related="stage_id.stage_type", store=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        team = (
            self._context.get("default_team_id") or self.env["crm.team"]._get_default_team_id(user_id=self.env.uid).id
        )
        res = super(CrmLead, self.with_context(default_team_id=team))._read_group_stage_ids(stages, domain, order)
        stage_type = self._context.get("default_type", "lead")
        domain = [("stage_type", "=", stage_type)]
        if stage_type == "lead":
            domain = ["|", ("stage_type", "=", stage_type), ("stage_type", "=", False)]
        res = res.filtered_domain(domain)

        return res
