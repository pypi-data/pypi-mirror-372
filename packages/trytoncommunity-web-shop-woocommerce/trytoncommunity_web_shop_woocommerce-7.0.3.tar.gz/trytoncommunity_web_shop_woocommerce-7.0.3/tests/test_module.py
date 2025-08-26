# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from contextlib import contextmanager

from trytond.modules.company.tests import create_company
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction


class WebShopWoocommerceTestCase(ModuleTestCase):
    'Test Web Shop Woocommerce module'
    module = 'web_shop_woocommerce'
    extras = ['product_image']

    @contextmanager
    def create_web_shop(self):
        pool = Pool()
        WebShop = pool.get('web.shop')
        Location = pool.get('stock.location')

        company = create_company()
        warehouse, = Location.search([('type', '=', 'warehouse')], limit=1)
        web_shop = WebShop(name="Web Shop")
        web_shop.company = company
        web_shop.currency = company.currency
        web_shop.warehouses = [warehouse]
        web_shop.type = 'woocommerce'
        web_shop.woocommerce_url = 'http://localhost'
        web_shop.woocommerce_consumer_key = 'test'
        web_shop.woocommerce_consumer_secret = 'test'
        web_shop.save()
        with Transaction().set_context(**web_shop.get_context()):
            yield web_shop

    @with_transaction()
    def test_woocommerce_id(self):
        pool = Pool()
        Category = pool.get('product.category')
        WooCommerceID = pool.get('web.shop.woocommerce_id')
        with self.create_web_shop() as web_shop:

            category = Category(name='Test')
            category.woocommerce_id = 1
            category.save()

            category = Category(category.id)
            self.assertEqual(category.woocommerce_id, 1)

            woocommerce_id, = WooCommerceID.search([])
            self.assertEqual(woocommerce_id.record, category)
            self.assertEqual(woocommerce_id.shop, web_shop)

        # Woocommerce id is empty when no context
        category = Category(category.id)
        self.assertIsNone(category.woocommerce_id)

        # ID is delete when category is deleted
        Category.delete([category])
        self.assertListEqual(WooCommerceID.search([]), [])


del ModuleTestCase
