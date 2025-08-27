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
    __slots__ = ['_message_type', '_commerce_code', '_serial', '_cfe_number', '_cfe_type', '_terminal_code']

    def __init__(self):
        self._message_type = None
        self._commerce_code = None
        self._serial = None
        self._cfe_number = None
        self._cfe_type = None
        self._terminal_code = None

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
