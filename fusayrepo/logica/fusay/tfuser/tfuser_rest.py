# coding: utf-8
"""
Fecha de creacion 02/01/2020
@autor: mejg231019
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.tempresa.empresa_dao import TEmpresaDao
from fusayrepo.logica.fusay.tfuser.tfuser_dao import TFuserDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import DbComunView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tfuser', path='/api/tfuser/{us_id}', cors_origins=('*',))
class TFuserRest(DbComunView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'auth':
            form = self.get_request_json_body()
            fuserdao = TFuserDao(self.dbsession)
            emp_codigo = cadenas.strip(form['empresa'])
            empresaDao = TEmpresaDao(self.dbsession)

            self.change_dbschema('public')
            empresa = empresaDao.buscar_por_codigo(emp_codigo=emp_codigo)
            if empresa is None:
                return {'status': 404,
                        'msg': 'Empresa no registrada'}
            else:
                emp_esquema = empresa['emp_esquema']
                self.change_dbschema(emp_esquema)
                autenticado = fuserdao.autenticar(us_cuenta=cadenas.strip(form['username']),
                                                  us_clave=cadenas.strip(form['password']))
                secciones = TSeccionDao(self.dbsession).listar()
                sec_id = secciones[0]['sec_id']

            if autenticado:
                user = fuserdao.get_user(us_cuenta=cadenas.strip(form['username']))
                genera_token_util = GeneraTokenUtil()
                token = genera_token_util.gen_token(us_id=user['us_id'], emp_codigo=empresa['emp_codigo'],
                                                    emp_esquema=empresa['emp_esquema'], sec_id=sec_id)
                return {'autenticado': autenticado,
                        'userinfo': user,
                        'seccion': secciones[0],
                        'token': token,
                        'menu': empresa['emp_menu'],
                        'empNombreComercial': empresa['emp_nombrecomercial']}
            else:
                return {'autenticado': autenticado}


    def get(self):
        us_id = self.get_request_matchdict('us_id')
        fuserdao = TFuserDao(self.dbsession)
        res = fuserdao.get_user(us_id)
        return res


