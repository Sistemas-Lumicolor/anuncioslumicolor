from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    show_produce = fields.Boolean(default=False)
    project_name = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("origin"):
                vals["show_produce"] = True
            else:
                so = self.env["sale.order"].search([("name", "=", vals.get("origin"))])
                if so.partner_id.can_produce_without_advance:
                    vals["show_produce"] = True
        return super().create(vals_list)
