# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

from . import ir, party, product, web

__all__ = ['register']


def register():
    Pool.register(
        ir.Cron,
        web.ShopWooCommerceId,
        web.Shop,
        web.Sale,
        party.Party,
        party.Address,
        product.Category,
        product.Product,
        module='web_shop_woocommerce', type_='model')
    Pool.register(
        module='web_shop_woocommerce', type_='wizard')
    Pool.register(
        module='web_shop_woocommerce', type_='report')
    Pool.register(
        web.Shop_SaleShipmentCost,
        depends=['sale_shipment_cost'],
        module='web_shop_woocommerce', type_='model')
    Pool.register(
        product.Image,
        product.Product_Image,
        depends=['product_image'],
        module='web_shop_woocommerce', type_='model')
