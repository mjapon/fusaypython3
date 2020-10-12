# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tpermiso.tpermiso_dao import TPermisoDao
from fusayrepo.logica.fusay.tpermisorol.tpermisorol_dao import TPermisoRolDao
from fusayrepo.logica.fusay.tpermisorol.tpermisorol_model import TPermisoRol
from fusayrepo.logica.fusay.trol.trol_model import TRol
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TRolDao(BaseDao):

    def listargrid(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='roles')
        return data

    def listar(self):
        sql = "select rl_id, rl_name, rl_desc, rl_abreviacion, rl_grupo from trol where rl_estado=0 order by rl_name"
        tupla_desc = ('rl_id', 'rl_name', 'rl_desc', 'rl_abreviacion', 'rl_grupo')
        return self.all(sql, tupla_desc)

    def get_form_crea(self):
        return {
            'rl_id': 0,
            'rl_name': '',
            'rl_desc': '',
            'rl_abreviacion': '',
            'rl_grupo': 0
        }

    def existe(self, nombre, abreviacion):
        sql = "select count(*) as cuenta from trol where rl_name = '{0}' or rl_abreviacion = '{1}' and rl_estado =0 " \
            .format(cadenas.strip_upper(nombre), cadenas.strip_upper(abreviacion))

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def existe_nombre(self, nombre):
        sql = "select count(*) as cuenta from trol where rl_name = '{0}' and rl_estado =0 " \
            .format(cadenas.strip_upper(nombre))

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def existe_abreviacion(self, abreviacion):
        sql = "select count(*) as cuenta from trol where rl_abreviacion = '{0}' and rl_estado =0 " \
            .format(cadenas.strip_upper(abreviacion))

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form, permisos, user_crea):
        nombre = cadenas.strip_upper(form['rl_name'])
        desc = cadenas.strip_upper(form['rl_desc'])
        abrevicacion = cadenas.strip_upper(form['rl_abreviacion'])
        grupo = form['rl_grupo']

        if not cadenas.es_nonulo_novacio(nombre):
            raise ErrorValidacionExc('Debe ingresar el nombre del rol')

        if not cadenas.es_nonulo_novacio(abrevicacion):
            raise ErrorValidacionExc('Debe ingresar la abreviacion del rol')

        if permisos is None or len(permisos) == 0:
            raise ErrorValidacionExc('Debe ingresar los permisos que tiene el rol')

        if self.existe(nombre, abrevicacion):
            raise ErrorValidacionExc('Ya esite un rol registrado con el nombre o la abrevicación especificada')

        trol = TRol()
        trol.rl_name = nombre
        trol.rl_abreviacion = abrevicacion
        trol.rl_desc = desc
        trol.rl_grupo = grupo
        trol.rl_estado = 0
        trol.rl_fechacrea = datetime.datetime.now()
        trol.rl_usercrea = user_crea

        self.dbsession.add(trol)
        self.dbsession.flush()

        rl_id = trol.rl_id

        for permiso in permisos:
            permisorol = TPermisoRol()
            prm_id = permiso['prm_id']
            permisorol.prm_id = prm_id
            permisorol.rl_id = rl_id
            permisorol.prl_fechacrea = datetime.datetime.now()
            self.dbsession.add(permisorol)

    def find_byid(self, rl_id):
        return self.dbsession.query(TRol).filter(TRol.rl_id == rl_id).first()

    def anular(self, rl_id):
        trol = self.find_byid(rl_id)
        if trol is not None:
            ts = datetime.datetime.now().isoformat()
            deleted_abr = trol.rl_abreviacion + '_deleted_ts_' + ts
            trol.rl_abreviacion = deleted_abr[:49]
            trol.rl_estado = 1
            trol.rl_fechaanula = datetime.datetime.now()
            self.dbsession.add(trol)

    def get_form_edita(self, rl_id):
        trol = self.find_byid(rl_id=rl_id)
        tpermisoroldao = TPermisoRolDao(self.dbsession)
        tpermisodao = TPermisoDao(self.dbsession)
        # rl_marca

        if trol is not None:
            roljson = trol.__json__()
            permisos_rol = tpermisoroldao.get_permisos(id_rol=rl_id)
            permisorolmap = set()
            for permiso in permisos_rol:
                permisorolmap.add(permiso['prm_id'])

            all_permisos = tpermisodao.listar()
            for perm in all_permisos:
                prm_id = perm['prm_id']
                if prm_id in permisorolmap:
                    perm['rl_marca'] = True
                else:
                    perm['rl_marca'] = False

            roljson['permisos'] = all_permisos
            return roljson
        return None

    def editar(self, form, permisos):
        rl_id = form['rl_id']
        trol = self.find_byid(rl_id)
        if trol is not None:
            nombre = cadenas.strip_upper(form['rl_name'])
            desc = cadenas.strip_upper(form['rl_desc'])
            abrevicacion = cadenas.strip_upper(form['rl_abreviacion'])

            current_rl_name = trol.rl_name
            current_rl_abr = trol.rl_abreviacion

            if current_rl_name != nombre:
                if self.existe_nombre(nombre):
                    raise ErrorValidacionExc('Ya existe un rol con el nombre indicado, ingrese otro')
                else:
                    trol.rl_name = nombre
            if current_rl_abr != abrevicacion:
                if self.existe_abreviacion(abrevicacion):
                    raise ErrorValidacionExc('Ya existe un rol con la abreviacion indicada, ingrese otra')
                else:
                    trol.rl_abreviacion = abrevicacion

            trol.rl_desc = desc
            trol.rl_fechaedita = datetime.datetime.now()

            tpermisosrol = self.dbsession.query(TPermisoRol).filter(TPermisoRol.rl_id == rl_id).all()
            for tpermisorol in tpermisosrol:
                self.dbsession.delete(tpermisorol)

            for permiso in permisos:
                permisorol = TPermisoRol()
                prm_id = permiso['prm_id']
                permisorol.prm_id = prm_id
                permisorol.rl_id = rl_id
                permisorol.prl_fechacrea = datetime.datetime.now()
                self.dbsession.add(permisorol)
