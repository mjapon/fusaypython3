# coding: utf-8
"""
Fecha de creacion 10/11/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuser.tfuser_dao import TFuserDao
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_model import TFuserRol
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.trol.trol_dao import TRolDao

log = logging.getLogger(__name__)


class TFuserRolDao(BaseDao):

    def crear(self, us_id, listaroles):
        for rol in listaroles:
            tfuserrol = TFuserRol()
            tfuserrol.us_id = us_id
            tfuserrol.rl_id = rol['rl_id']
            tfuserrol.usrl_fechacrea = datetime.datetime.now()
            self.dbsession.add(tfuserrol)

    def get_form_editar(self, us_id):
        tfuserdao = TFuserDao(self.dbsession)
        tfuser = tfuserdao.find_byid(us_id=us_id)
        if tfuser is not None:
            tpersonadao = TPersonaDao(self.dbsession)
            tpersona = tpersonadao.get_entity_byid(per_id=tfuser.per_id)
            if tpersona is not None:
                troldao = TRolDao(self.dbsession)
                allroles = troldao.listar()
                rolesuser = self.listar(us_id=us_id)
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
                    'persona': tpersona.__json__(),
                    'roles': allroles
                }
                return form

        return None

    def editar(self, us_id, listaroles):
        current_roles = self.dbsession.query(TFuserRol).filter(TFuserRol.us_id == us_id).all()
        for rol in current_roles:
            self.dbsession.delete(rol)

        self.crear(us_id, listaroles)

    def listar(self, us_id):
        sql = """select a.us_id, t.rl_name, t.rl_id from tfuserrol a join trol t on a.rl_id = t.rl_id
        where a.us_id = {0}""".format(us_id)

        tupla_desc = ('us_id', 'rl_name', 'rl_id')
        return self.all(sql, tupla_desc)

    def listar_permisos(self, us_id):
        sql = """
        select fr.us_id, rol.rl_name, rol.rl_id, per.prm_nombre, per.prm_abreviacion from tfuserrol fr
        join trol rol on fr.rl_id = rol.rl_id
        join tpermisorol perol on fr.rl_id = perol.rl_id
        join tpermiso per on perol.prm_id = per.prm_id
        where fr.us_id = {0} and rol.rl_estado = 0 and per.prm_estado = 0
        """.format(us_id)

        tupla_desc = ('us_id', 'rl_name', 'rl_id', 'prm_nombre', 'prm_abreviacion')
        return self.all(sql, tupla_desc)

    def build_menu(self, permisos):
        all_menu = {
            '*': {'label': 'Inicio', 'icon': 'pi pi-fw pi-home', 'routerLink': ['/lghome']},
            'TK_LISTAR': {'label': 'Tickets', 'icon': 'pi pi-fw pi-ticket', 'routerLink': ['/tickets']},
            'IG_LISTAR': {'label': 'Ingresos y Gastos', 'icon': 'pi pi-fw pi-sort-alt', 'routerLink': ['/vtickets']},
            'PRODS_LISTAR': {'label': 'Productos', 'icon': 'pi pi-fw pi-th-large', 'routerLink': ['/mercaderia']},
            'HIST_LISTAR': {'label': 'Historias Clínicas', 'icon': 'pi pi-fw pi-calendar',
                            'routerLink': ['/historiaclinica/1']},
            'HISTO_LISTAR': {'label': 'Historias Clínicas', 'icon': 'pi pi-fw pi-bell',
                             'routerLink': ['/historiaclinica/2']},
            'RL_LISTAR': {'label': 'Roles', 'icon': 'pi pi-fw pi-bookmark', 'routerLink': ['/roles']},
            'US_LISTAR': {'label': 'Usuarios', 'icon': 'pi pi-fw pi-users', 'routerLink': ['/usuarios']}
        }

        menu = []
        #menu.append(all_menu['*'])
        permisosSet = set()
        for perm in permisos:
            abrperm = perm['prm_abreviacion']
            permisosSet.add(abrperm)

        for key in all_menu.keys():
            if key in permisosSet:
                menu.append(all_menu[key])

        return menu
