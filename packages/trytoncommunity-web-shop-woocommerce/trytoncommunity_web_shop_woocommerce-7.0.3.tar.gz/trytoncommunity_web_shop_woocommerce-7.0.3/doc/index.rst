Web Shop Woocommerce Module
###########################

The web_shop_woocomerce module provides the integration with `WooCommerce API`_.

.. _`WooCommerce API`: https://woocommerce.github.io/woocommerce-rest-api-docs/


The module creates by default two cron jobs:

* Upload products from Tryton to WooCommerce
* Download orders from WooCommerce to Tryton


The first one is responsible of creating new products and categories but also
uploading any change to the product and syncronizing stock levels. The second
is downloads 'on-hold' orders, creating the customer related data if needed.
Once the order is created in Tryton the status it's updated to processing.
When the shipments are sent, Tryton updates the WooComerce state of the
order to 'done'.

.. toctree::
   :maxdepth: 2

   configuration
