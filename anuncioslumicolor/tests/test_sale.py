from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from .common import AnuncioslumicolorCase


@tagged("post_install", "-at_install")
class TestSale(AnuncioslumicolorCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = cls.env.ref("base.user_demo")
        cls.env = cls.env(user=cls.test_user)
        cls.group_allow_sale_products = cls.env.ref("anuncioslumicolor.group_allow_sale_products")
        cls.group_discount_per_so_line = cls.env.ref("product.group_discount_per_so_line")
        cls.test_user.groups_id |= cls.group_discount_per_so_line

    def test_01_modify_price_unit(self):
        """Testing that the user can't sell products with more than 10% of the price marked on he price list,
        in this case we modify the price_unit"""
        sale_order = self.create_sale_order(self.customer)
        # Verify that creating a sale without any modification does not give an error.
        self.create_new_sale_order_line_form(sale_order, self.product)
        error_msg = "Unable to make the sale due to underselling the product, contact sales manager"
        with self.assertRaisesRegex(UserError, error_msg):
            # A sale is created by changing the price unit
            self.create_new_sale_order_line_form(sale_order, self.product, price=600)
        # Verify that adding the user at the group can make the sale order
        self.test_user.groups_id |= self.group_allow_sale_products
        with Form(sale_order) as order:
            with order.order_line.edit(0) as line:
                line.price_unit = 600
        sale_order_line = sale_order.order_line[0]
        self.assertEqual(sale_order_line.price_unit, 600)

    def test_02_add_more_discount_than_10(self):
        """Testing that the user can't sell products with more than 10% of discount,
        in this case we add a discount greater than 10"""
        sale_order = self.create_sale_order(self.customer)
        error_msg = "Unable to make the sale due to underselling the product, contact sales manager"
        with self.assertRaisesRegex(UserError, error_msg):
            # A sale is created by adding more discount than 10%
            self.create_new_sale_order_line_form(sale_order, self.product, discount=15)

    def test_03_modify_price_add_discount(self):
        """Testing that the user can't sell products with more than 10% of discount,
        in this case we modify the price_unit and add a discount in total the price drops more than 10%."""
        sale_order = self.create_sale_order(self.customer)
        error_msg = "Unable to make the sale due to underselling the product, contact sales manager"
        with self.assertRaisesRegex(UserError, error_msg):
            # A sale is created by changing the price unit and adding a discount
            self.create_new_sale_order_line_form(sale_order, self.product, price=700, discount=5)
