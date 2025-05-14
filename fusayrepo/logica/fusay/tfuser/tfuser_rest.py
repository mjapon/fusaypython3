# coding: utf-8
"""
Fecha de creacion 02/01/2020
@autor: mejg231019
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tfuser.tfuser_dao import TFuserDao
from fusayrepo.logica.fusay.tfuser.tfusersec_dao import TFuserSecDao
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_dao import TFuserRolDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.tempresa.empresa_dao import TEmpresaDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import DbComunView, TokenView

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
            secciondao = TSeccionDao(self.dbsession)
            ttpdvdao = TtpdvDao(self.dbsession)
            empresa = empresaDao.buscar_por_codigo(emp_codigo=emp_codigo)
            if empresa is None:
                return {'status': 404,
                        'msg': 'Empresa no registrada'}
            else:
                emp_esquema = empresa['emp_esquema']
                self.change_dbschema(emp_esquema)
                autenticado = fuserdao.autenticar(us_cuenta=cadenas.strip(form['username']),
                                                  us_clave=cadenas.strip(form['password']))
                """
                secciones = secciondao.listar()
                sec_id = secciones[0]['sec_id']
                """

            if autenticado:
                #user = fuserdao.find_by_email(us_email=cadenas.strip(form['username']))
                user = fuserdao.get_user(us_cuenta=cadenas.strip(form['username']))

                fusersecdao = TFuserSecDao(self.dbsession)
                secs_user = fusersecdao.get_secciones_user(us_id=user['us_id'])
                if secs_user is None or len(secs_user) == 0:
                    raise ErrorValidacionExc(
                        'No tiene asignado una sección favor solicitar al administrador que se le asigne una sección')

                defaultsec = fusersecdao.get_default_sec(secciones=secs_user)

                sec_id = defaultsec['sec_id']
                genera_token_util = GeneraTokenUtil()
                alm_codigo = secciondao.get_alm_codigo_from_sec_codigo(sec_codigo=sec_id)
                ttpdvs = ttpdvdao.listar_min(alm_codigo=alm_codigo)

                # Se loguea por defecto en el primer punto de emision
                if len(ttpdvs) == 0:
                    raise ErrorValidacionExc(
                        'No hay registrados puntos de emisió para el establecimiento (cod:{0})'.format(alm_codigo))
                tdv_codigo = ttpdvs[0]['tdv_codigo']
                token = genera_token_util.gen_token(us_id=user['us_id'], emp_codigo=empresa['emp_codigo'],
                                                    emp_esquema=empresa['emp_esquema'], sec_id=sec_id,
                                                    tdv_codigo=tdv_codigo, emp_id=empresa['emp_id'])
                return {'autenticado': autenticado,
                        'userinfo': user,
                        'seccion': defaultsec,
                        'token': token,
                        'tdv_codigo': tdv_codigo,
                        'emp': empresa['emp_id'],
                        'menu': empresa['emp_menu'],
                        'sqm': empresa['emp_esquema'],
                        'empNombreComercial': empresa['emp_nombrecomercial']}
            else:
                return {'autenticado': autenticado}


@resource(collection_path='/api/tfusertoken', path='/api/tfusertoken/{us_id}', cors_origins=('*',))
class TFuserTokenRest(TokenView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'setroles':
            tfuserroldao = TFuserRolDao(self.dbsession)
            tfusersecdao = TFuserSecDao(self.dbsession)
            form = self.get_json_body()
            us_id = form['us_id']
            roles = form['roles']
            secciones = form['secciones']
            tfuserroldao.editar(us_id, roles)
            tfusersecdao.create_from_list(us_id=us_id, secciones=secciones)
            return {'status': 200, 'msg': 'Operación Exitosa'}
        elif accion == 'creauser':
            form = self.get_json_body()
            tfuserdao = TFuserDao(self.dbsession)
            tfuserdao.crear(form=form['form'], formcli=form['formcli'])
            return {'status': 200, 'msg': 'Usuario creado existosamente'}
        elif accion == 'chkrol':
            form = self.get_json_body()
            fuserroldao = TFuserRolDao(self.dbsession)
            isuserhas = fuserroldao.user_has_permiso(user_id=self.get_user_id(), prm_abreviacion=form['rol'])
            return self.res200({'hasperm': isuserhas})
        elif accion == 'chgstate':
            form = self.get_json_body()
            tfuserdao = TFuserDao(self.dbsession)
            new_state = int(form['state'])
            result = tfuserdao.cambiar_estado(us_id=form['user'], new_state=new_state)
            if new_state == 1:
                msg = 'Se desactivó exitósamente este usuario'
            else:
                msg = 'Se activó exitósamente este usuario'

            return self.res200({'msg': msg, 'resultado': result})
        elif accion == 'updclave':
            fuserroldao = TFuserRolDao(self.dbsession)
            tfuserdao = TFuserDao(self.dbsession)
            if fuserroldao.user_has_permiso(self.user_id, prm_abreviacion='US_CHG_PASS'):
                form = self.get_json_body()
                res = tfuserdao.cambiar_clave(form=form, user_cambia=self.get_user_id())
                if res == 1:
                    return self.res200({'res': res, 'msg': 'Cambio exitoso de clave'})
                else:
                    return self.res200({'res': res, 'msg': 'No se pudo realizar el cambio de clave'})
            else:
                return self.res200({'res': 0, 'msg': 'No tiene permisos para realizar cambio de clave'})

    def collection_get(self):
        accion = self.get_request_param('accion')
        if accion == 'listar':
            tfuserdao = TFuserDao(self.dbsession)
            usuarios = tfuserdao.listargrid()
            return {'status': 200, 'items': usuarios}
        elif accion == 'chkexiste':
            per_id = self.get_request_param('per_id')
            tfuserdao = TFuserDao(self.dbsession)
            datoscuenta = tfuserdao.find_byperid(per_id=per_id)
            if datoscuenta is not None:
                return {'status': 200, 'datoscuenta': datoscuenta}
            else:
                return {'status': 404}
        elif accion == 'formcrea':
            tfuserdao = TFuserDao(self.dbsession)
            form = tfuserdao.get_form_crear(sec_id=self.get_sec_id())
            form['status'] = 200
            return form

    def get(self):
        us_id = self.get_request_matchdict('us_id')
        accion = self.get_request_param('accion')

        if accion == 'formedita':
            fuserdao = TFuserDao(self.dbsession)
            form_edita = fuserdao.get_form_editar(us_id=us_id)
            return {'status': 200, 'formedita': form_edita}
        elif accion == 'lpermisos':
            fuserroldao = TFuserRolDao(self.dbsession)
            permisos = fuserroldao.listar_permisos(us_id)
            return {'status': 200, 'permisos': permisos}
        elif accion == 'gmenu':
            fuserroldao = TFuserRolDao(self.dbsession)
            permisos = fuserroldao.listar_permisos(us_id)
            menu = fuserroldao.build_menu(permisos,1)
            return {'status': 200, 'menu': menu}
