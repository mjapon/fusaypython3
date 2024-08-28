# coding: utf-8
"""
Fecha de creacion 3/5/20
@autor: mjapon
"""
import logging
from datetime import datetime

from cornice.resource import resource

from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.fusay.ttickets.tticket_dao import TTicketDao
from fusayrepo.utils import fechas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tticket', path='/api/tticket/{tk_id}', cors_origins=('*',))
class TTicketRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        ticket_dao = TTicketDao(self.dbsession)
        if 'form' == accion:
            persona_dao = TPersonaDao(self.dbsession)
            tk_dia = fechas.parse_fecha(datetime.now())
            form = ticket_dao.get_form(tk_dia, self.get_sec_id())
            formcli = persona_dao.get_form()
            secciondao = TSeccionDao(self.dbsession)
            datossec = secciondao.get_byid(sec_id=self.get_sec_id())
            return {'status': 200, 'form': form, 'formcli': formcli, 'seccion': datossec}

        elif 'servticktes' == accion:
            itemconfigdao = TItemConfigDao(self.dbsession)
            prods = itemconfigdao.get_prods_for_tickets()
            return {'status': 200, 'items': prods}

        elif 'forml' == accion:
            tsecciondao = TSeccionDao(self.dbsession)
            secs = tsecciondao.listar()
            secciones = [{'sec_id': 0, 'sec_nombre': 'Todos'}] + secs
            sec_id = self.get_sec_id()
            itemconfigdao = TItemConfigDao(self.dbsession)
            prods = itemconfigdao.get_prods_for_tickets()
            hoy = fechas.parse_fecha(datetime.now())
            return {'dia': hoy, 'secciones': secciones, 'sec_def': sec_id,
                    'prods': prods, 'desde': hoy, 'hasta': hoy}

        elif 'listar' == accion:
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            seccion = self.get_request_param('seccion')
            servicios = self.get_request_param('servicios')
            res = ticket_dao.listar(dia=self.get_request_param('dia'), sec_id=seccion,
                                    desde=desde, hasta=hasta, servicios=servicios)
            data = res['data']
            sumamonto = sum(it['tk_costo'] for it in data)
            return {'status': 200, 'res': res, 'suma': sumamonto}

        elif 'gdet' == accion:
            tkid = self.get_request_param('tkid')
            datosticket = ticket_dao.get_detalles(tk_id=tkid)
            return self.res200({'datosticket': datosticket})
        elif 'gformed' == accion:
            tkid = self.get_request_param('tkid')
            res = ticket_dao.get_form_edit(tk_id=tkid)
            return self.res200({'form': res['form'], 'servicios': res['servicios']})
        elif 'histservpac' == accion:
            perid = self.get_request_param('perid')
            histserv = ticket_dao.listar_servicios_persona(per_id=perid)
            return self.res200({'histserv': histserv})

    def collection_post(self):
        accion = self.get_request_param('accion')
        ticket_dao = TTicketDao(self.dbsession)

        if accion == 'guardar':
            allform = self.get_request_json_body()
            formcli = allform['form_cli']
            form = allform['form']

            tkid = ticket_dao.crear(form, formcli, self.get_user_id(), self.get_sec_id())
            return {'status': 200, 'msg': 'Registrado', 'tk_id': tkid}
        elif accion == 'upd':
            form = self.get_json_body()
            ticket_dao.actualizar(tk_id=form['tk_id'], form=form)
            return {'status': 200, 'msg': 'Actualizado exitósamente'}

        if accion == 'anular':
            form = self.get_json_body()
            tk_id = form['tk_id']

            ticket_dao.anular(tk_id=tk_id)
            return {'status': 200, 'msg': 'Ticket anulado'}
