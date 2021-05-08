# coding: utf-8
"""
Fecha de creacion 02/01/2020
@autor: mejg231019
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tfuser.tfuser_model import TFuser
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_dao import TFuserRolDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.trol.trol_dao import TRolDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TFuserDao(BaseDao):

    def find_byid(self, us_id):
        return self.dbsession.query(TFuser).filter(TFuser.us_id == us_id).first()

    def autenticar(self, us_cuenta, us_clave):
        sql = """
        select count(*) as cuenta from tfuser where us_cuenta = '{0}' and us_clave = '{1}'  
        """.format(us_cuenta, us_clave)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def get_user(self, us_cuenta):
        sql = """select a.us_id,
        a.per_id,
        a.us_cuenta,
        a.us_fechacrea,
        a.us_estado,
        b.per_ciruc,
        b.per_nombres,
        b.per_apellidos,
        b.per_direccion,
        b.per_telf,
        b.per_movil,
        b.per_email,
        b.per_tipo,
        b.per_lugnac from tfuser a
        join tpersona b on a.per_id = b.per_id           
         where us_cuenta = '{0}'""".format(us_cuenta)

        tupla_desc = ('us_id', 'per_id', 'us_cuenta', 'us_fechacrea', 'us_estado',
                      'per_ciruc', 'per_nombres', 'per_apellidos', 'per_direccion', 'per_telf',
                      'per_movil', 'per_email', 'per_tipo', 'per_lugnac')

        datos_user = self.first(sql=sql, tupla_desc=tupla_desc)
        return datos_user

    def listar(self):
        sql = """
            select a.us_id, a.us_cuenta, a.us_clave, p.per_ciruc, coalesce(p.per_nombres,'')||' '||coalesce(p.per_apellidos,'') as nomapel,
            case when a.us_estado = 0 then 'ACTIVO' else 'INACTIVO' end as estado            
            from tfuser a join tpersona p on a.per_id = p.per_id order by 5 asc 
        """
        tupla_desc = ('us_id', 'us_cuenta', 'us_clave', 'per_ciruc', 'nomapel', 'estado')

        return self.all(sql, tupla_desc)

    def listargrid(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='usuarios')
        return data

    def get_form_crear(self):
        form = {
            'us_id': 0,
            'us_cuenta': '',
            'us_clave': '',
            'us_confirmclave': '',
            'roles': []
        }
        tpersonadao = TPersonaDao(self.dbsession)
        formcli = tpersonadao.get_form()

        troldao = TRolDao(self.dbsession)
        allroles = troldao.listar()
        for rol in allroles:
            rol['rl_marca'] = False

        form['roles'] = allroles

        return {'form': form, 'formcli': formcli}

    def get_form_editar(self, us_id):
        tfuserdao = TFuserDao(self.dbsession)
        tfuser = tfuserdao.find_byid(us_id=us_id)
        tpersonadao = TPersonaDao(self.dbsession)

        tfuserroldao = TFuserRolDao(self.dbsession)

        if tfuser is not None:
            tpersona = tpersonadao.get_entity_byid(per_id=tfuser.per_id)
            if tpersona is not None:
                troldao = TRolDao(self.dbsession)
                allroles = troldao.listar()
                rolesuser = tfuserroldao.listar(us_id=us_id)
                rolesmap = set()
                for rol in rolesuser:
                    rolesmap.add(rol['rl_id'])

                for rol in allroles:
                    rl_id = rol['rl_id']
                    if rl_id in rolesmap:
                        rol['rl_marca'] = True
                    else:
                        rol['rl_marca'] = False

                form = {
                    'us_id': us_id,
                    'us_cuenta': tfuser.us_cuenta,
                    'roles': allroles
                }

                formcli = {
                    'per_id': tpersona.per_id,
                    'per_ciruc': tpersona.per_ciruc,
                    'per_nombres': tpersona.per_nombres,
                    'per_apellidos': tpersona.per_apellidos,
                    'per_direccion': tpersona.per_direccion,
                    'per_telf': tpersona.per_telf,
                    'per_movil': tpersona.per_movil,
                    'per_email': tpersona.per_email,
                    'per_tipo': tpersona.per_tipo,
                    'per_lugnac': tpersona.per_lugnac,
                    'per_nota': tpersona.per_nota
                }
                return {'form': form, 'formcli': formcli}

        return None

    def find_byperid(self, per_id):
        sql = "select us_id, us_cuenta, per_id, us_fechacrea, us_estado from tfuser where per_id = {0}".format(per_id)
        tupla_desc = ('us_id', 'us_cuenta', 'per_id', 'us_fechacrea', 'us_estado')
        return self.first(sql, tupla_desc)

    def existe_cuenta(self, us_cuenta):
        sql = "select count(*) as cuenta from tfuser where us_cuenta = '{0}'".format(cadenas.strip(us_cuenta))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form, formcli):
        tpersonadao = TPersonaDao(self.dbsession)
        per_id = formcli['per_id']
        if per_id is None or per_id == 0:
            per_id = tpersonadao.crear(formcli, permit_ciruc_null=False)
        else:
            tpersonadao.actualizar(per_id, formcli)

        # Verificar si ya existe una cuenta registrada para esta persona
        datoscuenta = self.find_byperid(per_id=per_id)
        if datoscuenta is not None:
            raise ErrorValidacionExc('No se puede crear una cuenta para esta persona, ya existe una cuenta registrada')

        us_cuenta = cadenas.strip(form['us_cuenta'])
        us_clave = cadenas.strip(form['us_clave'])
        us_confirmclave = cadenas.strip(form['us_confirmclave'])

        if len(us_cuenta) < 4:
            raise ErrorValidacionExc('El nombre de cuenta es muy corto, favor revisar')

        if self.existe_cuenta(us_cuenta):
            raise ErrorValidacionExc('Ya existe un usuario registrado con este nombre de cuenta')

        if len(us_clave) < 4:
            raise ErrorValidacionExc('La clave es muy corta, ingrese otra')

        if us_clave != us_confirmclave:
            raise ErrorValidacionExc('Las claves no coinciden, favor verifique')

        tfuser = TFuser()
        tfuser.per_id = per_id
        tfuser.us_cuenta = us_cuenta
        tfuser.us_clave = us_clave
        tfuser.us_fechacrea = datetime.now()

        self.dbsession.add(tfuser)
        self.dbsession.flush()

        us_id = tfuser.us_id
        tfuserroldao = TFuserRolDao(self.dbsession)
        tfuserroldao.crear(us_id=us_id, listaroles=form['roles'])
