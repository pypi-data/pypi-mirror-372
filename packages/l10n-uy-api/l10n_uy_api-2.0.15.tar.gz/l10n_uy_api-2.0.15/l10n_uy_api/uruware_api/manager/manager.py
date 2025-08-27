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
from ..connector import connector as conn
from . import req_body, ucfe_requirement
import math
from datetime import datetime
from random import choice
from xml.etree.ElementTree import Element, SubElement, tostring
from collections import defaultdict


# Cuidado de respetar el orden !!!!!!!!!
# En caso de cambiar el orden podria generar
# problemas al validar comprobantes en Uruware
# Ejemplo: Si previo a informar detalles enviamos
# las referencias no da un error diciendo que
# no se encuentra el elemento detalles.

TAXES = {
    'basic': '22',
    'minimum': '10'
}

INVOICE_INDICATOR = {
    'exempt': 1,
    'taxable_minimum': 2,
    'taxable_basic': 3,
    'taxable': 4,
    'free_delivery': 5,
    'no_invoiceable': 6,
    'negative_no_invoiceable': 7,
    'refund_picking': 8,
    'refund': 9,
    'exportation': 10,
    'tax': 11,
    'suspend': 12,
    'non_taxpayer': 13,
    'no_taxable': 15,
}

MESSAGES_TYPES = {
    'request': '310',
    'lot_request': '340',
    'response': '311',
    'lot_response': '341',
    'state_request': '360',
    'state_response': '361',
    'available_notification': '600',
    'notification_data': '610',
    'discard_notification': '620'
}

LOCAL_COUNTRY_CODE = 'UY'

def round_half_away_from_zero(n, digits=0):
    """Devuelve n redondeado a digits dígitos decimales,
       minimizar los errores de representación de punto flotante IEEE-754 y aplicar
       HALF-UP (away from zero).
       Créditos: Función replicada de float_round de odoo/tools/float_utils 
       en repositorio odoo rama 13.0 aplicando solo HALF-UP (away from zero)

    :param n: valor a redondear
    :type n: float
    :param digits: número de dígitos decimales a redondear, defaults to 0
    :type digits: int, optional
    :return: valor redondeado
    :rtype: flaot
    """
    if digits == 0 or n == 0:
        return 0.0
    rounding_factor = 10 ** -digits
    normalized_value = n / rounding_factor
    epsilon_magnitude = math.log(abs(normalized_value), 2)
    epsilon = 2**(epsilon_magnitude-52)
    normalized_value += math.copysign(epsilon, normalized_value)
    rounded_value = round(normalized_value)
    return rounded_value * rounding_factor


