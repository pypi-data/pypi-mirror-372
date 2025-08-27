#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from l10n_uy_api.uruware_api.manager.manager import Manager
from . import objects
import random
import unittest.mock as mock


MESSAGE_ERROR_CFC = 'Ya existe un CFE con el folio indicado pero diferente UUID.'
MAX_NUMBER_CFC = 999999


class TestUruware(unittest.TestCase):

    def setUp(self):
        self.connection_data = objects.ConnectionData()
        self.connection_data.url = 'https://test.ucfe.com.uy/inbox115_2/cfeservice.svc?singleWsdl'
        self.connection_data.user = 'FC-4@217628780017'
        self.connection_data.password = '/6lt8QG3tivnjJ4twcIWpQ=='
        self.connection_data.commerce_code = 'TRIBOL-582'
        self.connection_data.sucursal_code = 1
        self.connection_data.terminal_code = 'FC-4'
        self.connection_data.timeout = '30000'

        vat = objects.Vat(217628780017, 2)
        self.emisor = objects.Partner("Nexit")
        self.emisor.vat = vat
        self.emisor.state = 'Montevideo'
        self.emisor.name = 'Nexit'
        self.emisor.city = 'Montevideo'
        self.emisor.street = 'Bv.España 2579'
        self.emisor.dgi_sucursal_code = 1

    # ObtenerPdf
    def test_get_document_report(self):

        # ENVIO DE COMPROBANTE

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        Manager(self.connection_data, comprobante, self.emisor).send_document()

        connection_data = objects.ConnectionData()
        connection_data.url = 'https://test.ucfe.com.uy/query116_2/WebServicesFE.svc?wsdl'
        connection_data.user = 'FC-4@217628780017'
        connection_data.password = '/6lt8QG3tivnjJ4twcIWpQ=='
        connection_data.commerce_code = 'TRIBOL-582'
        connection_data.sucursal_code = 1
        connection_data.terminal_code = 'FC-4'
        connection_data.timeout = '30000'

        report = Manager(connection_data, comprobante, self.emisor).get_document_report()
        assert '%PDF' in report.decode('latin-1')
    
    # ObtenerPdfConParametros
    def test_get_document_report_with_parameters(self):

        # ENVIO DE COMPROBANTE

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78
        line1.cod_item = objects.CodItem('INT1', 'COD1')

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22
        line2.cod_item = objects.CodItem('INT1', 'COD2')

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        Manager(self.connection_data, comprobante, self.emisor).send_document()

        connection_data = objects.ConnectionData()
        connection_data.url = 'https://test.ucfe.com.uy/query116_2/WebServicesFE.svc?wsdl'
        connection_data.user = 'FC-4@217628780017'
        connection_data.password = '/6lt8QG3tivnjJ4twcIWpQ=='
        connection_data.commerce_code = 'TRIBOL-582'
        connection_data.sucursal_code = 1
        connection_data.terminal_code = 'FC-4'
        connection_data.timeout = '30000'

        report = Manager(connection_data, comprobante, self.emisor).get_document_report_parameters(['reporte'], ['codigo'])
        assert '%PDF' in report.decode('latin-1')

    # GenerarImagen
    def test_get_document_report_image(self):

        # ENVIO DE COMPROBANTE

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        Manager(self.connection_data, comprobante, self.emisor).send_document()

        connection_data = objects.ConnectionData()
        connection_data.url = 'https://test.ucfe.com.uy/query116_2/WebServicesFE.svc?wsdl'
        connection_data.user = 'FC-4@217628780017'
        connection_data.password = '/6lt8QG3tivnjJ4twcIWpQ=='
        connection_data.commerce_code = 'TRIBOL-582'
        connection_data.sucursal_code = 1
        connection_data.terminal_code = 'FC-4'
        connection_data.timeout = '30000'

        report = Manager(connection_data, comprobante, self.emisor).get_document_report(image=True)
        assert 'PNG' in report.decode('latin-1')
    
    # GenerarImagenConParametros
    def test_get_document_report_image_with_parameters(self):

        # ENVIO DE COMPROBANTE

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78
        line1.cod_item = objects.CodItem('INT1', 'COD1')

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22
        line2.cod_item = objects.CodItem('INT1', 'COD2')

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        Manager(self.connection_data, comprobante, self.emisor).send_document()

        connection_data = objects.ConnectionData()
        connection_data.url = 'https://test.ucfe.com.uy/query116_2/WebServicesFE.svc?wsdl'
        connection_data.user = 'FC-4@217628780017'
        connection_data.password = '/6lt8QG3tivnjJ4twcIWpQ=='
        connection_data.commerce_code = 'TRIBOL-582'
        connection_data.sucursal_code = 1
        connection_data.terminal_code = 'FC-4'
        connection_data.timeout = '30000'

        report = Manager(connection_data, comprobante, self.emisor).get_document_report_parameters(['reporte'], ['codigo'], image=True)
        assert 'PNG' in report.decode('latin-1')

    # 6.2.2.1 Ejemplo para e-Factura
    def test_eFact_cfe_invoice(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo para e-Factura con cobranza
    def test_eFact_cfe_invoice_receipt(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea de pago
        line1 = objects.ReceiptLine(10000, 6, "Pago de factura", 1, 10000)

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '111'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1]
        comprobante.refund_info = refund
        comprobante.currency = 'UYU'
        comprobante.include_tax = True
        comprobante.payment_method = "1"
        comprobante.own_collection = True

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo para e-Factura con impuesto de exportacion
    def test_eFact_cfe_invoice_with_tax_exportation(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=10)
        line2.description = "Con impuesto de exportacion"
        line2.description_extra = "Con impuesto de exportacion"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # X.X.X.X Ejemplo para e-Factura exportacion zona franca ( no se encuentra en manual)
    def test_eFact_zona_franca_cfe_invoice(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(100, invoice_indicator=10)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 0.0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo para e-Factura con descuento
    def test_eFact_cfe_invoice_with_discount(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(53437.5, invoice_indicator=3)
        line1.description = "BCAA 1400   180 cáñpsulas"
        line1.quantity = 150
        line1.discount = 5.0
        line1.discount_amount = 2812.50
        line1.unit_price = 375
        line1.tax = 11756.25

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.7.1 Ejemplo para e-Boleta de entrada
    def test_eBoleta_cfe_invoice(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea no gravada
        line1 = objects.InvoiceLine(122, invoice_indicator=15)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 122
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '151'
        comprobante.date = '2017-08-24'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eBoleta'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)
    
    # 6.2.7.1 Ejemplo para e-Boleta de entrada
    def test_eBoleta_cfe_invoice_imeba(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea no gravada
        line1 = objects.InvoiceLine(122, invoice_indicator=15)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 122
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '151'
        comprobante.date = '2017-08-24'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eBoleta'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'
        comprobante.imeba = True

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.1.1 Ejemplo para e-Ticket con pasaporte
    def test_eTck_cfe_invoice_with_passport(self):
        # partner factura
        partner_vat = objects.Vat(33241542, 5)
        invoice_partner = objects.Partner("Cliente prueba con PASAPORTE")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Cliente prueba con PASAPORTE'
        invoice_partner.city = 'Blumenau'
        invoice_partner.street = 'Carimbo 1122'
        invoice_partner.country_code = 'BR'
        invoice_partner.state = 'Santa Catarina'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo para e-Ticket para un partner sin vat
    def test_eTck_cfe_invoice_without_vat(self):
        # partner factura
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = False
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.1.1 Ejemplo para e-Ticket
    def test_eTck_cfe_invoice(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Idem 6.2.1.1 Ejemplo para e-Ticket con Exento
    def test_eTck_cfe_invoice_exempt(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(1000, invoice_indicator=1)
        line1.description = "Prueba Exento"
        line1.quantity = 1
        line1.unit_price = 1000
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.1.2 Ejemplo para e-Ticket venta por cuenta ajena
    def test_eTck_cfe_invoice_alien(self):
        # partner factura
        partner_vat = objects.Vat(123456, 4)
        invoice_partner = objects.Partner("Uruware Paraguay S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'PY'
        invoice_partner.country = 'Paraguay'

        line1 = objects.InvoiceLine(50000, invoice_indicator=3)
        line1.description = "Prueba de detalle"
        line1.quantity = 50
        line1.unit_price = 1000
        line1.tax = 9016.39
        line1.include_tax = True

        mandatario_vat = objects.Vat(215404940014, 2)
        mandatario = objects.Partner("Uruware")
        mandatario.vat = mandatario_vat
        mandatario.country_code = 'UY'

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '131'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.include_tax = True
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'
        comprobante.fiscal_data = mandatario

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.1.3 Ejemplo para nota de credito de e-Ticket
    def test_eTck_cfe_refund(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(122, invoice_indicator=3)
        line1.description = "Desarrollo de soporte logico"
        line1.quantity = 1
        line1.unit_price = 122
        line1.tax = 22
        line1.include_tax = True

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '101'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '102'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.include_tax = True
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1]
        comprobante.refund_info = refund
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.3.1 Ejemplo para e-Factura exportacion con documento uruguayo
    def test_eFact_cfe_invoice_exportation_for_uyu_partner(self):
        # partner factura
        partner_vat = objects.Vat(213866340011, 2)
        invoice_partner = objects.Partner("CANAL 10 SAETA")
        invoice_partner.vat = partner_vat
        invoice_partner.street = 'Lorenzo Carnelli 1234'
        invoice_partner.country_code = 'UY'
        invoice_partner.name = 'CANAL 10 SAETA'
        invoice_partner.city = 'Montevideo'
        invoice_partner.state = 'Montevideo'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'
        invoice_partner.country = 'Uruguay'
        invoice_partner.zip = '11200'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(60000, invoice_indicator=10)
        line1.description = "Articulos de consumo"
        line1.quantity = 150
        line1.unit_price = 400
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '121'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact_Exp'
        comprobante.incoterm_code = 'N/A'
        comprobante.sale_mode_code = 1
        comprobante.transport_route_code = 1
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.3.1 Ejemplo para e-Factura exportacion
    def test_eFact_cfe_invoice_exportation(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 4)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware'
        invoice_partner.city = 'Beijing'
        invoice_partner.street = 'Tayuan Office Building 1-1-2 (100600)'
        invoice_partner.country_code = 'CN'
        invoice_partner.country = 'China'
        invoice_partner.state = 'Beijing'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(60000, invoice_indicator=10)
        line1.description = "Articulos de consumo"
        line1.quantity = 150
        line1.unit_price = 400
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '121'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact_Exp'
        comprobante.incoterm_code = 'N/A'
        comprobante.sale_mode_code = 1
        comprobante.transport_route_code = 1
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.4.1 Ejemplo para un e-Remito
    def test_eRem(self):

        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.PickingLine("Test remito", 0)
        line1.description_extra = "Descripcion extra"
        line1.quantity = 3.0

        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '181'
        comprobante.date = '2015-01-31'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eRem'
        comprobante.transport_type = 1
        comprobante.picking_lines = [line1]

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.4.2 Ejemplo para una correcion de e-Remito
    def test_eRem_correccion(self):

        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.PickingLine("Test remito", 0)
        line1.description_extra = "Descripcion extra"
        line1.quantity = 3.0

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '181'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = 'Se corrige total trasladado'
        refund.refund_invoices = [refund_invoice]

        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '181'
        comprobante.date = '2015-01-31'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eRem'
        comprobante.picking_lines = [line1]
        comprobante.transport_type = 1
        comprobante.refund_info = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # TODO: Falta implementar e-remito de exportación y hacer los tests

    # 6.2.5.1 Ejemplo para un e-Remito exportacion
    # def test_eRem_exportacion(self):
    #     partner_vat = objects.Vat(215404940014, 4)
    #     invoice_partner = objects.Partner("Uruware S.A.")
    #     invoice_partner.vat = partner_vat
    #     invoice_partner.name = 'Uruware'
    #     invoice_partner.city = 'Beijing'
    #     invoice_partner.street = 'Tayuan Office Building 1-1-2 (100600)'
    #     invoice_partner.country_code = 'CN'
    #     invoice_partner.country = 'China'
    #     invoice_partner.state = 'Beijing'
    #     invoice_partner.email = 'lbaldi@openpyme.com.ar'

    #     # creamos linea gravada tasa basica
    #     line1 = objects.InvoiceLine(150000, invoice_indicator=8)
    #     line1.description = "Lana cruda"
    #     line1.quantity = 1000
    #     line1.unit_price = 150000
    #     line1.tax = 0

    #     # creamos factura
    #     comprobante = objects.Invoice('invoice')
    #     comprobante.cfe_code = '124'
    #     comprobante.date = '2015-01-31'
    #     comprobante.partner = invoice_partner
    #     comprobante.cfe_type = 'eRem_Exp'
    #     comprobante.transport_type = 1
    #     comprobante.sale_mode_code = 1
    #     comprobante.transport_route_code = 1
    #     comprobante.invoice_lines = [line1]
    #     comprobante.currency = 'UYU'

    #     msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

    #     assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo para un e-Resguardo con referencia
    def test_eRes_with_reference(self):
        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 19800
        retention_detail1.percentage_retention = 100
        retention_detail1.taxable_base = 90000
        retention_detail1.get_tax.return_value = 22

        retention_detail2 = mock.Mock()
        retention_detail2.amount = 2200
        retention_detail2.percentage_retention = 100
        retention_detail2.taxable_base = 10000
        retention_detail2.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.retention_code = 2183114
        retention1.percentage_retention = 100
        retention1.retention_detail = [retention_detail1, retention_detail2]
        retention1.get_amount.return_value = 22000
        retention1.get_taxable_base.return_value = 100000

        retention_detail3 = mock.Mock()
        retention_detail3.amount = 10000
        retention_detail3.percentage_retention = 100
        retention_detail3.taxable_base = 10000
        retention_detail3.get_tax.return_value = 22

        retention2 = mock.Mock()
        retention2.percentage_retention = 100
        retention2.retention_code = 2183121
        retention2.retention_detail = [retention_detail3]
        retention2.get_amount.return_value = 10000
        retention2.get_taxable_base.return_value = 10000

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '182'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund_invoice_2 = objects.Invoice('invoice')
        refund_invoice_2.cfe_code = '111'
        refund_invoice_2.date = '2018-01-02'
        refund_invoice_2.cfe_serial = 'A'
        refund_invoice_2.cfe_number = '245'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice, refund_invoice_2]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '182'
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1, retention2]
        comprobante.refund_info = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.6.1 Ejemplo para un e-Resguardo
    def test_eRes(self):

        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 19800
        retention_detail1.percentage_retention = 100
        retention_detail1.taxable_base = 90000
        retention_detail1.get_tax.return_value = 22

        retention_detail2 = mock.Mock()
        retention_detail2.amount = 2200
        retention_detail2.percentage_retention = 100
        retention_detail2.taxable_base = 10000
        retention_detail2.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.percentage_retention = 100
        retention1.retention_code = 2183114
        retention1.retention_detail = [retention_detail1, retention_detail2]
        retention1.get_amount.return_value = 22000
        retention1.get_taxable_base.return_value = 100000

        retention_detail3 = mock.Mock()
        retention_detail3.amount = 10000
        retention_detail3.taxable_base = 10000
        retention_detail3.get_tax.return_value = 22

        retention2 = mock.Mock()
        retention2.retention_code = 2183121
        retention2.percentage_retention = 100
        retention2.retention_detail = [retention_detail3]
        retention2.get_amount.return_value = 10000
        retention2.get_taxable_base.return_value = 10000

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '182'
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1, retention2]

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # e-Resguardo con referencias
    def test_eRes_with_references(self):
        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 2200
        retention_detail1.percentage_retention = 100
        retention_detail1.taxable_base = 10000
        retention_detail1.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.retention_code = 2183114
        retention1.percentage_retention = 100
        retention1.retention_detail = [retention_detail1]
        retention1.get_amount.return_value = 2200
        retention1.get_taxable_base.return_value = 10000

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '182'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '182'
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1]
        comprobante.references = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # 6.2.6.2 Ejemplo para una correccion de e-Resguardo
    def test_eRes_refund(self):

        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 2200
        retention_detail1.percentage_retention = 100
        retention_detail1.taxable_base = 10000
        retention_detail1.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.retention_code = 2183114
        retention1.percentage_retention = 100
        retention1.retention_detail = [retention_detail1]
        retention1.get_amount.return_value = 2200
        retention1.get_taxable_base.return_value = 10000

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '182'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '182'
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1]
        comprobante.refund_info = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

    # Ejemplo con contingencia - CFC

    # 6.2.2.1 Ejemplo para e-Factura
    def test_eFact_cfc_invoice(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    def test_eFact_leyends(self):

        self.connection_data.legends_ids = (6, 0, [
            {
                'sending_legends': 'header',
                'obligatory_legend': 'Leyenda Header'
            },
            {
                'sending_legends': 'partner',
                'obligatory_legend': 'Leyenda Partner'
            },
            {
                'sending_legends': 'line',
                'obligatory_legend': 'Leyenda Line'
            },
        ])

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    def test_eFact_perceptions(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line = objects.InvoiceLine(1467.75, invoice_indicator=2)
        line.description = "Servicios de desarrollo"
        line.quantity = 5
        line.unit_price = 309
        line.tax = 146.775
        line.discount = 5
        line.discount_amount = 77.25
        
        perception1 = objects.Perception(
            code='2183229',
            taxable_base=1467.75,
            amount=22.016,
            percentage=1.5
        )
        perception2 = objects.Perception(
            code='2183220',
            taxable_base=146.775,
            amount=29.355,
            percentage=20
        )
        line.perceptions = [perception1, perception2]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = random.randint(1, MAX_NUMBER_CFC)
        comprobante.cfe_code = '211'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.7.1 Ejemplo para e-Boleta de entrada
    def test_eBoleta_cfc_invoice(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea no gravada
        line1 = objects.InvoiceLine(122, invoice_indicator=15)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 122
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '251'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2017-08-24'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eBoleta'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.1.1 Ejemplo para e-Ticket
    def test_eTck_cfc_invoice(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '201'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.1.2 Ejemplo para e-Ticket venta por cuenta ajena
    def test_eTck_cfc_invoice_alien(self):
        # partner factura
        partner_vat = objects.Vat(123456, 4)
        invoice_partner = objects.Partner("Uruware Paraguay S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'PY'
        invoice_partner.country = 'Paraguay'

        line1 = objects.InvoiceLine(50000, invoice_indicator=3)
        line1.description = "Prueba de detalle"
        line1.quantity = 50
        line1.unit_price = 1000
        line1.tax = 9016.39
        line1.include_tax = True


        mandatario_vat = objects.Vat(215404940014, 2)
        mandatario = objects.Partner("Uruware")
        mandatario.vat = mandatario_vat
        mandatario.country_code = 'UY'

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '231'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.include_tax = True
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'
        comprobante.fiscal_data = mandatario

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.1.3 Ejemplo para nota de credito de e-Ticket
    def test_eTck_cfc_refund(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(122, invoice_indicator=3)
        line1.description = "Desarrollo de soporte logico"
        line1.quantity = 1
        line1.unit_price = 122
        line1.tax = 22
        line1.include_tax = True

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '101'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '202'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.include_tax = True
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1]
        comprobante.refund_info = refund
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.3.1 Ejemplo para e-Factura exportacion
    def test_eFact_cfc_invoice_exportation(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 4)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware'
        invoice_partner.city = 'Beijing'
        invoice_partner.street = 'Tayuan Office Building 1-1-2 (100600)'
        invoice_partner.country_code = 'CN'
        invoice_partner.country = 'China'
        invoice_partner.state = 'Beijing'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(60000, invoice_indicator=10)
        line1.description = "Articulos de consumo"
        line1.quantity = 150
        line1.unit_price = 400
        line1.tax = 0

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '221'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact_Exp'
        comprobante.incoterm_code = 'N/A'
        comprobante.sale_mode_code = 1
        comprobante.transport_route_code = 1
        comprobante.invoice_lines = [line1]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.4.1 Ejemplo para un e-Remito
    def test_eRem_cfc(self):

        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.PickingLine("Test remito", 0)
        line1.description_extra = "Descripcion extra"
        line1.quantity = 3.0

        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '281'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eRem'
        comprobante.picking_lines = [line1]
        comprobante.transport_type = 1

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.4.2 Ejemplo para una correcion de e-Remito
    def test_eRem_correccion_cfc(self):

        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.PickingLine("Test remito", 0)
        line1.description_extra = "Descripcion extra"
        line1.quantity = 3.0

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '181'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = 'Se corrige total trasladado'
        refund.refund_invoices = [refund_invoice]

        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '281'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-01-31'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eRem'
        comprobante.picking_lines = [line1]
        comprobante.transport_type = 1
        comprobante.refund_info = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # TODO: Falta implementar e-remito de exportación y hacer los tests

    # 6.2.5.1 Ejemplo para un e-Remito exportacion
    # def test_eRem_exportacion_cfc(self):
    #     partner_vat = objects.Vat(215404940014, 4)
    #     invoice_partner = objects.Partner("Uruware S.A.")
    #     invoice_partner.vat = partner_vat
    #     invoice_partner.name = 'Uruware'
    #     invoice_partner.city = 'Beijing'
    #     invoice_partner.street = 'Tayuan Office Building 1-1-2 (100600)'
    #     invoice_partner.country_code = 'CN'
    #     invoice_partner.country = 'China'
    #     invoice_partner.state = 'Beijing'
    #     invoice_partner.email = 'lbaldi@openpyme.com.ar'

    #     # creamos linea gravada tasa basica
    #     line1 = objects.InvoiceLine(150000, invoice_indicator=8)
    #     line1.description = "Lana cruda"
    #     line1.quantity = 1000
    #     line1.unit_price = 150000
    #     line1.tax = 0

    #     # creamos factura
    #     comprobante = objects.Invoice('invoice')
    #     comprobante.cfe_code = '224'
    #     comprobante.document_type = 'cfc'
    #     comprobante.cfe_serial = 'XA'
    #     comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
    #     comprobante.date = '2015-01-31'
    #     comprobante.partner = invoice_partner
    #     comprobante.cfe_type = 'eRem_Exp'
    #     comprobante.transport_type = 1
    #     comprobante.sale_mode_code = 1
    #     comprobante.transport_route_code = 1
    #     comprobante.invoice_lines = [line1]
    #     comprobante.currency = 'UYU'

    #     msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

    #     assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.6.1 Ejemplo para un e-Resguardo
    def test_eRes_cfc(self):

        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 19800
        retention_detail1.percentage_retention = 10
        retention_detail1.taxable_base = 90000
        retention_detail1.get_tax.return_value = 22

        retention_detail2 = mock.Mock()
        retention_detail2.amount = 2200
        retention_detail2.percentage_retention = 10
        retention_detail2.taxable_base = 10000
        retention_detail2.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.retention_code = 2183114
        retention1.percentage_retention = 10
        retention1.retention_detail = [retention_detail1, retention_detail2]
        retention1.get_amount.return_value = 22000
        retention1.get_taxable_base.return_value = 100000

        retention_detail3 = mock.Mock()
        retention_detail3.amount = 10000
        retention_detail3.percentage_retention = 10
        retention_detail3.taxable_base = 10000
        retention_detail3.get_tax.return_value = 22

        retention2 = mock.Mock()
        retention2.retention_code = 2183121
        retention2.percentage_retention = 10
        retention2.retention_detail = [retention_detail3]
        retention2.get_amount.return_value = 10000
        retention2.get_taxable_base.return_value = 10000

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '282'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1, retention2]

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # 6.2.6.2 Ejemplo para una correccion de e-Resguardo
    def test_eRes_refund_cfc(self):

        partner_vat = objects.Vat(13353214, 3)
        invoice_partner = objects.Partner("Juan Perez")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Juan Perez'
        invoice_partner.country = 'Uruguay'
        invoice_partner.country_code = 'UY'

        retention_detail1 = mock.Mock()
        retention_detail1.amount = 2200
        retention_detail1.percentage_retention = 10
        retention_detail1.taxable_base = 10000
        retention_detail1.get_tax.return_value = 22

        retention1 = mock.Mock()
        retention1.retention_code = 2183114
        retention1.percentage_retention = 10
        retention1.retention_detail = [retention_detail1]
        retention1.get_amount.return_value = 2200
        retention1.get_taxable_base.return_value = 10000

        refund_invoice = objects.Invoice('invoice')
        refund_invoice.cfe_code = '182'
        refund_invoice.date = '2015-01-31'
        refund_invoice.cfe_serial = 'A'
        refund_invoice.cfe_number = '1234567'

        refund = objects.Object()
        refund.refund_reason = ''
        refund.refund_invoices = [refund_invoice]

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '282'
        comprobante.document_type = 'cfc'
        comprobante.cfe_serial = 'XA'
        comprobante.cfe_number = str(random.randint(1, MAX_NUMBER_CFC))
        comprobante.date = '2015-02-01'
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eResg'
        comprobante.currency = 'UYU'
        comprobante.retentions = [retention1]
        comprobante.refund_info = refund

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage) or msg.get('responseMsg') == MESSAGE_ERROR_CFC

    # Consulta de estado para un 6.2.2.1 Ejemplo para e-Factura
    def test_eFact_cfe_invoice_state(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)

        comprobante.cfe_serial = msg.get('responseBody').Resp.Serie
        comprobante.cfe_number = msg.get('responseBody').Resp.NumeroCfe

        msg_state = Manager(self.connection_data, comprobante, self.emisor).get_cfe_state()

        assert not msg_state.get('responseMsg')

    # Prueba de duplicidad de uuid
    # el segundo documento deberia dar el mismo nro de cfe
    # dado que deberia ser como una consulta.
    def test_duplicity(self):
        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.uuid = 'UUID_DUPLICADO'
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg_first = Manager(self.connection_data, comprobante, self.emisor).send_document()

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        line1 = objects.InvoiceLine(100, invoice_indicator=3)
        line1.description = "Prueba tasa basica"
        line1.quantity = 1
        line1.unit_price = 100
        line1.tax = 22

        line2 = objects.InvoiceLine(50, invoice_indicator=2)
        line2.description = "Prueba tasa minima"
        line2.quantity = 1
        line2.unit_price = 50
        line2.tax = 5

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.uuid = 'UUID_DUPLICADO'
        comprobante.cfe_code = '101'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eTck'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'

        msg_second = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert msg_first.get('responseBody').Resp.XmlCfeFirmado == msg_second.get('responseBody').Resp.XmlCfeFirmado

    def test_eFact_cfe_invoice_three_decimal_places(self):

        # partner factura
        partner_vat = objects.Vat(215404940014, 2)
        invoice_partner = objects.Partner("Uruware S.A.")
        invoice_partner.vat = partner_vat
        invoice_partner.name = 'Uruware S.A.'
        invoice_partner.city = 'Montevideo'
        invoice_partner.street = 'Bv.Espana 2579'
        invoice_partner.country_code = 'UY'
        invoice_partner.country = 'Uruguay'
        invoice_partner.email = 'lbaldi@openpyme.com.ar'

        # creamos linea gravada tasa basica
        line1 = objects.InvoiceLine(99, invoice_indicator=3)
        line1.description = "Servicios de desarrollo"
        line1.quantity = 1
        line1.unit_price = 99
        line1.tax = 21.78

        # creamos linea no facturable
        line2 = objects.InvoiceLine(0.22, invoice_indicator=6)
        line2.description = "Redondeo"
        line2.description_extra = "Redondeo Extra"
        line2.quantity = 1
        line2.unit_price = 0.22

        # creamos factura
        comprobante = objects.Invoice('invoice')
        comprobante.cfe_code = '111'
        comprobante.date = '2015-01-31'
        comprobante.payment_method = 1
        comprobante.partner = invoice_partner
        comprobante.cfe_type = 'eFact'
        comprobante.invoice_lines = [line1, line2]
        comprobante.currency = 'UYU'
        comprobante.decimal_places = 3

        msg = Manager(self.connection_data, comprobante, self.emisor).send_document()

        assert not (msg.get('responseMsg') or msg.get('responseBody').ErrorMessage)
