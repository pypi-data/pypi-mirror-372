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


class UcfeRequirement(object):
    __slots__ = ['_message_type', '_commerce_code', '_serial', '_cfe_number', '_cfe_type', '_terminal_code',
                 '_adenda', '_rut_emisor', '_email_envio_pdf_receptor', '_request_date', '_request_time', '_id_req', '_uuid',
                 '_cfe_xml_or_text', '_notification_type']

    def __init__(self):
        self._message_type = None        
        self._notification_type = None
        self._commerce_code = None
        self._serial = None
        self._cfe_number = None
        self._cfe_type = None
        self._terminal_code = None
        self._adenda = None
        self._rut_emisor = None
        self._email_envio_pdf_receptor = None
        self._request_date = None
        self._request_time = None
        self._id_req = None
        self._uuid = None
        self._cfe_xml_or_text = None

    @property
    def cfe_xml_or_text(self):
        return self._cfe_xml_or_text

    @cfe_xml_or_text.setter
    def cfe_xml_or_text(self, cfe_xml_or_text):
        self._cfe_xml_or_text = cfe_xml_or_text

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    @property
    def id_req(self):
        return self._id_req

    @id_req.setter
    def id_req(self, id_req):
        self._id_req = id_req

    @property
    def request_time(self):
        return self._request_time

    @request_time.setter
    def request_time(self, request_time):
        self._request_time = request_time

    @property
    def request_date(self):
        return self._request_date

    @request_date.setter
    def request_date(self, request_date):
        self._request_date = request_date

    @property
    def adenda(self):
        return self._adenda

    @adenda.setter
    def adenda(self, adenda):
        self._adenda = adenda

    @property
    def email_envio_pdf_receptor(self):
        return self._email_envio_pdf_receptor

    @email_envio_pdf_receptor.setter
    def email_envio_pdf_receptor(self, email_envio_pdf_receptor):
        self._email_envio_pdf_receptor = email_envio_pdf_receptor

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type
    
    @property
    def notification_type(self):
        return self._notification_type

    @notification_type.setter
    def notification_type(self, notification_type):
        self._notification_type = notification_type

    @property
    def commerce_code(self):
        return self._commerce_code

    @commerce_code.setter
    def commerce_code(self, commerce_code):
        self._commerce_code = commerce_code

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

    @property
    def cfe_number(self):
        return self._cfe_number

    @cfe_number.setter
    def cfe_number(self, cfe_number):
        self._cfe_number = cfe_number

    @property
    def cfe_type(self):
        return self._cfe_type

    @cfe_type.setter
    def cfe_type(self, cfe_type):
        self._cfe_type = cfe_type

    @property
    def terminal_code(self):
        return self._terminal_code

    @terminal_code.setter
    def terminal_code(self, terminal_code):
        self._terminal_code = terminal_code

    @property
    def rut_emisor(self):
        return self._rut_emisor

    @rut_emisor.setter
    def rut_emisor(self, rut_emisor):
        self._rut_emisor = rut_emisor

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
