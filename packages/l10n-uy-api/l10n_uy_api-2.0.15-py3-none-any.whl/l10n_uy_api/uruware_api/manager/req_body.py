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


class ReqBody(object):
    __slots__ = ['_commerce_code', '_terminal_code', '_timeout', '_request_date']

    def __init__(self):
        self._commerce_code = None
        self._terminal_code = None
        self._timeout = None
        self._request_date = None

    @property
    def commerce_code(self):
        return self._commerce_code

    @commerce_code.setter
    def commerce_code(self, commerce_code):
        self._commerce_code = commerce_code

    @property
    def terminal_code(self):
        return self._terminal_code

    @terminal_code.setter
    def terminal_code(self, terminal_code):
        self._terminal_code = terminal_code

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def request_date(self):
        return self._request_date

    @request_date.setter
    def request_date(self, request_date):
        self._request_date = request_date


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
