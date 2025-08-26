# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.modules.party.exceptions import InvalidPhoneNumber
from trytond.pool import Pool, PoolMeta

from .web import ShopWooCommerceIdMixin


class Party(ShopWooCommerceIdMixin, metaclass=PoolMeta):
    __name__ = 'party.party'

    @classmethod
    def create_from_woocommerce(cls, shop, values):
        pool = Pool()
        Address = pool.get('party.address')
        Mechanism = pool.get('party.contact_mechanism')
        party = cls()
        party.name = values['billing'].get('company')
        addresses = []
        invoice_address = Address.create_from_woocommerce(
            shop, values['billing'])
        invoice_address.invoice = True
        addresses.append(invoice_address)
        if not invoice_address.woocommerce_equal(shop, values['shipping']):
            shipment_address = Address.create_from_woocommerce(
                shop, values['shipping'])
            shipment_address.delivery = True
            addresses.append(shipment_address)
        else:
            invoice_address.delivery = True
        party.addresses = list(getattr(party, 'addresses', [])) + addresses
        if not party.name:
            party.name = party.addresses[0].party_name
        party.woocommerce_id = values['customer_id']
        mechanisms = []
        if values['billing'].get('email'):
            mechanism = Mechanism()
            mechanism.party = party
            mechanism.type = 'email'
            mechanism.value = mechanism.format_value(
                value=values['billing']['email'].lower(), type_='email')
            mechanism.invoice = True
            mechanisms.append(mechanism)
        if values['billing'].get('phone'):
            mechanism = Mechanism()
            mechanism.party = party
            mechanism.type = 'phone'
            mechanism.value = mechanism.format_value(
                value=values['billing']['phone'], type_='phone')
            mechanism.invoice = True
            try:
                mechanism.party.rec_name = party.name
                Mechanism.check_valid_phonenumber([mechanism])
            except InvalidPhoneNumber:
                mechanism.type = 'other'
            mechanisms.append(mechanism)
        party.contact_mechanisms = mechanisms
        party.save()
        return party


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    def woocommerce_equal(self, shop, values):
        new_address = self.create_from_woocommerce(shop, values)
        return (new_address.street == self.street
            and new_address.city == self.city
            and new_address.postal_code == self.postal_code)

    @classmethod
    def create_from_woocommerce(cls, shop, values):
        pool = Pool()
        Country = pool.get('country.country')
        Subdivision = pool.get('country.subdivision')
        address = cls()
        address.party_name = ' '.join(filter(bool, [
                        values['first_name'], values['last_name']]))
        address.street = '\n'.join(filter(bool, [
                        values['address_1'], values['address_2']]))
        address.city = values['city']
        address.postal_code = values['postcode']
        country = Country.search([
                ('code', '=', values['country']),
                ], limit=1)
        if country:
            address.country, = country
            subdivision = Subdivision.search([
                    ('code', '=', '%s-%s' % (
                            address.country.code, values['state'])),
                    ], limit=1)
            if subdivision:
                address.subdivision, = subdivision
            else:
                address.subdivision = None
        else:
            address.country = None
            address.subdivision = None
        return address
