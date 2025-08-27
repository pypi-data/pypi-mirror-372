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

from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.sax.saxutils import escape as _xml_escape

from .manager import Manager, MESSAGES_TYPES
from . import ucfe_requirement

MESSAGES_TYPES.update({
    'batch_send':   '700',
    'batch_sign':   '710',
    'batch_query':  '720',
    'batch_send_r': '701',
    'batch_sign_r': '711',
    'batch_query_r':'721',
})

class BatchManager(Manager):

    def __init__(self, connection_data, comprobantes, emisor):
        super().__init__(connection_data, None, emisor)
        self.comprobantes = comprobantes

    def _header_line(self, cfe, id_req):
        """
        Construye la línea de encabezado del CFE.        
        """
        return "|".join([
            MESSAGES_TYPES['lot_request'],           # Posición 1
            cfe.uuid or self._get_uuid_cfe(),        # Posición 2
            str(cfe.cfe_code).zfill(3),             # Posición 3
            cfe.cfe_serial or '',                    # Posición 4
            str(cfe.cfe_number).zfill(7) if cfe.cfe_number else '',  # Posición 5
            str(id_req).zfill(10),                   # Posición 6
            datetime.now().strftime('%H%M%S'),       # Posición 7
            datetime.now().strftime('%Y%m%d'),       # Posición 8
            self.connection_data.terminal_code,      # Posición 9
            self.connection_data.commerce_code,      # Posición 10
            '',                                      # Posición 11
            '',                                      # Posición 12
            '',                                      # Posición 13
            '',                                      # Posición 14
            '',                                      # Posición 15
            '',                                      # Posición 16
            '',                                      # Posición 17
            '',                                      # Posición 18
            '',                                      # Posición 19
            '',                                      # Posición 20
            '',                                      # Posición 21
            cfe.partner.email or '',                 # Posición 22 - EmailEnvioPdfReceptor
        ])
    
    def fill_xml(self):
        """
        Extiendo el método fill_xml del Manager para incluir adenda.
        """
        xml_base = super().fill_xml()
        
        # Si hay adenda, la agrego antes del cierre de </CFE>
        if hasattr(self.comprobante, 'description') and self.comprobante.description:
            # Busco la posición de </CFE> para insertar la adenda antes
            cfe_close_pos = xml_base.rfind('</CFE>')
            if cfe_close_pos != -1:
                # Creo el elemento adenda
                adenda_elem = Element("Adenda")
                adenda_elem.text = self.comprobante.description
                adenda_xml = tostring(adenda_elem).decode()
                
                # Inserto la adenda
                xml_with_adenda = xml_base[:cfe_close_pos] + adenda_xml + xml_base[cfe_close_pos:]
                return xml_with_adenda
        
        return xml_base

    def _build_cfes_block(self):
        """
        Genera el bloque de CFEs: HEADER + cuerpo XML escapado.
        """
        lines = []
        for idx, c in enumerate(self.comprobantes, start=1):
            header = self._header_line(c, idx)
            self.comprobante = c
            body_xml = self.fill_xml()
            body_escaped = _xml_escape(body_xml)
            lines.append(f"{header}\n{body_escaped}")
        return "\n".join(lines)

    def _build_root(self, batch_name, placeholder):
        """
        Construye el XML raíz del batch, marcando siempre <Comprimido>false</Comprimido>.
        """
        root = Element('ProcesoBatch')
        SubElement(root, 'Nombre').text = batch_name
        cfes_el = SubElement(root, 'Cfes')
        cfes_el.text = placeholder
        SubElement(root, 'Comprimido').text = 'false'
        return root
    
    def _assemble_batch(self, batch_name, cfes_block):
        """
        Inserta el bloque de CFEs en el XML padre.
        """
        placeholder = '__CFES_CONTENT__'
        root = self._build_root(batch_name, placeholder)
        xml_str = tostring(root).decode()
        return xml_str.replace(placeholder, cfes_block)
    
    def _proceso_batch_xml(self, batch_name):
        cfes_block = self._build_cfes_block()
        return self._assemble_batch(batch_name, cfes_block)

    def _tiny_proceso_batch_xml(self, batch_name):
        """
        Igual que _proceso_batch_xml pero sin el nodo <Cfes>.
        """
        placeholder = '__CFES_CONTENT__'
        root = self._build_root(batch_name, placeholder)
        for e in list(root):
            if e.tag == 'Cfes':
                root.remove(e)
        xml_str = tostring(root).decode()
        return xml_str

    def send_batch(self, batch_name):
        """
        Envía el batch al servicio UCFE, siempre en XML sin comprimir.
        """
        xml = self._proceso_batch_xml(batch_name)
        req_body = self.create_req_body()
        ucfe_req = self.create_ucfe_req(MESSAGES_TYPES['batch_send'], xml)
        return self._Manager__send(req_body, ucfe_req)

    def sign_batch(self, batch_name):
        """
        (Esto no se usa pero no descarto que lo vayamos a necesitar) 
        Se solicita la firma del batch a UCFE.
        """
        xml = self._tiny_proceso_batch_xml(batch_name)
        req_body = self.create_req_body()
        ucfe_req = self.create_ucfe_req(MESSAGES_TYPES['batch_sign'], xml)
        return self._Manager__send(req_body, ucfe_req)

    def query_batch(self, batch_name):
        """
        Consulta el batch en UCFE.
        """
        xml = self._tiny_proceso_batch_xml(batch_name)
        req_body = self.create_req_body()
        ucfe_req = self.create_ucfe_req(MESSAGES_TYPES['batch_query'], xml)
        return self._Manager__send(req_body, ucfe_req)

    def create_ucfe_req(self, message_type, xml):
        """
        Crea un objeto UcfeRequirement con los datos requeridos para el batch.
        """
        UcfeReq = ucfe_requirement.UcfeRequirement()
        UcfeReq.message_type = message_type
        UcfeReq.commerce_code = self.connection_data.commerce_code
        UcfeReq.terminal_code = self.connection_data.terminal_code
        UcfeReq.cfe_xml_or_text = xml
        UcfeReq.request_date = datetime.now().strftime('%Y%m%d')
        UcfeReq.request_time = datetime.now().strftime('%H%M%S')
        return UcfeReq

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: