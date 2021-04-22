# coding: utf-8
"""
Fecha de creacion 4/21/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/ttpdv', path='/api/ttpdv/{tdv_codigo}', cors_origins=('*',))
class TtpdvRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        ttpdvdao = TtpdvDao(self.dbsession)
        if accion == 'listarm':
            ttpdvs = ttpdvdao.listar_min_from_sec_codigo(sec_id=self.get_sec_id())
            return self.res200({'ttpdvs': ttpdvs})

    def collection_post(self):
        accion = self.get_rqpa()
        if accion == 'setttpdv':
            form = self.get_json_body()
            tdv_codigo = form['tdv_codigo']
            auth_token = self.request.headers['x-authtoken']
            genera_token_util = GeneraTokenUtil()
            token = genera_token_util.update_tdvcod_token(token=auth_token, tdv_codigo=tdv_codigo)
            return {'status': 200, 'token': token}
