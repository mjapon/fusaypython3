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
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.tempresa.empresa_dao import TEmpresaDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import DbComunView


@resource(collection_path='/api/movil/tfuser', path='/api/movil/tfuser/{us_id}', cors_origins=('*',))
class TFuserMovilRest(DbComunView):

    def collection_get(self):
        empdao = TEmpresaDao(self.dbsession)
        datosemp = empdao.get_datos_emp_public(emp_codigo='fusay')
        return {'status': 200, 'empresa': datosemp}

    def collection_post(self):
        empdao = TEmpresaDao(self.dbsession)
        body = self.get_json_body()

        empresa = body['empresa']
        username = body['username']
        password = body['password']

        empresa = empdao.buscar_por_codigo(emp_codigo=empresa)
        if empresa is None:
            return {'status': 404, 'msg': 'Empresa no registrada', 'autenticado': False}
        else:
            emp_esquema = empresa['emp_esquema']
            self.change_dbschema(emp_esquema)
            tfuserdao = TFuserDao(self.dbsession)
            fusersecdao = TFuserSecDao(self.dbsession)
            secdao = TSeccionDao(self.dbsession)
            ttpdvdao = TtpdvDao(self.dbsession)

            autenticado = tfuserdao.autenticar(us_cuenta=username, us_clave=password)

            user = tfuserdao.get_user(us_cuenta=cadenas.strip(username))
            secs_user = fusersecdao.get_secciones_user(us_id=user['us_id'])
            persona = {'per_id': user['per_id'],
                       'per_ciruc': user['per_ciruc'],
                       'per_nombres': user['per_nombres'],
                       'per_apellidos': user['per_apellidos'],
                       'per_direccion': user['per_direccion'],
                       'per_telf': user['per_telf'],
                       'per_movil': user['per_movil'],
                       'per_email': user['per_email']}
            if secs_user is None or len(secs_user) == 0:
                raise ErrorValidacionExc(
                    'No tiene asignado una sección favor solicitar al administrador que se le asigne una sección')

            defaultsec = fusersecdao.get_default_sec(secciones=secs_user)

            sec_id = defaultsec['sec_id']
            genera_token_util = GeneraTokenUtil()
            alm_codigo = secdao.get_alm_codigo_from_sec_codigo(sec_codigo=sec_id)

            ttpdvs = ttpdvdao.listar_min(alm_codigo=alm_codigo)

            # Se loguea por defecto en el primer punto de emision
            if len(ttpdvs) == 0:
                raise ErrorValidacionExc(
                    'No hay registrados puntos de emisió para el establecimiento (cod:{0})'.format(alm_codigo))
            tdv_codigo = ttpdvs[0]['tdv_codigo']
            token = genera_token_util.gen_token(us_id=user['us_id'], emp_codigo=empresa['emp_codigo'],
                                                emp_esquema=empresa['emp_esquema'], sec_id=sec_id,
                                                tdv_codigo=tdv_codigo)

            return {'status': 200, 'msg': 'Post ejectutado exitósamente',
                    'autenticado': autenticado,
                    'token': token,
                    'secid': sec_id,
                    'tdvcodigo': tdv_codigo,
                    'persona': persona}
