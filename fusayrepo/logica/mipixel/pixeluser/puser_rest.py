# coding: utf-8
"""
Fecha de creacion 11/12/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.mipixel.pixeluser.pxuser_dao import TPixelUserDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import FusayPublicView
from cornice.resource import resource

log = logging.getLogger(__name__)


@resource(collection_path='/api/tpxuser', path='/api/tpxuser/{pxus_id}', cors_origins=('*',))
class TPxUserRest(FusayPublicView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'auth':
            form = self.get_request_json_body()
            fuserdao = TPixelUserDao(self.dbsession)

            autenticado = fuserdao.autenticar(us_cuenta=cadenas.strip(form['username']),
                                              us_clave=cadenas.strip(form['password']))
            if autenticado:
                user = fuserdao.get_user(us_cuenta=cadenas.strip(form['username']))
                genera_token_util = GeneraTokenUtil()
                token = genera_token_util.gen_token_pixel(us_id=user['pxus_id'])
                return {'autenticado': autenticado,
                        'userinfo': user,
                        'token': token}
            else:
                return {'autenticado': autenticado}
