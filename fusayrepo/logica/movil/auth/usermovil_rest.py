# coding: utf-8
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tfuser.tfuser_dao import TFuserDao
from fusayrepo.logica.movil.auth.usermovil_dao import TUserEmailDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import DbComunView

from cornice.resource import resource


@resource(collection_path='/api/movil/auth', path='/api/movil/auth/{email}', cors_origins=('*',))
class TUserEmailRest(DbComunView):

    def collection_post(self):
        self.change_dbschema('public')
        form = self.get_request_json_body()
        useremaildao = TUserEmailDao(self.dbsession)
        input_email = cadenas.strip(form['username'])
        input_pass = cadenas.strip(form['password'])
        if len(input_email) == 0 or len(input_pass) == 0:
            raise ErrorValidacionExc('Debe ingresar el usuario y clave')

        autenticado = useremaildao.autenticar(email=input_email,
                                              clave=input_pass)
        if autenticado:
            userinfo = useremaildao.get_user_info(email=input_email)
            if userinfo is not None:
                empresas = userinfo['empresas']
                emp_schemas = useremaildao.get_emp_schemas(empcods=empresas)
                default_emp = empresas[0]
                default_schema = emp_schemas[0]['emp_esquema']
                self.change_dbschema(default_schema)
                userdao = TFuserDao(self.dbsession)
                userempinfo = userdao.find_by_email(us_email=input_email)

                genera_token_util = GeneraTokenUtil()
                token = genera_token_util.gen_movil_token(us_id=userempinfo['us_id'], us_email=input_email,
                                                          default_emp=default_emp,
                                                          default_scheme=default_schema)
                return {
                    'auth': autenticado,
                    'userinfo': userempinfo,
                    'token': token,
                    'empresas': emp_schemas
                }
        else:
            return {'auth': False}


@resource(collection_path='/api/movil/authEmail', path='/api/movil/authEmail/{email}', cors_origins=('*',))
class TUEmailRest(DbComunView):

    def collection_post(self):
        self.change_dbschema('public')
        form = self.get_request_json_body()
        useremaildao = TUserEmailDao(self.dbsession)
        input_email = cadenas.strip(form['username'])
        if len(input_email) == 0:
            raise ErrorValidacionExc('Debe ingresar un correo de google')

        autenticado = useremaildao.autenticarEmail(email=input_email)
        if autenticado:
            userinfo = useremaildao.get_user_info(email=input_email)
            if userinfo is not None:
                empresas = userinfo['empresas']
                emp_schemas = useremaildao.get_emp_schemas(empcods=empresas)
                default_emp = empresas[0]
                default_schema = emp_schemas[0]['emp_esquema']
                self.change_dbschema(default_schema)
                userdao = TFuserDao(self.dbsession)
                userempinfo = userdao.find_by_email(us_email=input_email)

                genera_token_util = GeneraTokenUtil()
                token = genera_token_util.gen_movil_token(us_id=userempinfo['us_id'], us_email=input_email,
                                                          default_emp=default_emp,
                                                          default_scheme=default_schema)
                return {
                    'auth': autenticado,
                    'userinfo': userempinfo,
                    'token': token,
                    'empresas': emp_schemas
                }
        else:
            return {'autenticado': autenticado}
