# coding: utf-8
"""
Fecha de creacion 11/12/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.mipixel.pixel_dao import MiPixelDao
from fusayrepo.utils.pyramidutil import TokenView
from cornice.resource import resource

log = logging.getLogger(__name__)


@resource(collection_path='/api/tpixel', path='/api/tpixel/{px_id}', cors_origins=('*',))
class PixelRest(TokenView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'anular':
            jsonbody = self.get_request_json_body()
            pixeldao = MiPixelDao(self.dbsession)
            pixeldao.anular(px_id=jsonbody['px_id'], obsanula=jsonbody['px_obs'])
            return {'status': 200, 'msg': 'Registro anulado exitosamente'}

        elif accion == 'confirmar':
            jsonbody = self.get_request_json_body()
            pixeldao = MiPixelDao(self.dbsession)
            pixeldao.confirmar(px_id=jsonbody['px_id'], obs_confirma=jsonbody['px_obs'])
            return {'status': 200, 'msg': 'Registro confirmado exitosamente'}

    def collection_get(self):
        accion = self.get_request_param('accion')
        if accion == 'listar':
            pixeldao = MiPixelDao(self.dbsession)
            statusactivo = 2
            items = pixeldao.listar(estado=statusactivo)
            return {'status': 200, 'items': items}
        elif accion == 'listarall':
            pixeldao = MiPixelDao(self.dbsession)
            items = pixeldao.listar_all()
            return {'status': 200, 'items': items}