class Manager(object):
    __slots__ = ['emisor', 'comprobante', 'connection_data']

    def __init__(self, connection_data, comprobante=None, emisor=None):
        self.emisor = emisor
        self.comprobante = comprobante
        self.connection_data = connection_data

    def get_partner_legal_name(self, partner):
        """
        Obtiene la razón social del partner según la configuración UCFE

        :param partner: objeto partner
        :type partner: res.partner
        :return: Razón social según configuración
        :rtype: str
        """
        if (hasattr(self.connection_data, 'ucfe_config') and 
            self.connection_data.ucfe_config and 
            hasattr(self.connection_data.ucfe_config, 'get_partner_legal_name')):
            return self.connection_data.ucfe_config.get_partner_legal_name(partner)
        # Fallback al comportamiento original
        return str(partner.name)

    def create_req_body(self):
        ReqBody = req_body.ReqBody()
        ReqBody.commerce_code = self.connection_data.commerce_code
        ReqBody.terminal_code = self.connection_data.terminal_code
        ReqBody.timeout = self.connection_data.timeout
        ReqBody.request_date = datetime.now().isoformat('T')
        return ReqBody

    def create_ucfe_req(self, message_type, xml=None):
        UcfeReq = ucfe_requirement.UcfeRequirement()
        UcfeReq.message_type = message_type
        UcfeReq.commerce_code = self.connection_data.commerce_code
        UcfeReq.serial = self.comprobante.cfe_serial
        UcfeReq.cfe_number = self.comprobante.cfe_number
        UcfeReq.cfe_type = self.comprobante.cfe_code
        UcfeReq.terminal_code = self.connection_data.terminal_code
        UcfeReq.adenda = self.comprobante.description
        UcfeReq.email_envio_pdf_receptor = self.comprobante.partner.email
        UcfeReq.request_date = datetime.now().strftime('%Y%m%d')
        UcfeReq.request_time = datetime.now().strftime('%H%M%S')
        UcfeReq.id_req = 1
        UcfeReq.uuid = self._get_uuid_cfe()
        UcfeReq.cfe_xml_or_text = xml
        return UcfeReq

    def create_notification_ucfe_req(self, message_type, notification_type=None, id_req=None):
        UcfeReq = ucfe_requirement.UcfeRequirement()
        UcfeReq.message_type = message_type
        UcfeReq.notification_type = notification_type
        UcfeReq.commerce_code = self.connection_data.commerce_code
        UcfeReq.terminal_code = self.connection_data.terminal_code
        UcfeReq.id_req = id_req
        return UcfeReq

    def __send(self, ReqBody, UcfeReq):
        """
        Envia a webservice los datos que se encuentren en reqBody y ucfeReq,
        utilizando un conector.
        :return: dict. con mensaje de respuesta,  cuerpo de respuesta y request
        """
        conn_obj = conn.Connector()
        conn_obj.send(ReqBody, UcfeReq, self.connection_data)
        return {
            'responseMsg': conn_obj.response_msg,
            'responseBody': conn_obj.response_body,
            'request': conn_obj.request
        }

    def get_cfe_state(self):
        """
        Obtiene el estado del comprobante a partir del codigo de consulta del UcfeReq y un comprobante
        :return: dict. con mensaje de respuesta,  cuerpo de respuesta y request
        """

        ReqBody = self.create_req_body()
        UcfeReq = self.create_ucfe_req(message_type=MESSAGES_TYPES.get('state_request'))

        return self.__send(ReqBody, UcfeReq)

    def get_available_notification(self, notification_type=None):
        """Obtiene la primera notificación disponible de la cola

        :param notification_type: Tipo de notificación que se quiere pedir, 
        por defecto None en caso que se quiera cualquiera
        :type notification_type: string, optional
        :return: Mensaje de respuesta, cuerpo de respuesta y request
        :rtype: dict
        """        

        ReqBody = self.create_req_body()
        UcfeReq = self.create_notification_ucfe_req(MESSAGES_TYPES.get('available_notification'),
                                                    notification_type)

        return self.__send(ReqBody, UcfeReq)

    def get_notification_data(self, id_req):
        """Obtiene la información de una notificación

        :param id_req: Id de la notificación a consultar
        :type id_req: string
        :return: Mensaje de respuesta, cuerpo de respuesta y request
        :rtype: dict
        """ 

        ReqBody = self.create_req_body()
        UcfeReq = self.create_notification_ucfe_req(message_type=MESSAGES_TYPES.get('notification_data'), 
                                                    id_req=id_req)

        return self.__send(ReqBody, UcfeReq)
    
    def discard_notification(self, notification_type, id_req):
        """Descarta una notificación

        :param notification_type: Tipo de la notificación
        :type notification_type: string
        :param id_req: Id de la notificación a descartar
        :type id_req: string
        :return: Mensaje de respuesta, cuerpo de respuesta y request
        :rtype: dict
        """ 

        ReqBody = self.create_req_body()
        UcfeReq = self.create_notification_ucfe_req(message_type=MESSAGES_TYPES.get('discard_notification'), 
                                                    notification_type=notification_type, id_req=id_req)

        return self.__send(ReqBody, UcfeReq)

    def get_document_report(self, image=False):

        conn_obj = conn.Connector()

        return conn_obj.get_document_report(
            self.connection_data,
            self.emisor.vat.number,
            self.comprobante.cfe_code,
            self.comprobante.cfe_serial,
            self.comprobante.cfe_number,
            image=image
        )

    def get_document_report_parameters(self, name_parameters, parameters, image=False):

        conn_obj = conn.Connector()

        return conn_obj.get_document_report_parameters(
            self.connection_data,
            self.emisor.vat.number,
            self.comprobante.cfe_code,
            self.comprobante.cfe_serial,
            self.comprobante.cfe_number,
            name_parameters,
            parameters,
            image=image
        )

    def get_document_received_report(self):

        conn_obj = conn.Connector()

        return conn_obj.get_document_received_report(
            self.connection_data,
            self.comprobante.vat,
            self.comprobante.rut_received,
            self.comprobante.cfe_code,
            self.comprobante.cfe_serial,
            self.comprobante.cfe_number
        )

    def send_document(self):
        """
        Envia los datos del comprobante a webservice para su validacion
        :return: dict. con mensaje de respuesta, cuerpo de respuesta y request
        """

        # Creamos ReqBody
        ReqBody = self.create_req_body()

        # Creamos xml con datos de comprobante y lo asignamos al ucfeReq
        xml = self.fill_xml()
        UcfeReq = self.create_ucfe_req(message_type=MESSAGES_TYPES.get('request'), xml=xml)

        # Enviar
        return self.__send(ReqBody, UcfeReq)

    def fill_xml(self):
        """
        Completa un elemento xml plano con los datos del comprobante.
        :return: objeto xml
        """
        type = self.comprobante.cfe_type
        root = Element(type)
        Encabezado = SubElement(root, "Encabezado")
        self.build_IdDoc(Encabezado)
        self.build_Emisor(Encabezado)
        self.build_Receptor(Encabezado, type)
        self.build_Totales(Encabezado, type)
        self.build_Detalles(root, type)
        if hasattr(self.comprobante, 'invoice_discount_lines'):
            self.build_DescuentosRecargos(root, type)
        self.build_Referencias(root)
        self.build_Compl_Fiscal_Data(root)
        xml_msg = '<CFE version="1.0" xmlns="http://cfe.dgi.gub.uy">{}</CFE>'.format(tostring(root).decode())
        return xml_msg

    def build_IdDoc(self, Encabezado):

        IdDoc = SubElement(Encabezado, "IdDoc")
        SubElement(IdDoc, "TipoCFE").text = str(self.comprobante.cfe_code)

        if self.comprobante.document_type == 'cfc':
            SubElement(IdDoc, "Serie").text = str(self.comprobante.cfe_serial)
            SubElement(IdDoc, "Nro").text = str(self.comprobante.cfe_number)

        SubElement(IdDoc, "FchEmis").text = str(self.comprobante.date)
        if self.comprobante.include_tax: SubElement(IdDoc, "MntBruto").text = '1'
        elif hasattr(self.comprobante, 'imeba') and self.comprobante.imeba: SubElement(IdDoc, "MntBruto").text = '2'
        if self.comprobante.payment_method: SubElement(IdDoc, "FmaPago").text = str(self.comprobante.payment_method)
        if hasattr(self.comprobante, 'own_collection'): SubElement(IdDoc,"IndCobPropia").text = '1'
        if self.comprobante.date_due: SubElement(IdDoc, "FchVenc").text = str(self.comprobante.date_due)

        if self.comprobante.incoterm_code: SubElement(IdDoc, "ClauVenta").text = str(self.comprobante.incoterm_code)
        if self.comprobante.transport_type: SubElement(IdDoc, "TipoTraslado").text = str(self.comprobante.transport_type)
        if self.comprobante.sale_mode_code: SubElement(IdDoc, "ModVenta").text = str(self.comprobante.sale_mode_code if self.comprobante.sale_mode_code else 'N/A')
        if self.comprobante.transport_route_code: SubElement(IdDoc, "ViaTransp").text = str(self.comprobante.transport_route_code)
        if hasattr(self.comprobante, 'sending_legends_header'): SubElement(IdDoc, "InfoAdicionalDoc").text = str(self.comprobante.obligatory_legend_header)

        if hasattr(self.comprobante, 'owner'): SubElement(IdDoc, "IndPropiedad").text = str(self.comprobante.owner)
        if hasattr(self.comprobante, 'owner_vat_code'): SubElement(IdDoc, "TipoDocProp").text = str(self.comprobante.owner_vat_code)
        if hasattr(self.comprobante, 'owner_country_code'): SubElement(IdDoc, "CodPaisProp").text = str(self.comprobante.owner_country_code)
        if hasattr(self.comprobante, 'owner_vat'): SubElement(IdDoc, "DocProp").text = str(self.comprobante.owner_vat)
        if hasattr(self.comprobante, 'owner_partner_name'): SubElement(IdDoc, "RznSocProp").text = str(self.comprobante.owner_partner_name)

        return IdDoc

    def build_Emisor(self, Encabezado):
        """
        Construye el elemento emisor del objeto xml, que contiene datos del emisor del comprobante.
        :param Encabezado: elemento encabezado xml
        :param emisor: objeto emisor
        """
        # ELEMENTOS DEL EMISOR (COMPANIA)
        Emisor = SubElement(Encabezado, "Emisor")
        SubElement(Emisor, "RUCEmisor").text = str(self.emisor.vat.number or '')
        SubElement(Emisor, "RznSoc").text = str(self.emisor.name)
        if hasattr(self.emisor, 'phone'): SubElement(Emisor, "Telefono").text = str(self.emisor.phone)
        if hasattr(self.emisor, 'email'): SubElement(Emisor, "CorreoEmisor").text = str(self.emisor.email)
        SubElement(Emisor, "CdgDGISucur").text = str(self.connection_data.sucursal_code or '')
        SubElement(Emisor, "DomFiscal").text = str(self.emisor.street or '')
        SubElement(Emisor, "Ciudad").text = str(self.emisor.city or '')
        SubElement(Emisor, "Departamento").text = str(self.emisor.state or '')

    def build_Receptor(self, Encabezado, type):

        Receptor = SubElement(Encabezado, "Receptor")

        RECEPTOR_BUILDER = {
            'eFact_Exp': self.build_exportation_receptor,
            'eFact': self.build_local_receptor,
            'eTck': self.build_local_receptor,
            'eBoleta': self.build_local_receptor,
            'eResg': self.build_local_receptor,
            'eRem': self.build_local_receptor_rem,
            'eRem_Exp': self.build_exportation_receptor,
        }
        if type == 'eTck':
            RECEPTOR_BUILDER.get(type)(Receptor,Encabezado)
        else:
            RECEPTOR_BUILDER.get(type)(Receptor)

    def get_doc_recep_type(self, country_code):
        return "DocRecep" if country_code == LOCAL_COUNTRY_CODE else "DocRecepExt"

    def build_exportation_receptor(self, Receptor):

        SubElement(Receptor, "TipoDocRecep").text = str(self.comprobante.partner.vat.code or '')
        SubElement(Receptor, "CodPaisRecep").text = str(self.comprobante.partner.country_code or '')
        SubElement(Receptor, self.get_doc_recep_type(self.comprobante.partner.country_code)).text = str(self.comprobante.partner.vat.number or '')
        SubElement(Receptor, "RznSocRecep").text = self.get_partner_legal_name(self.comprobante.partner)
        SubElement(Receptor, "DirRecep").text = str(self.comprobante.partner.street or '')
        SubElement(Receptor, "CiudadRecep").text = str(self.comprobante.partner.city or '')
        SubElement(Receptor, "DeptoRecep").text = str(self.comprobante.partner.state or '')
        SubElement(Receptor, "PaisRecep").text = str(self.comprobante.partner.country or '')
        if hasattr(self.comprobante, 'sending_legends_partner'):
            SubElement(Receptor, "InfoAdicional").text = str(self.comprobante.obligatory_legend_partner)
        if hasattr(self.comprobante, 'identificator'):
            SubElement(Receptor, "CompraID").text = str(self.comprobante.identificator or '')
        if self.comprobante.partner.zip: SubElement(Receptor, "CP").text = str(self.comprobante.partner.zip or '')

    def build_local_receptor(self, Receptor, Encabezado=None):
        """
        Completa los datos del receptor de un eTicket, eFactura, eBoleta, eResguardo.
        Incluye los datos de dirección aunque el partner receptor no tenga vat.
        :param Receptor: elemento Receptor del xml
        :param Encabezado: elemento Encabezado del xml
        """
        
        # Añadimos información de VAT solo si existe
        if self.comprobante.partner.vat:
            SubElement(Receptor, "TipoDocRecep").text = str(self.comprobante.partner.vat.code or '')
            SubElement(Receptor, "CodPaisRecep").text = str(self.comprobante.partner.country_code or '')
            SubElement(Receptor, self.get_doc_recep_type(self.comprobante.partner.country_code)).text = str(self.comprobante.partner.vat.number or '')
        
        # Siempre añadimos la razón social (nombre)
        SubElement(Receptor, "RznSocRecep").text = self.get_partner_legal_name(self.comprobante.partner)

        # Siempre añadimos la dirección y demás información
        SubElement(Receptor, "DirRecep").text = str(self.comprobante.partner.street or '')
        SubElement(Receptor, "CiudadRecep").text = str(self.comprobante.partner.city or '')
        SubElement(Receptor, "DeptoRecep").text = str(self.comprobante.partner.state or '')
        if hasattr(self.comprobante, 'sending_legends_partner'):
            SubElement(Receptor, "InfoAdicional").text = str(self.comprobante.obligatory_legend_partner)
        if hasattr(self.comprobante, 'lugar_dest_ent'):
            SubElement(Receptor, "LugarDestEnt").text = str(self.comprobante.lugar_dest_ent or '')
        if hasattr(self.comprobante, 'identificator'):
            SubElement(Receptor, "CompraID").text = str(self.comprobante.identificator or '')

    def build_local_receptor_rem(self, Receptor):

        SubElement(Receptor, "TipoDocRecep").text = str(self.comprobante.partner.vat.code or '')
        SubElement(Receptor, "CodPaisRecep").text = str(self.comprobante.partner.country_code or '')
        SubElement(Receptor, self.get_doc_recep_type(self.comprobante.partner.country_code)).text = str(self.comprobante.partner.vat.number or '')
        SubElement(Receptor, "RznSocRecep").text = self.get_partner_legal_name(self.comprobante.partner)
        SubElement(Receptor, "DirRecep").text = str(self.comprobante.partner.street or '')
        SubElement(Receptor, "CiudadRecep").text = str(self.comprobante.partner.city or '')
        SubElement(Receptor, "DeptoRecep").text = str(self.comprobante.partner.state or '')
        SubElement(Receptor, "PaisRecep").text = str(self.comprobante.partner.country or '')
        if hasattr(self.comprobante, 'identificator'):
            SubElement(Receptor, "CompraID").text = str(self.comprobante.identificator or '')
        if self.comprobante.partner.zip: SubElement(Receptor, "CP").text = str(self.comprobante.partner.zip or '')

    def build_Totales(self, Encabezado, type):
        """
        Completa los totales para el comprobante, segun el tipo
        :param Encabezado: elemento Encabezado del xml
        :param type: string tipo
        """
        Totales = SubElement(Encabezado, "Totales")

        TOTALES_BUILDER = {
            'eFact_Exp': self.totales_eFact_Exp,
            'eFact': self.totales_eFact,
            'eTck': self.totales_eFact,
            'eBoleta': self.totales_eFact,
            'eResg': self.totales_eResg,
            'eRem': self.totales_eRem,
            'eRem_Exp': self.totales_eRem_Exp,
        }

        TOTALES_BUILDER.get(type)(Totales)

    def totales_eRem_Exp(self, Totales):
        SubElement(Totales, "TpoMoneda").text = str(self.comprobante.currency) or ''
        if self.comprobante.currency_rate:  SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        SubElement(Totales, "MntExpoyAsim").text = self._format_amount(self.get_mnt_exportation())
        SubElement(Totales, "MntTotal").text = self._format_amount(self.get_total_amount())
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))

    def totales_eFact_Exp(self, Totales):
        SubElement(Totales, "TpoMoneda").text = str(self.comprobante.currency) or ''
        if self.comprobante.currency_rate:  SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        SubElement(Totales, "MntExpoyAsim").text = self._format_amount(self.get_mnt_exportation())
        SubElement(Totales, "MntTotal").text = self._format_amount(self.get_total_amount())
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))
        if self.get_mnt_non_invoiceable() or self.get_mnt_negative_non_invoiceable(): SubElement(Totales, "MontoNF").text = self._format_amount(self.get_mnt_non_invoiceable() + self.get_mnt_negative_non_invoiceable())
        SubElement(Totales, "MntPagar").text = self._format_amount(self.get_total_to_pay())

    def totales_eFact(self, Totales):
        SubElement(Totales, "TpoMoneda").text = str(self.comprobante.currency) or ''
        if self.comprobante.currency_rate: SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        if self.get_mnt_non_taxable() or self.get_mnt_exempt() or self.get_mnt_non_taxpayer(): SubElement(Totales, "MntNoGrv").text = self._format_amount(self.get_mnt_non_taxable() + self.get_mnt_exempt() + self.get_mnt_non_taxpayer())
        if self.get_mnt_exportation(): SubElement(Totales, "MntExpoyAsim").text = self._format_amount(self.get_mnt_exportation())
        if self.get_mnt_base_iva_tasa_min(): SubElement(Totales, "MntNetoIvaTasaMin").text = self._format_amount(self.get_mnt_base_iva_tasa_min())
        if self.get_mnt_base_iva_tasa_basic(): SubElement(Totales, "MntNetoIVATasaBasica").text = self._format_amount(self.get_mnt_base_iva_tasa_basic())
        if self.get_mnt_base_iva_tasa_min(): SubElement(Totales, "IVATasaMin").text = TAXES.get('minimum')
        if self.get_mnt_base_iva_tasa_basic(): SubElement(Totales, "IVATasaBasica").text = TAXES.get('basic')
        if self.get_mnt_iva_tasa_min(): SubElement(Totales, "MntIVATasaMin").text = self._format_amount(self.get_mnt_iva_tasa_min())
        if self.get_mnt_iva_tasa_basic(): SubElement(Totales, "MntIVATasaBasica").text = self._format_amount(self.get_mnt_iva_tasa_basic())
        SubElement(Totales, "MntTotal").text = self._format_amount(self.get_total_amount())
        if self.has_perceptions(): SubElement(Totales, "MntTotRetenido").text = self._format_amount(self.get_mnt_perception())
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.invoice_lines))
        if self.has_perceptions():
            for p_code, p_amount in self.get_perceptions().items():
                RetencPercep = SubElement(Totales, "RetencPercep")
                SubElement(RetencPercep, "CodRet").text = str(p_code)
                SubElement(RetencPercep, "ValRetPerc").text = self._format_amount(p_amount)
        if self.get_mnt_non_invoiceable() or self.get_mnt_negative_non_invoiceable(): SubElement(Totales, "MontoNF").text = self._format_amount(self.get_mnt_non_invoiceable() + self.get_mnt_negative_non_invoiceable())
        SubElement(Totales, "MntPagar").text = self._format_amount(self.get_total_to_pay())

    def totales_eResg(self, Totales):

        factor = -1 if hasattr(self.comprobante, 'refund_info') else 1

        SubElement(Totales, "TpoMoneda").text = self.comprobante.currency or ''
        if self.comprobante.currency_rate: SubElement(Totales, "TpoCambio").text = self._format_tipo_cambio(self.comprobante.currency_rate)
        SubElement(Totales, "MntTotRetenido").text = self._format_amount(self.get_total_retention() * factor)
        detail_count = 0
        for retention in self.comprobante.retentions:
            detail_count += len(retention.retention_detail)
        SubElement(Totales, "CantLinDet").text = str(detail_count)
        retentions = {}
        ret_nro = 0
        for ret in self.comprobante.retentions:
            ret_nro += 1
            retentions[ret_nro] = SubElement(Totales, "RetencPercep")
            SubElement(retentions[ret_nro], "CodRet").text = str(ret.retention_code)
            SubElement(retentions[ret_nro], "ValRetPerc").text = self._format_amount(ret.get_amount() * factor)

    def totales_eRem(self, Totales):
        SubElement(Totales, "CantLinDet").text = str(len(self.comprobante.picking_lines))

    def build_Compl_Fiscal_Data(self, root):
        if hasattr(self.comprobante, 'fiscal_data'):
            Compl_Fiscal = SubElement(root, "Compl_Fiscal")
            Compl_Fiscal_Data = SubElement(Compl_Fiscal, "Compl_Fiscal_Data")
            SubElement(Compl_Fiscal_Data, "RUCEmisor").text = str(self.emisor.vat.number or '')
            SubElement(Compl_Fiscal_Data, "TipoDocMdte").text = str(self.comprobante.fiscal_data.vat.code or '')
            SubElement(Compl_Fiscal_Data, "Pais").text = str(self.comprobante.fiscal_data.country_code or '')
            SubElement(Compl_Fiscal_Data, "DocMdte").text = str(self.comprobante.fiscal_data.vat.number or '')
            SubElement(Compl_Fiscal_Data, "NombreMdte").text = str(self.comprobante.fiscal_data.name or '')

    def build_Referencias(self, root):

        refund_info = self.comprobante.refund_info if hasattr(self.comprobante, 'refund_info') else None
        references = self.comprobante.references if hasattr(self.comprobante, 'references') else None
        reference_details = refund_info or references

        if reference_details:

            if reference_details.refund_invoices:

                # ELEMENTOS DE REFERENCIA NOTA DE CREDITO / DEBITO
                Referencia = SubElement(root, "Referencia")
                NroLinRef = 0

                for refund in reference_details.refund_invoices:
                    ReferenciaChild = SubElement(Referencia, "Referencia")

                    NroLinRef += 1

                    SubElement(ReferenciaChild, "NroLinRef").text = str(NroLinRef)
                    SubElement(ReferenciaChild, "TpoDocRef").text = refund.cfe_code
                    SubElement(ReferenciaChild, "Serie").text = refund.cfe_serial
                    SubElement(ReferenciaChild, "NroCFERef").text = refund.cfe_number
                    SubElement(ReferenciaChild, "RazonRef").text = reference_details.refund_reason or 'N/A'
                    SubElement(ReferenciaChild, "FechaCFEref").text = str(refund.date)

            else:

                Referencia = SubElement(root, "Referencia")
                ReferenciaChild = SubElement(Referencia, "Referencia")

                SubElement(ReferenciaChild, "NroLinRef").text = '1'
                SubElement(ReferenciaChild, "IndGlobal").text = '1'
                SubElement(ReferenciaChild, "RazonRef").text = reference_details.refund_reason or 'N/A'

    def build_Detalles(self, root, type):

        Detalle = SubElement(root, "Detalle")

        DETALLES_BUILDER = {
            'eFact_Exp': self.detalle_eFact,
            'eFact': self.detalle_eFact,
            'eTck': self.detalle_eFact,
            'eBoleta': self.detalle_eFact,
            'eResg': self.detalle_eResg,
            'eRem': self.detalle_eRem,
            'eRem_Exp': self.detalle_eFact,
        }

        DETALLES_BUILDER.get(type)(Detalle)

    def build_DescuentosRecargos(self, root, type):

        DescuentoRecargo = SubElement(root, "DscRcgGlobal")
        DESCUENTOS_BUILDER = {
            'eFact_Exp': self.descuento_eFact,
            'eFact': self.descuento_eFact,
            'eTck': self.descuento_eFact,
        }

        DESCUENTOS_BUILDER.get(type)(DescuentoRecargo)

    def descuento_eFact(self, DescuentoRecargo):
        item_nro = 0
        Item = {}
        for line in self.comprobante.invoice_discount_lines:
            item_nro += 1
            Item[item_nro] = SubElement(DescuentoRecargo, "DRG_Item")
            SubElement(Item[item_nro], "NroLinDR").text = str(item_nro)
            # Los descuentos se envia D en los recargos se envia R
            SubElement(Item[item_nro], "TpoMovDR").text = 'D'
            # Si el monto es un monto en pesos se envia 1 un porcentaje se envia 2
            SubElement(Item[item_nro], "TpoDR").text = '1'
            # Descripcion
            SubElement(Item[item_nro], "GlosaDR").text = str(line.description)
            # Valor de descuento
            SubElement(Item[item_nro], "ValorDR").text = self._format_amount(line.amount)
            # Indicador de facturación
            SubElement(Item[item_nro], "IndFactDR").text = str(line.invoice_indicator)

    def detalle_eRem(self, Detalle):
        item_nro = 0
        Item = {}
        for line in self.comprobante.picking_lines:
            item_nro += 1
            Item[item_nro] = SubElement(Detalle, "Item")
            SubElement(Item[item_nro], "NroLinDet").text = str(item_nro)
            if hasattr(self.comprobante, 'refund_info'):
                SubElement(Item[item_nro], "IndFact").text = str(INVOICE_INDICATOR.get('refund_picking'))
            SubElement(Item[item_nro], "NomItem").text = str(line.description)
            if hasattr(line, 'description_extra') and hasattr(line, 'sending_legends_line'):
                SubElement(Item[item_nro], "DscItem").text = str(line.description_extra) + '\n' + str(line.obligatory_legend_line)
            elif hasattr(line, 'description_extra'):
                SubElement(Item[item_nro], "DscItem").text = str(line.description_extra)
            elif hasattr(line, 'sending_legends_line'):
                SubElement(Item[item_nro], "DscItem").text = str(line.obligatory_legend_line)
            SubElement(Item[item_nro], "Cantidad").text = str(line.quantity)
            SubElement(Item[item_nro], "UniMed").text = str(line.uom_code) if line.uom_code else 'N/A'

    def detalle_eFact(self, Detalle):
        item_nro = 0
        Item = {}
        for line in self.comprobante.invoice_lines:
            item_nro += 1
            Item[item_nro] = SubElement(Detalle, "Item")
            SubElement(Item[item_nro], "NroLinDet").text = str(item_nro)
            if hasattr(line, 'cod_items') and line.cod_items:
                for c in line.cod_items:
                    cod_item_elem = SubElement(Item[item_nro], "CodItem")
                    SubElement(cod_item_elem, "TpoCod").text = str(c.tpo_cod)
                    SubElement(cod_item_elem, "Cod").text = str(c.cod)
            if line.invoice_indicator:
                SubElement(Item[item_nro], "IndFact").text = str(line.invoice_indicator)
            SubElement(Item[item_nro], "NomItem").text = str(line.description)
            if hasattr(line, 'description_extra') and hasattr(line, 'sending_legends_line'):
                SubElement(Item[item_nro], "DscItem").text = str(line.description_extra) + '\n' + str(line.obligatory_legend_line)
            elif hasattr(line, 'description_extra'):
                SubElement(Item[item_nro], "DscItem").text = str(line.description_extra)
            elif hasattr(line, 'sending_legends_line'):
                SubElement(Item[item_nro], "DscItem").text = str(line.obligatory_legend_line)
            SubElement(Item[item_nro], "Cantidad").text = str(line.quantity)
            SubElement(Item[item_nro], "UniMed").text = str(line.uom_code) if line.uom_code else 'N/A'
            SubElement(Item[item_nro], "PrecioUnitario").text = self._format_amount(line.unit_price, self.comprobante.decimal_places if hasattr(self.comprobante, "decimal_places") else 2)
            if hasattr(line, 'discount') and hasattr(line, 'discount_amount'):
                SubElement(Item[item_nro], "DescuentoPct").text = self._format_amount(line.discount)
                SubElement(Item[item_nro], "DescuentoMonto").text = self._format_amount(line.discount_amount)
            if hasattr(line, 'perceptions') and line.perceptions:
                for percep in line.perceptions:
                    RetencPercep = SubElement(Item[item_nro], "RetencPercep")
                    SubElement(RetencPercep, "CodRet").text = str(percep.code)
                    if hasattr(percep, 'percentage'):
                        SubElement(RetencPercep, "Tasa").text = self._format_amount(percep.percentage)
                    SubElement(RetencPercep, "MntSujetoaRet").text = self._format_amount(percep.taxable_base)
                    SubElement(RetencPercep, "ValRetPerc").text =self._format_amount(math.fabs(percep.amount))
            SubElement(Item[item_nro], "MontoItem").text = self._format_amount(abs(line.amount))

    def detalle_eResg(self, Detalle):
        item_nro = 0
        Item = {}
        for retention in self.comprobante.retentions:
            for detail in retention.retention_detail:
                item_nro += 1
                Item[item_nro] = SubElement(Detalle, "Item")
                SubElement(Item[item_nro], "NroLinDet").text = str(item_nro)
                if hasattr(self.comprobante, 'refund_info'):
                    SubElement(Item[item_nro], "IndFact").text = str(INVOICE_INDICATOR.get('refund'))
                RetencPercep = SubElement(Item[item_nro], "RetencPercep")
                SubElement(RetencPercep, "CodRet").text = str(retention.retention_code)
                if hasattr(retention, 'percentage_retention'):
                    SubElement(RetencPercep, "Tasa").text = self._format_amount(retention.percentage_retention)

                # Se decidio no enviar la tasa dado que puede haber diferencias y el % es legal
                # en el caso de identificar que comience a ser necesario simplemente se debera
                # descomentar la siguiente linea.
                # SubElement(RetencPercep, "Tasa").text = str(detail.get_tax())

                SubElement(RetencPercep, "MntSujetoaRet").text = self._format_amount(detail.taxable_base)
                SubElement(RetencPercep, "ValRetPerc").text =self._format_amount(math.fabs(detail.amount))

    @staticmethod
    def _format_tipo_cambio(rate):
        return '{:.3f}'.format(round_half_away_from_zero(rate, 3))

    @staticmethod
    def _format_amount(amount, decimal=2):
        value = '{:.' + str(decimal) + 'f}'
        return value.format(round_half_away_from_zero(amount, 5))

    def _get_uuid_cfe(self):
        uuid = self.comprobante.uuid if hasattr(self.comprobante, 'uuid') else False
        if not uuid:
            longitud = 12
            valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
            uuid = ""
            uuid = uuid.join([choice(valores) for i in range(longitud)])
        return uuid

    def get_mnt(self, indicator):
        total = sum([line.amount for line in self.comprobante.invoice_lines if
                     str(line.invoice_indicator) == str(indicator)])
        total_discount = sum([line_discount.amount for line_discount in self.comprobante.invoice_discount_lines if
                     str(line_discount.invoice_indicator) == str(indicator)]) if hasattr(self.comprobante, 'invoice_discount_lines') else 0
        return total - total_discount if total else 0

    def get_tax(self, indicator):
        total = sum([line.tax for line in self.comprobante.invoice_lines if
                     str(line.invoice_indicator) == str(indicator)])
        tax_discount = sum([line_discount.tax for line_discount in self.comprobante.invoice_discount_lines if
                            str(line_discount.invoice_indicator) == str(indicator)]) if hasattr(self.comprobante, 'invoice_discount_lines') else 0
        return total - tax_discount if total else 0

    def get_mnt_base(self, indicator):
        total = sum([line.amount - line.tax if line.include_tax else line.amount for line in self.comprobante.invoice_lines if str(line.invoice_indicator) == str(indicator)])
        total_discount = sum([line_discount.amount - line_discount.tax if line_discount.include_tax else line_discount.amount for line_discount in self.comprobante.invoice_discount_lines if
                              str(line_discount.invoice_indicator) == str(indicator)]) if\
            hasattr(self.comprobante,'invoice_discount_lines') else 0
        return total - total_discount if total else 0

    def get_mnt_non_invoiceable(self):
        return self.get_mnt(INVOICE_INDICATOR.get('no_invoiceable'))

    def get_mnt_negative_non_invoiceable(self):
        return self.get_mnt(INVOICE_INDICATOR.get('negative_no_invoiceable'))

    def get_mnt_non_taxable(self):
        return self.get_mnt(INVOICE_INDICATOR.get('no_taxable'))

    def get_mnt_exempt(self):
        return self.get_mnt(INVOICE_INDICATOR.get('exempt'))

    def get_mnt_exportation(self):
        return self.get_mnt(INVOICE_INDICATOR.get('exportation'))

    def get_mnt_base_iva_tasa_min(self):
        return self.get_mnt_base(INVOICE_INDICATOR.get('taxable_minimum'))

    def get_mnt_iva_tasa_min(self):
        return self.get_tax(INVOICE_INDICATOR.get('taxable_minimum'))

    def get_mnt_base_iva_tasa_basic(self):
        return self.get_mnt_base(INVOICE_INDICATOR.get('taxable_basic'))

    def get_mnt_iva_tasa_basic(self):
        return self.get_tax(INVOICE_INDICATOR.get('taxable_basic'))

    def get_mnt_non_taxpayer(self):
        return self.get_mnt(INVOICE_INDICATOR.get('non_taxpayer'))

    def get_total_amount(self):
        total_basic = round_half_away_from_zero(self.get_mnt_iva_tasa_basic(), 2) + round_half_away_from_zero(self.get_mnt_base_iva_tasa_basic(), 2)
        total_min = round_half_away_from_zero(self.get_mnt_iva_tasa_min(), 2) + round_half_away_from_zero(self.get_mnt_base_iva_tasa_min(), 2)
        total_no_taxable = round_half_away_from_zero(self.get_mnt_non_taxable(), 2)
        total_exempt = round_half_away_from_zero(self.get_mnt_exempt(), 2)
        total_exportation = round_half_away_from_zero(self.get_mnt_exportation(), 2)
        total_non_taxpayer = round_half_away_from_zero(self.get_mnt_non_taxpayer(), 2)
        return total_basic + total_min + total_no_taxable + total_exempt + total_exportation + total_non_taxpayer

    def get_total_to_pay(self):
        total_perception = round_half_away_from_zero(self.get_mnt_perception(), 2)
        total_non_invoiceable = round_half_away_from_zero(self.get_mnt_non_invoiceable(), 2)
        total_negative_non_invoiceable = round_half_away_from_zero(self.get_mnt_negative_non_invoiceable(), 2)
        total_perception = round_half_away_from_zero(self.get_mnt_perception(), 2)
        return self.get_total_amount() + total_non_invoiceable + total_negative_non_invoiceable + total_perception

    def get_total_retention(self):
        return sum([ret.get_amount() for ret in self.comprobante.retentions])
    
    def has_perceptions(self):
        return any(hasattr(line, 'perceptions') and line.perceptions for line in self.comprobante.invoice_lines)
    
    def get_perceptions(self):
        perceptions = defaultdict(float)
        if self.has_perceptions():
            for line in self.comprobante.invoice_lines:
                for percep in line.perceptions:
                    perceptions[percep.code] += percep.amount
        # Recorro el diccionario y redondeo el monto de las percepciones para evitar diferencias
        rounded_perceptions = {key: round(value, 2) for key, value in perceptions.items()}
        return rounded_perceptions
    
    def get_mnt_perception(self):
        return sum(amount for amount in self.get_perceptions().values())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
