from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    mrp_attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Production Attachment",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    mrp_attachment_omit = fields.Boolean(
        "Omit production attachments",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    project_name = fields.Char(readonly=True, states={"draft": [("readonly", False)], "sent": [("readonly", False)]})
    delivery_days = fields.Integer(help="Enter the business days needed to deliver the product")

    def action_confirm(self):
        sales_need_attachment = self.filtered(
            lambda so: so.project_name and not so.mrp_attachment_omit and not so.mrp_attachment_ids
        )
        if sales_need_attachment:
            raise ValidationError(
                _(
                    "You need to confirm you will skip production attachments of this orders:\n\n%s",
                    "\n".join(sales_need_attachment.mapped("name")),
                )
            )
        res = super().action_confirm()
        for record in self:
            production_order = self.env["mrp.production"].search(
                [("origin", "=", record.name)], order="create_date desc", limit=1
            )

            if not production_order:
                continue
            production_order.write({"project_name": record.project_name})

            if record.mrp_attachment_omit:
                continue
            for attachment in record.mrp_attachment_ids:
                attachment.copy(
                    {
                        "res_model": production_order._name,
                        "res_id": production_order.id,
                    }
                )
        return res

    @api.onchange("delivery_days")
    def _onchange_delivery_days(self):
        for order in self:
            date_now = fields.Datetime.now()
            if order.delivery_days > 0:
                date_now = date_now + timedelta(days=order.delivery_days or 0.0)
            order.commitment_date = date_now
