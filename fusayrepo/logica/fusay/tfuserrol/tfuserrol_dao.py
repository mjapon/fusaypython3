# coding: utf-8
"""
Fecha de creacion 10/11/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_model import TFuserRol
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TFuserRolDao(BaseDao):

    def crear(self, us_id, listaroles):
        for rol in listaroles:
            tfuserrol = TFuserRol()
            tfuserrol.us_id = us_id
            tfuserrol.rl_id = rol['rl_id']
            tfuserrol.usrl_fechacrea = datetime.datetime.now()
            self.dbsession.add(tfuserrol)

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

        paramsdao = TParamsDao(self.dbsession)
        hasplanesvalue = paramsdao.get_param_value('EMP_HASPLANES')
        hasplanes = False
        if hasplanesvalue is not None:
            hasplanes = cadenas.strip(hasplanesvalue) == '1'

        contabilidad_list = [
            {'label': 'Ingresos y Gastos', 'icon': '', 'routerLink': ['/vtickets']},
            {'label': 'Libro Diario', 'icon': 'pi pi-fw pi-book', 'routerLink': ['/librodiario']},
            {'label': 'Libro Mayor', 'icon': '', 'routerLink': ['/libromayor']},
            # {'label': 'Cuentas', 'icon': '', 'routerLink': ['/rubros']},
            {'label': 'Plan de cuentas', 'icon': '', 'routerLink': ['/plancuentas']},
            {'label': 'Balance General', 'icon': '', 'routerLink': ['/contabilidad/balancegeneral']},
            {'label': 'Estado de Resultados', 'icon': '', 'routerLink': ['/contabilidad/estadoresultados']}
        ]
        tickets_list = [
            {'label': 'Listado', 'icon': 'pi pi-fw pi-ticket', 'routerLink': ['/tickets']},
            {'label': 'Crear', 'icon': 'pi pi-fw pi-file', 'routerLink': ['/ticket/form']}
        ]

        prods_list = [
            {'label': 'Listado', 'icon': '', 'routerLink': ['/mercaderia']},
            {'label': 'Categorias', 'icon': '', 'routerLink': ['/categorias']}
        ]

        if hasplanes:
            prods_list.append({'label': 'Planes', 'icon': '', 'routerLink': ['/planes']})

        users_list = [
            {'label': 'Admin Usuarios', 'icon': 'pi pi-fw pi-users', 'routerLink': ['/usuarios']},
            {'label': 'Admin Roles', 'icon': 'pi pi-fw pi-bookmark', 'routerLink': ['/roles']}
        ]

        hist_list = [
            {'label': 'Administrar', 'icon': 'pi pi-fw pi-calendar',
             'routerLink': ['/historiaclinica/1']}
        ]

        histo_list = [
            {'label': 'Administrar', 'icon': 'pi pi-fw pi-bell',
             'routerLink': ['/odonto']}
        ]

        ventas_list = [
            {'label': 'Movimientos', 'icon': '',
             'routerLink': ['/trndocs/1']},
            {'label': 'Emitir Factura', 'icon': 'pi pi-fw pi-money-bill',
             'routerLink': ['/trndocform/1']},
            {'label': 'Emitir nota de venta', 'icon': '',
             'routerLink': ['/trndocform/2']},
            {'label': 'Cuentas por cobrar', 'icon': '',
             'routerLink': ['/cuentasxcp/1']},
            {'label': 'Utilidades', 'icon': '',
             'routerLink': ['/utilventas']}
        ]

        compras_list = [
            {'label': 'Movimientos', 'icon': '', 'cicon': 'fas fa-shopping-basket',
             'routerLink': ['/trndocs/2']},
            {'label': 'Registrar factura', 'icon': '',
             'routerLink': ['/trndocform/7']},
            {'label': 'Cuentas por pagar', 'icon': '',
             'routerLink': ['/cuentasxcp/2']}
        ]

        refs_list = [
            {'label': 'Listado', 'icon': 'pi pi-fw pi-users',
             'routerLink': ['/referentes']},
        ]

        agn_list = [
            {'label': 'Agenda', 'icon': 'pi pi-fw pi-calendar',
             'routerLink': ['/agenda/1']},
        ]

        all_menu = {
            '*': {'label': 'Inicio', 'icon': 'pi pi-fw pi-home', 'cicon': 'fas fa-home', 'routerLink': ['/lghome']},
            'TK_LISTAR': {'label': 'Tickets', 'icon': 'pi pi-fw pi-ticket', 'cicon': 'fas fa-ticket-alt',
                          'items': tickets_list},
            'IG_LISTAR': {'label': 'Contabilidad', 'icon': 'pi pi-fw pi-book', 'cicon': 'fas fa-calculator',
                          'items': contabilidad_list},
            'PRODS_LISTAR': {'label': 'Inventario', 'icon': 'pi pi-fw pi-microsoft', 'cicon': 'fas fa-store',
                             'items': prods_list},
            'HIST_LISTAR': {'label': 'Atención Médica', 'icon': 'pi pi-fw pi-calendar',
                            'cicon': 'fas fa-stethoscope', 'items': hist_list},
            'HISTO_LISTAR': {'label': 'Atención Odontológica', 'icon': 'pi pi-fw pi-bell',
                             'cicon': 'fas fa-tooth',
                             'items': histo_list},
            'US_LISTAR': {'label': 'Usuarios', 'icon': 'pi pi-fw pi-users', 'cicon': 'fas fa-users',
                          'items': users_list},
            'VN_LISTAR': {'label': 'Ventas', 'icon': 'pi pi-fw pi-money-bill', 'cicon': 'fas fa-shopping-cart',
                          'items': ventas_list},
            'CM_LISTAR': {'label': 'Compras', 'icon': 'pi pi-fw pi-wallet', 'cicon': 'fas fa-shopping-bag',
                          'items': compras_list},
            'REF_LISTAR': {'label': 'Referentes', 'icon': 'pi pi-fw pi-users', 'cicon': 'fas fa-user-friends',
                           'items': refs_list},
            'AGN_LISTAR': {'label': 'Agenda', 'icon': 'pi pi-fw pi-calendar', 'cicon': 'far fa-calendar-plus',
                           'items': agn_list}
        }

        menu = []
        # menu.append(all_menu['*'])
        permisosSet = set()
        for perm in permisos:
            abrperm = perm['prm_abreviacion']
            permisosSet.add(abrperm)

        for key in all_menu.keys():
            if key in permisosSet:
                menu.append(all_menu[key])

        return menu
