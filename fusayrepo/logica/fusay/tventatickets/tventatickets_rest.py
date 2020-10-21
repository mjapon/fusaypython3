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
            tipos = vtdao.get_tipos_cuentas()
            cuentas = vtdao.get_cuentas(tipo=1)
            return {'status': 200, 'form': form, 'tipos': tipos, 'cuentas': cuentas}
        elif 'listar' == accion:
            tipo = self.get_request_param('tipo')
            cuenta = self.get_request_param('cuenta')
            res = vtdao.listar(tipo=tipo, cuenta=cuenta)
            data = res['data']
            sumamonto = sum(it['vt_monto'] for it in data)
            return {'status': 200, 'res': res, 'suma': redondear(sumamonto, 2)}
        elif 'forml' == accion:
            tipos = vtdao.get_tipos_cuentas()
            cuentas = vtdao.get_cuentas(tipo=1)
            return {'status': 200, 'tipos': tipos, 'cuentas': cuentas}
        elif 'gcuentas' == accion:
            tipo = self.get_request_param('tipo')
            cuentas = vtdao.get_cuentas(tipo=tipo)
            return {'status': 200, 'cuentas': cuentas}

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