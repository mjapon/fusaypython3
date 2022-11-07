# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.compele.tcontribuyente.tcontribuyente_dao import TContribuyenteDao
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import DbComunView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tcontrib', path='/api/tcontrib/{cnt_id}', cors_origins=('*',))
class FacteContribRest(DbComunView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'auth':
            form = self.get_request_json_body()
            tcontrib_dao = TContribuyenteDao(self.dbsession)
            autenticado = tcontrib_dao.autenticar(user=form['user'], password=form['password'])

            if autenticado:
                genera_token_util = GeneraTokenUtil()
                datoscontrib = tcontrib_dao.get_datos_contrib(cnt_ciruc=form['user'])
                token = genera_token_util.get_token_facte(cnt_ciruc=form['user'],
                                                          cnt_email=datoscontrib['cnt_email'],
                                                          cnt_id=datoscontrib['cnt_id'])

                return {
                    'autenticado': autenticado,
                    'userinfo': datoscontrib,
                    'token': token
                }
            else:
                return {'autenticado': autenticado}
