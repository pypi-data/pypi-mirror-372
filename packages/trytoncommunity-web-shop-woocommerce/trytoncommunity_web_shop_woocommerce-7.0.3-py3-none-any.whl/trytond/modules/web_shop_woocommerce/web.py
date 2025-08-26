# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging
import re
from decimal import Decimal

import dateutil
from woocommerce import API

from trytond.config import config
from trytond.exceptions import UserError
from trytond.i18n import gettext, lazy_gettext
from trytond.model import Model, ModelSQL, Unique, fields
from trytond.model.modelstorage import RequiredValidationError
from trytond.modules.product import round_price
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.tools import grouped_slice
from trytond.transaction import Transaction

from .exceptions import MissingParentsError, WooCommerceError

logger = logging.getLogger(__name__)

API_CHUNK = config.getint('web_shop_woocommerce', 'api_chunk', default=100)


class ShopWooCommerceId(ModelSQL):
    "Web Shop WooCommerce ID"
    __name__ = 'web.shop.woocommerce_id'

    record = fields.Reference("Record", 'get_records', required=True)
    shop = fields.Many2One('web.shop', "Web Shop", required=True)
    woocommerce_id = fields.Integer("WooCommerce ID", required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('record_unique', Unique(t, t.record, t.shop),
                'web_shop_woocommerce.msg_id_record_unique'),
            ]

    @classmethod
    def get_records(cls):
        pool = Pool()
        Model = pool.get('ir.model')
        models = [klass.__name__ for _, klass in pool.iterobject()
            if issubclass(klass, ShopWooCommerceIdMixin)]
        models = Model.search([
                ('model', 'in', models),
                ])
        return [(m.model, m.name) for m in models]


class ShopWooCommerceIdMixin:
    __slots__ = ()
    _woocommerce_html_fields = set()

    woocommerce_id = fields.Function(
        fields.Integer(
            lazy_gettext('web_shop_woocommerce.msg_woocommerce_id')),
        'get_woocommerce_id',
        setter='set_woocommerce_id')

    @classmethod
    def get_woocommerce_id(cls, records, name):
        pool = Pool()
        WoocommerceID = pool.get('web.shop.woocommerce_id')
        result = {}.fromkeys(r.id for r in records)
        shop = Transaction().context.get('woocommerce_shop', -1)
        for sub_records in grouped_slice(records):
            for woo_id in WoocommerceID.search([
                        ('shop', '=', shop),
                        ('record', 'in', map(str, sub_records)),
                        ]):
                result[woo_id.record.id] = woo_id.woocommerce_id
        return result

    @classmethod
    def set_woocommerce_id(cls, records, name, value):
        pool = Pool()
        WooCommerceId = pool.get('web.shop.woocommerce_id')

        shop = Transaction().context.get('woocommerce_shop', -1)
        if shop < 0:
            return
        for sub_records in grouped_slice(records):
            sub_records = list(sub_records)
            woo_ids = WooCommerceId.search([
                        ('shop', '=', shop),
                        ('record', 'in', map(str, sub_records)),
                        ])
            if not woo_ids:
                woo_ids = [
                    WooCommerceId(record=r, shop=shop, woocommerce_id=value)
                    for r in sub_records]
                WooCommerceId.save(woo_ids)
            else:
                WooCommerceId.write(woo_ids, {'woocommerce_id': value})

    @classmethod
    def clear_woocommerce_id(cls, records):
        pool = Pool()
        WooCommerceId = pool.get('web.shop.woocommerce_id')
        for sub_records in grouped_slice(records):
            woo_ids = WooCommerceId.search([
                    ('record', 'in', [str(r) for r in sub_records]),
                    ])
            if woo_ids:
                WooCommerceId.delete(woo_ids)

    @classmethod
    def delete(cls, records):
        cls.clear_woocommerce_id(records)
        super().delete(records)

    def store_woocommerce_values(self, response):
        pass


