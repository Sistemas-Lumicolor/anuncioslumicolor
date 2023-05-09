from odoo.fields import Command
from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMRP(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_sale = cls.env.ref("base.res_partner_address_4")
        cls.partner_vendor = cls.env.ref("base.res_partner_2")
        cls.company = cls.env.company
        cls.payment_method_cash = cls.env.ref("l10n_mx_edi.payment_method_efectivo")
        cls.account_payment = cls.env["res.partner.bank"].create(
            {
                "acc_number": "123456789",
                "partner_id": cls.partner_sale.id,
            }
        )
        cls.product_4.unspsc_code_id = cls.env.ref("product_unspsc.unspsc_code_01010101")
        cls.payment_term = cls.env.ref("account.account_payment_term_30days")
        cls.company_partner = cls.env.ref("base.main_partner")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        route_manufacture = cls.warehouse.manufacture_pull_id.route_id.id
        cls.warehouse.mto_pull_id.route_id.active = True
        route_buy = cls.warehouse.buy_pull_id.route_id.id
        route_mto = cls.warehouse.mto_pull_id.route_id.id
        supplierinfo_1 = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.env.ref("product.product_product_1_product_template").id,
                "partner_id": cls.partner_vendor.id,
                "delay": 3,
            }
        )
        supplierinfo_2 = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.env.ref("product.product_product_2_product_template").id,
                "partner_id": cls.partner_vendor.id,
                "delay": 3,
            }
        )
        cls.product_4.write({"route_ids": [Command.set([route_manufacture, route_mto])]})
        cls.product_1.write(
            {
                "route_ids": [Command.set([route_buy, route_mto])],
                "seller_ids": [Command.set(supplierinfo_1.id)],
            }
        )
        cls.product_2.write(
            {
                "route_ids": [Command.set([route_buy, route_mto])],
                "seller_ids": [Command.set(supplierinfo_2.id)],
            }
        )

    def create_sale_order(self, partner, **line_kwargs):
        sale_order = Form(self.env["sale.order"])
        sale_order.partner_id = partner
        sale_order.project_name = "Test Project"
        sale_order.mrp_attachment_omit = True
        sale_order.delivery_days = 1
        sale_order = sale_order.save()
        self.create_so_line(sale_order, **line_kwargs)
        return sale_order

    def create_so_line(self, sale_order, product=None, quantity=5, price=150):
        if product is None:
            product = self.product_4
        with Form(sale_order) as so:
            with so.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = quantity
                line.tax_id.clear()

    def create_payment(self, invoice, amount=None):
        bank_journal = self.env["account.journal"].search([("type", "=", "bank")], limit=1)
        payment_register = Form(
            self.env["account.payment"].with_context(active_model="account.move", active_ids=invoice.ids)
        )
        payment_register.date = invoice.date
        payment_register.l10n_mx_edi_payment_method_id = self.env.ref("l10n_mx_edi.payment_method_efectivo")
        payment_register.journal_id = bank_journal
        if amount:
            payment_register.amount = amount
        payment = payment_register.save()
        payment.action_post()
        return payment

    def test_01_check_sale_mo_and_purchase(self):
        sale_order = self.create_sale_order(self.partner_sale)
        sale_order.action_confirm()
        mo = self.env["mrp.production"].search([("origin", "=", sale_order.name)])
        self.assertEqual(mo.origin, sale_order.name)
        self.assertEqual(mo.show_produce, False)
        context_sale = {
            "active_model": "sale.order",
            "active_ids": [sale_order.id],
            "active_id": sale_order.id,
        }

        invoicing_wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context_sale)
            .create({"advance_payment_method": "delivered"})
        )
        invoicing_wizard.create_invoices()
        invoice = sale_order.invoice_ids[0]

        move_form = Form(invoice)
        move_form.l10n_mx_edi_payment_method_id = self.payment_method_cash
        move_form.invoice_payment_term_id = self.payment_term
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = 5
        invoice = move_form.save()
        invoice.action_post()
        invoice.invalidate_recordset()
        self.assertEqual(invoice.state, "posted")
        self.create_payment(invoice, 0.50)
        mo = self.env["mrp.production"].search([("origin", "=", sale_order.name)])
        self.assertEqual(mo.project_name, sale_order.project_name)
        self.assertEqual(mo.show_produce, True)
