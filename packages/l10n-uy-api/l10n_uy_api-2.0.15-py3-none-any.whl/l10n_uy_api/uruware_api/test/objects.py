# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

class Object(object):
    pass

class Tax(object):
    def __init__(self, amount):
        self.amount = amount
        self.taxable_base = None
        self.aliquot = None

TAX_TYPES = {
2: 'minimo',
3: 'basico'
}
class UruwareTax(Tax):
    def __init__(self, amount, taxable_base, tax_type):
        super(UruwareTax, self).__init__(amount)
        self.taxable_base = taxable_base
        self._tax_type = tax_type

    @property
    def tax_type(self):
        return self._tax_type

    @tax_type.setter
    def tax_type(self, value):
        if value not in TAX_TYPES:
            raise AttributeError("El codigo de impuesto no corresponde a ningun impuesto")
        self._tax_type = TAX_TYPES.get(value)

class DocumentType(object):
    def __init__(self, cfe_type):
        self.cfe_type = cfe_type
        self.is_export = None

class ContingencyDocumentType(DocumentType):
    def __init__(self, cfe_type, serial, number):
        super(ContingencyDocumentType, self).__init__(cfe_type)
        self.serial = serial
        self.number = number

class Vat(object):
    def __init__(self, number, vat_type):
        self.number = number
        self.code = vat_type

    @staticmethod
    def validate_number():
        raise NotImplemented("Funcion no implementada para este tipo de documento")

class Partner(object):
    def __init__(self, name):
        self.name = name
        self.state = None
        self.city = None
        self.country_code = None
        self.country = None
        self.zip = None
        self.vat = None
        self.street = None
        self.dgi_sucursal_code = None
        self.email = None

class CodItem(object):

    def __init__(self, tpo_cod, cod):
        self.tpo_cod = tpo_cod
        self.cod = cod

class InvoiceLine(object):

    def __init__(self, amount, invoice_indicator=None):
        self.amount = amount
        self.description = None
        self.tax = None
        self.quantity = None
        self.invoice_indicator = invoice_indicator
        self.uom_code = None
        self.unit_price = None
        self.include_tax = None
        self.cod_item = None
        self.perceptions = None

class Perception(object):

    def __init__(self, code, taxable_base, amount, percentage=None):
        self.code = code
        self.taxable_base = taxable_base
        self.amount = amount
        self.percentage = percentage

class PickingLine(object):

    def __init__(self, description, quantity):
        self.description = description
        self.quantity = quantity
        self.uom_code = None
        self.description_extra = None

class ReceiptLine(object):

    def __init__(self, amount, invoice_indicator, description, quantity, unit_price):
        self.amount = amount
        self.invoice_indicator = invoice_indicator
        self.description = description
        self.quantity = quantity
        self.uom_code = 'N/A'
        self.unit_price = unit_price


INVOICE_TYPES = [
    'invoice',
    'refund',
    'debit_note'
]
class Invoice(object):
    def __init__(self, invoice_type):
        self.date = None
        self.date_due = None
        self.invoice_lines = []
        self.uuid = None
        self._invoice_type = invoice_type
        self.payment_method = None
        self.include_tax = None
        self.partner = None
        self.transport_type = None
        self.cfe_serial = None
        self.cfe_number = None
        self.cfe_code = None
        self.cfe_type = None
        self.document_type = None
        self.currency = None
        self.currency_rate = None
        self.origin = []
        self.origin_description = None
        self.description = None
        self.incoterm_code = None
        self.sale_mode_code = None
        self.transport_route_code = None
        self.imeba = False

    @property
    def invoice_type(self):
        return self._invoice_type

    @invoice_type.setter
    def invoice_type(self, value):
        if value not in INVOICE_TYPES:
            raise AttributeError("El tipo de comprobante no es valido")

class ConnectionData(object):
    def __init__(self):
        self.url = None
        self.user = None
        self.password = None
        self.terminal_code = None
        self.commerce_code = None
        self.sucursal_code = None
        self.timeout = None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