class Shop(metaclass=PoolMeta):
    __name__ = 'web.shop'

    woocommerce_url = fields.Char(
        "WooCommerce URL",
        states={
            'required': Eval('type') == 'woocommerce',
            'invisible': Eval('type') != 'woocommerce',
            })
    woocommerce_consumer_key = fields.Char(
        "WooCommerce Consumer Key",
        states={
            'required': Eval('type') == 'woocommerce',
            'invisible': Eval('type') != 'woocommerce',
            })
    woocommerce_consumer_secret = fields.Char(
        "WooCommerce Consumer Secret",
        states={
            'required': Eval('type') == 'woocommerce',
            'invisible': Eval('type') != 'woocommerce',
            })
    price_list = fields.Many2One('product.price_list', "Price List")
    shipping_product = fields.Many2One('product.product', "Shipping Product",
        domain=[
            ('salable', '=', True),
            ('type', '=', 'service'),
            ])

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.type.selection.append(('woocommerce', "WooCommerce"))

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('//page[@id="woocommerce"]', 'states', {
                    'invisible': Eval('type') != 'woocommerce',
                    }),
            ]

    def get_context(self):
        context = super().get_context()
        if self.type == 'woocommerce':
            context['woocommerce_shop'] = self.id
        if self.price_list:
            context['price_list'] = self.price_list.id
        return context

    @property
    def to_sync(self):
        result = super().to_sync
        if self.type == 'woocommerce':
            result = True
        return result

    @property
    def woocommerce_api_parameters(self):
        return {
            'url': self.woocommerce_url,
            'consumer_key': self.woocommerce_consumer_key,
            'consumer_secret': self.woocommerce_consumer_secret,
            'timeout': 30,
            }

    def get_woocommerce_api(self):
        return API(**self.woocommerce_api_parameters)

    @classmethod
    def woocommerce_response(cls, request):
        try:
            response = request.json()
        except Exception:
            raise WooCommerceError(
                gettext('web_shop_woocommerce.msg_sincronization_error',
                    response=request.text))
        if 'message' in response:
            raise WooCommerceError(
                gettext('web_shop_woocommerce.msg_sincronization_error',
                    response=response['message']))
        return response

    def woocommerce_tryton_record(self, model, woocommerce_id):
        "Return the tryton record of a giveen woocommerce id"
        pool = Pool()
        WooCommerceID = pool.get('web.shop.woocommerce_id')

        if issubclass(model, Model):
            model = model.__name__
        # TODO: Cache?
        table = WooCommerceID.__table__()
        query = table.select(table.id,
            where=(table.record.like(model + '%%')
                & (table.shop == self.id)
                & (table.woocommerce_id == woocommerce_id)))
        records = WooCommerceID.search([('id', 'in', query)], limit=1)
        if records:
            return records[0].record
        return None

    def woocommerce_compare_values(self, Model, woo_values, values):
        to_update = {}
        if not woo_values:
            return to_update
        for key, value in values.items():
            # Do not compare empty categories
            if value == []:
                continue
            woo_value = woo_values.get(key)
            if (isinstance(woo_value, list)
                    and woo_value
                    and isinstance(woo_value[0], dict)
                    and isinstance(value[0], dict)
                    and 'id' in woo_value[0]):
                if 'id' in value[0]:
                    # Use only ids to relation fields
                    woo_value = [{'id': w['id']} for w in woo_value]
                else:
                    # Only compare keys set on Tryton
                    tryton_keys = value[0].keys()
                    woo_value = [dict((k, v)
                            for k, v in x.items()
                            if k in tryton_keys
                            ) for x in woo_value]
            if woo_value != value:
                if (key in Model._woocommerce_html_fields
                        and not re.search(r'<[^>]+>', value)):
                    # Do not update empty html fields
                    if not value.strip() and woo_value in {'', '</p>\n'}:
                        continue
                    # Do not update different html values in woo commerce
                    if woo_value == f'<p>{value}</p>\n':
                        continue
                to_update[key] = value
        return to_update

    def woocommerce_sync_records(self, Model, records, endpoint):
        wcapi = self.get_woocommerce_api()
        to_update = {}
        woo2tryton = {}
        latter = []

        while records:
            for record in records:
                entity = record.get_woocommerce_entity()
                if entity is None:
                    latter.append(record)
                    continue
                woo_id = record.woocommerce_id
                if not woo_id:
                    try:
                        response = self.woocommerce_response(
                            wcapi.post(endpoint, entity))
                        record.store_woocommerce_values(response)
                        record.woocommerce_id = response['id']
                    except WooCommerceError:
                        logger.exception(
                            "Error updating record %d", record.id)
                        continue
                else:
                    to_update[woo_id] = entity
                    woo2tryton[woo_id] = record
            Model.save(records)
            Transaction().commit()
            if latter and len(records) == len(latter):
                raise MissingParentsError(
                    gettext('web_shop_woocommerce.msg_missing_parents_error',
                        records=','.join([x.rec_name for x in latter])))
            logger.info("Created new records %d/%d", len(records), len(latter))
            records = latter
            latter = []

        logger.info("Getting existing records info")
        woo_values = {}
        for sub_ids in grouped_slice(list(to_update.keys()), API_CHUNK):
            params = {
                'include': ','.join(map(str, sub_ids)),
                'per_page': API_CHUNK,
                }
            response = self.woocommerce_response(
                wcapi.get(endpoint, params=params))
            for woo_record in response:
                woo_values[woo_record['id']] = woo_record

        logger.info("Comparing and updating values")
        for woo_id, values in to_update.items():
            to_update = self.woocommerce_compare_values(
                Model, woo_values.get(woo_id), values)
            if to_update:
                try:
                    response = self.woocommerce_response(
                        wcapi.post('%s/%d' % (endpoint, woo_id), to_update))
                    record = woo2tryton[response['id']]
                    record.store_woocommerce_values(response)
                except WooCommerceError:
                    logger.exception(
                        "Error updating record %d", woo_id)

    @classmethod
    def woocommerce_update_products(cls, shops=None):
        pool = Pool()
        Product = pool.get('product.product')
        Category = pool.get('product.category')

        if shops is None:
            shops = cls.search([
                    ('type', '=', 'woocommerce'),
                    ])
        cls.lock(shops)
        for shop in shops:
            with Transaction().set_context(**shop.get_context()):
                logger.info("Syncronizing categories for %s", shop.rec_name)
                shop.woocommerce_sync_records(
                    Category,
                    shop.get_categories(),
                    'products/categories')
                logger.info("Syncronizing products for %s", shop.rec_name)
                products, _, _ = shop.get_products()
                shop.woocommerce_sync_records(
                    Product,
                    products,
                    'products')

                logger.info("Removing products for %s", shop.rec_name)
                wcapi = shop.get_woocommerce_api()
                # Rebrowse to get proper context
                for removed in Product.browse(shop.products_removed):
                    if not removed.woocommerce_id:
                        continue
                    shop.woocommerce_response(
                        wcapi.post('products/%d' % (removed.woocommerce_id),
                            removed.woocommerce_disable_data(shop)))
                shop.products_removed = []
                # TODO: Manage category removal
                # shop.categories_removed = []
                logger.info("Finised syncronization for %s", shop.rec_name)

        cls.save(shops)

    def woocommerce_orders_params(self, page):
        return {
            'status': 'on-hold',
            'page': page,
            }

    def woocommerce_customer(self, order):
        pool = Pool()
        Party = pool.get('party.party')
        customer_id = order.get('customer_id', 0)
        email = order.get('billing', {}).get('email', '').lower()
        if customer_id != 0:
            party = self.woocommerce_tryton_record(Party, customer_id)
            if party:
                return party
        elif email:
            parties = Party.search([
                    ('contact_mechanisms', 'where', [
                            ('type', '=', 'email'),
                            ('value', '=', email),
                            ]),
                    ], limit=1)
            if parties:
                return parties[0]
        return Party.create_from_woocommerce(self, order)

    def woocommerce_sale(self, order):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        Currency = pool.get('currency.currency')

        sale = Sale()
        sale.company = self.company
        sale.web_shop = self
        # TODO: Remove id on 7.4 series as contraint is now shop dependant
        sale.web_id = '%s_%s' % (self.id, order['id'])
        sale.sale_date = dateutil.parser.isoparse(
            order['date_created_gmt']).date()
        sale.reference = order['number']
        currencies = Currency.search([
                ('code', '=', order['currency'])
                ], limit=1)
        if not currencies:
            currencies = Currency.search([
                    ('symbol', '=', order['currency_symbol'])
                    ], limit=1)
        if not currencies:
            raise UserError('missing currency')
        sale.currency, = currencies
        sale.party = self.woocommerce_customer(order)
        sale.on_change_party()
        if (not sale.invoice_address
                or not sale.invoice_address.woocommerce_equal(
                    self, order['billing'])):
            for address in sale.party.addresses:
                if address.woocommerce_equal(self, order['billing']):
                    sale.invoice_address = address
                    break
            else:
                invoice_address = Address.create_from_woocommerce(
                    self, order['billing'])
                invoice_address.party = sale.party
                invoice_address.save()
                sale.invoice_address = invoice_address
        if (not sale.shipment_address
                or not sale.shipment_address.woocommerce_equal(
                    self, order['shipping'])):
            for address in sale.party.addresses:
                if address.woocommerce_equal(self, order['shipping']):
                    sale.shipment_address = address
                    break
            else:
                shipment_address = Address.create_from_woocommerce(
                    self, order['shipping'])
                shipment_address.party = sale.party
                shipment_address.save()
                sale.shipment_address = shipment_address
        sale.comment = order.get('customer_note')

        lines = []
        for item in order['line_items']:
            line = self.woocommerce_sale_line(order, item, sale)
            if line:
                lines.append(line)
        if order.get('shipping_lines'):
            for item in order['shipping_lines']:
                line = self.woocommerce_shipping_line(order, item, sale)
                if line:
                    lines.append(line)
        sale.lines = lines
        return sale

    def woocommerce_sale_line(self, order, item, sale):
        pool = Pool()
        Product = pool.get('product.product')
        Line = pool.get('sale.line')

        line = Line()
        line.type = 'line'
        line.sale = sale
        line.product = self.woocommerce_tryton_record(
            Product, item['product_id'])
        if not line.product:
            line.description = item['name']
        line.quantity = item['quantity']
        line.on_change_product()
        line.unit_price = round_price(Decimal(str(item['price'])))
        return line

    def woocommerce_shipping_line(self, order, item, sale):
        pool = Pool()
        Line = pool.get('sale.line')

        if not self.shipping_product:
            raise RequiredValidationError(
                gettext('web_shop_woocommerce'
                    '.msg_missing_shipping_product',
                    shop=self.rec_name))

        line = Line()
        line.type = 'line'
        line.sale = sale
        line.product = self.shipping_product
        line.description = item['method_title']
        line.quantity = 1.0
        line.on_change_product()
        line.unit_price = round_price(Decimal(str(item['total'])))
        return line

    @classmethod
    def woocommerce_download_orders(cls, shops=None):
        pool = Pool()
        Sale = pool.get('sale.sale')

        if shops is None:
            shops = cls.search([
                    ('type', '=', 'woocommerce'),
                    ])
        cls.lock(shops)
        for shop in shops:
            sales = []
            with Transaction().set_context(**shop.get_context()):
                wcapi = shop.get_woocommerce_api()
                page = 1
                orders = shop.woocommerce_response(
                    wcapi.get(
                        'orders',
                        params=shop.woocommerce_orders_params(page)))
                while orders:
                    for order in orders:
                        sale = shop.woocommerce_sale(order)
                        if sale:
                            sales.append(sale)
                    page += 1
                    orders = shop.woocommerce_response(
                        wcapi.get(
                            'orders',
                            params=shop.woocommerce_orders_params(page)))
                Sale.save(sales)
                cls.woocommerce_confirm_orders(sales)
                shop.update_woocommerce_status(sales, 'processing')

    @classmethod
    def woocommerce_confirm_orders(cls, sales):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Sale.quote(sales)
        Sale.confirm(sales)

    def woocommerce_sale_id(self, sale):
        return sale.web_id.split('_')[1]

    def update_woocommerce_status(self, sales, status):
        wcapi = self.get_woocommerce_api()
        for sale in sales:
            self.woocommerce_response(
                wcapi.post(
                    'orders/%s' % self.woocommerce_sale_id(sale),
                    data={'status': status}))


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @property
    def woocommerce_completed(self):
        return self.shipment_state == 'sent'

    def set_shipment_cost(self):
        if self.web_shop and self.web_shop.type == 'woocommerce':
            return []
        return super().set_shipment_cost()

    @classmethod
    def process(cls, sales):
        to_check = []
        for sale in sales:
            if (sale.web_shop
                    and sale.web_shop.type == 'woocommerce'
                    and not sale.woocommerce_completed):
                to_check.append(sale)
        super().process(sales)
        for sale in to_check:
            if sale.woocommerce_completed:
                sale.web_shop.update_woocommerce_status([sale], 'completed')


class Shop_SaleShipmentCost(metaclass=PoolMeta):
    __name__ = 'web.shop'

    def woocommerce_shipping_line(self, order, item, sale):
        line = super().woocommerce_shipping_line(order, item, sale)
        # TODO compute based on carrier, not total
        line.shipment_cost = round_price(Decimal(str(item['total'])))
        return line
