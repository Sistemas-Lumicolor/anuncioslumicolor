from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_amount(self):
        """This overwrite is to determine if there is a partial payment,
        necessary to set show_produce fields in MRP."""
        res = super()._compute_amount()
        for invoice in self.filtered("invoice_origin"):
            mrp = self.env["mrp.production"].search(
                [("origin", "=", invoice.invoice_origin), ("show_produce", "=", False)]
            )
            mrp.write({"show_produce": invoice.amount_total != invoice.amount_residual})
        return res
