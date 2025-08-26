# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from urllib.parse import urlparse, urlunparse

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.tools import slugify

from .web import ShopWooCommerceIdMixin


class Category(ShopWooCommerceIdMixin, metaclass=PoolMeta):
    __name__ = 'product.category'

    woocommerce_tax_class = fields.Char("WooCommerce Tax Class",
        states={
            'invisible': ~Eval('accounting', False),
            })

    def get_woocommerce_entity(self):
        values = {
            'name': self.name,
            'slug': slugify(self.name).lower(),
            'parent': 0,
            }
        if self.parent:
            if self.parent.woocommerce_id:
                values['parent'] = self.parent.woocommerce_id
            else:
                return
        return values


class Product(ShopWooCommerceIdMixin, metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._woocommerce_html_fields |= {'description', 'short_description'}

    @property
    def woocommerce_tax_class(self):
        if self.account_category:
            parent = self.account_category
            while parent:
                if parent.woocommerce_tax_class:
                    return parent.woocommerce_tax_class
                parent = parent.parent
            return ''

    def woocommerce_disable_data(self, shop):
        return {
            'status': 'private',
            'catalog_visibility': 'hidden',
            }

    def get_woocommerce_entity(self):
        short_description = description = (
            self.web_shop_description or self.description or '')
        lines = description.splitlines()
        if len(lines) > 1:
            short_description = lines[0]
            description = '\n'.join(lines[1:])

        list_price = self.list_price or Decimal(0)
        sale_price = self.get_sale_price([self], 0)[self.id] or Decimal(0)
        if sale_price > list_price:
            list_price = sale_price
        values = {
            'name': self.name,
            'type': 'simple',
            'regular_price': str(list_price),
            'description': description,
            'short_description': short_description,
            'status': 'publish',
        }
        if sale_price < list_price:
            values['sale_price'] = sale_price
        if self.type != 'service':
            values['manage_stock'] = True
            values['stock_quantity'] = self.forecast_quantity
        if self.code:
            values['sku'] = self.code
        categories = []
        for category in self.categories:
            if category.woocommerce_id:
                categories.append({'id': category.woocommerce_id})
        values['categories'] = categories
        tax_class = self.woocommerce_tax_class
        if tax_class is not None:
            values['tax_class'] = tax_class
        return values


class Image(ShopWooCommerceIdMixin, metaclass=PoolMeta):
    __name__ = 'product.image'

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        to_clear = []
        for images, values in zip(actions, actions):
            if values.keys() & {'image', 'template', 'web_shop'}:
                to_clear.extend(images)

        super().write(*args)

        cls.clear_woocommerce_id(to_clear)


class Product_Image(metaclass=PoolMeta):
    __name__ = 'product.product'

    def woocommerce_image_url_args(self):
        return {
            's': 1024,
            }

    @property
    def woocommerce_extension(self):
        return '.jpg'

    @classmethod
    def woocommerce_image_pattern(cls):
        return {
            'web_shop': True,
        }

    @classmethod
    def add_woocommerce_extension(cls, url, extension):
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        # Test if last path is not /
        if path_parts[-1]:
            path_parts[-1] += extension
        else:
            path_parts[-2] += extension
        new_path = "/".join(path_parts)
        nova_url = urlunparse(parsed._replace(path=new_path))
        return nova_url

    def get_woocommerce_entity(self):
        pool = Pool()
        Product = pool.get('product.product')
        values = super().get_woocommerce_entity()
        images = []
        pattern = Product.woocommerce_image_pattern()
        for index, image in enumerate(self.get_images(pattern)):
            if not image.woocommerce_id:
                url_args = self.woocommerce_image_url_args()
                url_args.update({
                    '_external': True,
                    'i': index,
                    })
                image_url = self.get_image_url(**url_args)
                if not image_url:
                    continue
                # Woocommerce requires an extension to be set to properly
                # import the file. Otherwise image is not correctly parsed
                image_url = Product.add_woocommerce_extension(
                    image_url, self.woocommerce_extension)
                images.append({'src': image_url})
        values['images'] = images
        return values

    def store_woocommerce_values(self, response):
        pool = Pool()
        Image = pool.get('product.image')
        super().store_woocommerce_values(response)

        tryton_images = list(self.get_images(self.woocommerce_image_pattern()))
        woo_images = response.get('images', [])
        to_save = []
        for image, woo_image in zip(tryton_images, woo_images):
            if not image.woocommerce_id:
                image.woocommerce_id = woo_image['id']
                to_save.append(image)
        if to_save:
            Image.save(to_save)
