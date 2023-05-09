from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # The default parameter was redefined to set the user who is creating the contact in the field.
    user_id = fields.Many2one(default=lambda self: self.env.user)
    can_produce_without_advance = fields.Boolean(default=False)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = list(args or [])
        if not self.env.user.has_group("anuncioslumicolor.group_allow_see_all_contacts"):
            args += [("user_id", "=", self.env.user.id)]
        return super().name_search(name, args, operator, limit)
