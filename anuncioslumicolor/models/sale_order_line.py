from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image = fields.Image(max_width=128, max_height=128)

    def _check_discount(self):
        if self.env.user.has_group("anuncioslumicolor.group_allow_sale_products"):
            return True

        allowed_discount = float(
            self.env["ir.config_parameter"].sudo().get_param("anuncioslumicolor.max_allowed_so_line_discount") or "0"
        )
        for line in self.filtered("product_id"):
            price_subtotal = line.price_subtotal
            lst_price = line._get_display_price() * line.product_uom_qty
            diff = 100 * (lst_price - price_subtotal) / lst_price if lst_price else 0
            if diff > allowed_discount:
                raise UserError(_("Unable to make the sale due to underselling the product, contact sales manager"))
        return True

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_discount()
        return lines

    def write(self, values):
        res = super().write(values)
        self._check_discount()
        return res
