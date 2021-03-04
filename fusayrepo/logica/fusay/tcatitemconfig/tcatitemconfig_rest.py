# coding: utf-8
"""
Fecha de creacion 3/11/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tcatitemconfig.tcatitemconfig_dao import TCatItemConfigDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/categorias', path='/api/categorias/{catic_id}', cors_origins=('*',))
class TCatItemConfigRest(TokenView):

    def collection_get(self):

        accion = self.get_rqpa()
        catdao = TCatItemConfigDao(self.dbsession)
        if accion == 'listar':
            res = catdao.listar()
            return {'items': res, 'status': 200}
        elif accion == 'formcrea':
            form = catdao.get_form_crea()
            return self.res200({'form': form})

    def post(self):
        accion = self.get_request_param('accion')
        if accion == 'crear':
            catdao = TCatItemConfigDao(self.dbsession)
            jsonbody = self.get_request_json_body()
            catdao.crear(nombre=jsonbody['catic_nombre'], caja=jsonbody['catic_caja'])
            return {'status': 200, 'msg': u'Registro exitoso'}
        elif accion == 'actualizar':
            cat_id = self.get_request_matchdict('catic_id')
            jsonbody = self.get_request_json_body()
            catdao = TCatItemConfigDao(self.dbsession)
            catdao.actualizar(cat_id, jsonbody['catic_nombre'], jsonbody['catic_caja'])
            return {'status': 200, 'msg': u'Actualización exitosa'}
        elif accion == 'anular':
            cat_id = self.get_request_matchdict('catic_id')
            catdao = TCatItemConfigDao(self.dbsession)
            catdao.anular(cat_id)
            return {'status': 200, 'msg': u'Categoria anulada exitosamente'}
