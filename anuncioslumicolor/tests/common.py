from odoo.tests import Form, TransactionCase


class AnuncioslumicolorCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_4")
        cls.customer = cls.env.ref("base.res_partner_2")

    def create_sale_order(self, customer=None):
        """Method to create a new sale order

        :param customer: customer to whom a sales order is to be created, defaults to None
        :type customer: optional
        """
        if customer is None:
            customer = self.customer
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = customer
        sale_form.project_name = "undefined"
        sale_form.mrp_attachment_omit = True
        sale_form.delivery_days = 1
        return sale_form.save()

    def create_new_sale_order_line_form(self, sale_order, product=False, product_qty=1.0, price=0, discount=0):
        """Method to create a new sale order line

        :param sale_order: Purchase Order to which a new line will be added
        :type sale_order: sale.order obj
        :param product: Product to be sold, defaults to False
        :type product: bool, optional
        :param product_qty: Quantity of products to be purchased, defaults to 1.0
        :type product_qty: float, optional
        :param price: Price at which the product is offered; if it differs from the price list by 10%,
        a UserError is expected to be returned. defaults to 0
        :type price: int, optional
        :param discount: Discount that can be given to the product,
        this must not lower the price to more than 10% of the list price. defaults to 0
        :type discount: int, optional
        """
        if not product:
            product = self.product
        if not price:
            price = product.list_price
        with Form(sale_order) as order:
            with order.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = product_qty
                line.price_unit = price
                line.discount = discount
