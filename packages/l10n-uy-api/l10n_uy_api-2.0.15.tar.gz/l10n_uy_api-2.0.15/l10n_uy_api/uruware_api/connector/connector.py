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

from zeep import Client
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken


class Connector(object):

    __slots__ = ['_response_body', '_response_msg', '_request']

    def __init__(self):
        self._response_body = None
        self._response_msg = None
        self._request = None

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, request):
        self._request = request

    @property
    def response_body(self):
        return self._response_body

    @response_body.setter
    def response_body(self, response_body):
        self._response_body = response_body

    @property
    def response_msg(self):
        return self._response_msg

    @response_msg.setter
    def response_msg(self, response_msg):
        self._response_msg = response_msg

    def get_client(self, connection_data):
        return Client(
            connection_data.url,
            wsse=UsernameToken(
                connection_data.user,
                connection_data.password
            )
        )

    def get_document_report(self, connection_data, rut, cfe_code, cfe_serial, cfe_number, image=False):
        client = self.get_client(connection_data)
        if image:
            return client.service.GenerarImagen(rut, cfe_code, cfe_serial, cfe_number, 'png')[0]
        else:
            return client.service.ObtenerPdf(rut, cfe_code, cfe_serial, cfe_number)

    def get_document_report_parameters(self, connection_data, rut, cfe_code, cfe_serial, cfe_number, name_parameters, parameters, image=False):
        client = self.get_client(connection_data)
        if image:
            return client.service.GenerarImagenConParametros(rut, cfe_code, cfe_serial, cfe_number, 'png', nombreParametros=name_parameters, valoresParametros=parameters)[0]
        else:
            return client.service.ObtenerPdfConParametros(rut, cfe_code, cfe_serial, cfe_number, nombreParametros=name_parameters, valoresParametros=parameters)

    def get_document_received_report(self, connection_data, rut, rut_received, cfe_code, cfe_serial, cfe_number):
        client = self.get_client(connection_data)
        return client.service.ObtenerPdfCfeRecibido(rut, rut_received, cfe_code, cfe_serial, cfe_number)
    
    def send(self, req_body, ucfe_requirement, connection_data):
        """
        Genera los tokens correspondientes, los envia y devuelve el mensaje de la respuesta
        :param req_body: un objeto de tipo ReqBody que contendra los datos del cuerpo
        :param ucfe_requirement: un objeto de tipo UcfeRequirement que contendra los datos del requerimiento
        :return:
        """

        client = self.get_client(connection_data)

        client_ucfe_requirement = client.type_factory('ns0').RequerimientoParaUcfe()
        client_ucfe_requirement.TipoMensaje = ucfe_requirement.message_type
        client_ucfe_requirement.TipoNotificacion = ucfe_requirement.notification_type
        client_ucfe_requirement.CodComercio = ucfe_requirement.commerce_code
        client_ucfe_requirement.Serie = ucfe_requirement.serial
        client_ucfe_requirement.NumeroCfe = ucfe_requirement.cfe_number
        client_ucfe_requirement.TipoCfe = ucfe_requirement.cfe_type
        client_ucfe_requirement.CodTerminal = ucfe_requirement.terminal_code
        client_ucfe_requirement.Adenda = ucfe_requirement.adenda
        client_ucfe_requirement.EmailEnvioPdfReceptor = ucfe_requirement.email_envio_pdf_receptor
        client_ucfe_requirement.FechaReq = ucfe_requirement.request_date
        client_ucfe_requirement.HoraReq = ucfe_requirement.request_time
        client_ucfe_requirement.IdReq = ucfe_requirement.id_req
        client_ucfe_requirement.Uuid = ucfe_requirement.uuid
        client_ucfe_requirement.RutEmisor = ucfe_requirement.rut_emisor
        client_ucfe_requirement.CfeXmlOTexto = ucfe_requirement.cfe_xml_or_text

        client_req_body = client.type_factory('ns0').ReqBody()
        client_req_body.CodComercio = req_body.commerce_code
        client_req_body.CodTerminal = req_body.terminal_code
        client_req_body.Tout = req_body.timeout
        client_req_body.RequestDate = req_body.request_date
        client_req_body.Req = client_ucfe_requirement

        try:
            self.response_body = client.service.Invoke(client_req_body)
            self.response_msg = self.response_body.Resp.MensajeRta
            self.request = client_req_body
        except Fault as e:
            self.response_body = None
            self.response_msg = e.message
            self.request = client_req_body

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
