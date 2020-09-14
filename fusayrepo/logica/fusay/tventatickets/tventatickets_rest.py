# coding: utf-8
"""
Fecha de creacion 9/14/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tventatickets.tventatickets_dao import TVentaTicketsDao
from fusayrepo.utils.ivautil import redondear
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tventaticket', path='/api/tventaticket/{vt_id}', cors_origins=('*',))
class TVentaTicketsRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        vtdao = TVentaTicketsDao(self.dbsession)
        if 'form' == accion:
            form = vtdao.get_form()
            tiposrubro = vtdao.get_tipos_rubro()
            return {'status': 200, 'form': form, 'tiposrubro': tiposrubro}
        if 'listar' == accion:
            res = vtdao.listar()
            data = res['data']
            sumamonto = sum(it['vt_monto'] for it in data)
            return {'status': 200, 'res': res, 'suma': redondear(sumamonto, 2)}

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'guardar':
            form = self.get_request_json_body()
            vtdao = TVentaTicketsDao(self.dbsession)
            vtdao.crear(form)
            return {'status': 200, 'msg': 'Registro exitoso'}

        elif accion == 'anular':
            form = self.get_request_json_body()
            vt_id = form['vt_id']
            vtdao = TVentaTicketsDao(self.dbsession)
            vtdao.anular(vt_id)
            return {'status': 200, 'msg': 'Registro anulado existósamemente'}

        elif accion == 'confirmar':
            form = self.get_request_json_body()
            vt_id = form['vt_id']
            vtdao = TVentaTicketsDao(self.dbsession)
            vtdao.confirmar(vt_id)
            return {'status': 200, 'msg': 'Registro confirmado exitosamente'}
