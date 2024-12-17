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

    def user_has_permiso(self, user_id, prm_abreviacion):
        sql = """
        select count(*) as cuenta from tfuserrol fr
        join trol rol on fr.rl_id = rol.rl_id
        join tpermisorol perol on fr.rl_id = perol.rl_id
        join tpermiso per on perol.prm_id = per.prm_id and per.prm_abreviacion in ('{0}')
        where fr.us_id = {1} and rol.rl_estado = 0 and per.prm_estado = 0
        """.format(prm_abreviacion, user_id)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def listar_permisos(self, us_id):
        sql = """        
        select per.prm_id, per.prm_abreviacion, per.prm_nombre from tpermiso per
        where per.prm_id in (
           select permrol.prm_id from tfuserrol fr
           join trol rol on fr.rl_id = rol.rl_id
           join tpermisorol permrol on permrol.rl_id = rol.rl_id where fr.us_id = {0}) order by per.prm_nombre
        """.format(us_id)

        tupla_desc = ('prm_id', 'prm_abreviacion', 'prm_nombre')
        return self.all(sql, tupla_desc)

    def build_menu(self, permisos):

        paramsdao = TParamsDao(self.dbsession)
        hasplanesvalue = paramsdao.get_param_value('EMP_HASPLANES')
        hasplanes = False
        if hasplanesvalue is not None:
            hasplanes = cadenas.strip(hasplanesvalue) == '1'

        contabilidad_list = [
            {'label': 'Ingresos y Gastos', 'icon': 'fa-solid fa-bars-staggered', 'routerLink': ['/vtickets']},
            {'label': 'Libro Diario', 'icon': 'fa-solid fa-book', 'routerLink': ['/librodiario']},
            {'label': 'Libro Mayor', 'icon': 'fa-solid fa-book-open', 'routerLink': ['/libromayor']},
            {'label': 'Plan de cuentas', 'icon': 'fa-solid fa-list-ol', 'routerLink': ['/plancuentas']},
            {'label': 'Balance General', 'icon': 'fa-solid fa-chart-pie',
             'routerLink': ['/contabilidad/balancegeneral']},
            {'label': 'Estado de Resultados', 'icon': 'fa-solid fa-chart-line',
             'routerLink': ['/contabilidad/estadoresultados']},
            {'label': 'Cierre Periodo', 'icon': 'fa-solid fa-folder-closed',
             'routerLink': ['contabilidad/periodo/cierre']},
            {'label': 'Apertura Periodo', 'icon': 'fa-solid fa-folder-open',
             'routerLink': ['contabilidad/periodo/apertura']}
        ]

        tickets_list = [
            {'label': 'Listado', 'icon': 'fa-solid fa-rectangle-list', 'routerLink': ['/tickets']},
            {'label': 'Crear', 'icon': 'fa-solid fa-ticket-simple', 'routerLink': ['/ticket/form']}
        ]

        prods_list = [
            {'label': 'Listado', 'icon': 'fa-solid fa-rectangle-list', 'routerLink': ['/mercaderia']},
            {'label': 'Categorias', 'icon': 'fa-solid fa-tags', 'routerLink': ['/categorias']}
        ]

        if hasplanes:
            prods_list.append({'label': 'Planes', 'icon': '', 'routerLink': ['/planes']})

        users_list = [
            {'label': 'Usuarios', 'icon': 'fa-solid fa-users', 'routerLink': ['/usuarios']},
            {'label': 'Roles', 'icon': 'fa-solid fa-users-gear', 'routerLink': ['/roles']}
        ]

        ventas_list = [
            {'label': 'Listado', 'icon': 'fa-solid fa-rectangle-list',
             'routerLink': ['/trndocs/1']},
            {'label': 'Emitir Factura', 'icon': 'fa-solid fa-file-invoice-dollar',
             'routerLink': ['/trndocform/1/c']},
            {'label': 'Emitir Nota de venta', 'icon': 'fa-solid fa-file-invoice',
             'routerLink': ['/trndocform/2/c']},
            {'label': 'Notas de crédito', 'icon': 'fa-solid fa-rectangle-list',
             'routerLink': ['/trndocs/3']},
            {'label': 'Utilidades', 'icon': 'fa-solid fa-coins',
             'routerLink': ['/utilventas']},
            {'label': 'Cierre Caja', 'icon': 'fa-solid fa-cash-register',
             'routerLink': ['/cierrecaja']}
        ]

        compras_list = [
            {'label': 'Movimientos', 'icon': 'fa-solid fa-rectangle-list',
             'routerLink': ['/trndocs/2']},
            {'label': 'Registrar factura', 'icon': 'fa-solid fa-file-invoice',
             'routerLink': ['/trndocform/7/c']}
        ]

        caja_list = [
            {'label': 'Créditos', 'icon': 'fa-solid fa-credit-card',
             'routerLink': ['/finan/home']},
            {'label': 'Cuentas', 'icon': 'fa-solid fa-file-circle-plus',
             'routerLink': ['/finan/aperturacta']},
            {'label': 'Movimientos', 'icon': 'fa-solid fa-comments-dollar',
             'routerLink': ['/finan/movscta']}
        ]

        config_list = [
            {'label': 'Parámetros',
             'icon': 'fa-solid fa-cog',
             'routerLink': ['/parametros']}
        ]

        all_menu = {
            '*': {'label': 'Inicio', 'icon': 'fa-solid fa-house', 'routerLink': ['/lghome']},
            'TK_LISTAR': {'label': 'Tickets', 'icon': 'fa-solid fa-ticket',
                          'items': tickets_list},
            'IG_LISTAR': {'label': 'Contabilidad', 'icon': 'fa-solid fa-book', 'cicon': 'fas fa-calculator',
                          'items': contabilidad_list},
            'PRODS_LISTAR': {'label': 'Productos', 'icon': 'fa-solid fa-boxes-stacked', 'cicon': 'fas fa-store',
                             'items': prods_list},
            'HIST_LISTAR': {'label': 'Atención Médica', 'icon': 'fa-solid fa-user-doctor',
                            'routerLink': ['/historiaclinica/1']},
            'HISTO_LISTAR': {'label': 'Atención Odontológica', 'icon': 'fa-solid fa-tooth',
                             'routerLink': ['/odonto']},
            'US_LISTAR': {'label': 'Usuarios', 'icon': 'fa-solid fa-user-group',
                          'items': users_list},
            'VN_LISTAR': {'label': 'Ventas', 'icon': 'fa-solid fa-cart-shopping',
                          'items': ventas_list},
            'CM_LISTAR': {'label': 'Compras', 'icon': 'fa-solid fa-boxes-packing',
                          'items': compras_list},
            'REF_LISTAR': {'label': 'Referentes', 'icon': 'fa-solid fa-address-book', 'routerLink': ['/referentes']},
            'AGN_LISTAR': {'label': 'Agenda', 'icon': 'fa-solid fa-calendar-check', 'routerLink': ['/agenda/1']},
            'AGP_ADM': {'label': 'Cobro Agua', 'icon': 'fa-solid fa-faucet-drip', 'routerLink': ['/aguap/home']},
            'REP_ADM': {'label': 'Reportes', 'icon': 'fa-solid fa-chart-pie',
                        'routerLink': ['/reportes']},
            'FIN_CRED_LIST': {'label': 'Caja de Crédito', 'icon': 'fa-solid fa-piggy-bank',
                              'items': caja_list},
            'APP_CONFIG': {'label': 'Configuración', 'icon': 'fa-solid fa-cog', 'items': config_list}
        }

        menu = []
        # menu.append(all_menu['*'])
        permisos_set = set()
        for perm in permisos:
            abrperm = perm['prm_abreviacion']
            permisos_set.add(abrperm)

        if 'CXC_LISTAR' in permisos_set:
            ventas_list.append({'label': 'Cuentas por cobrar', 'icon': 'fa-solid fa-person-arrow-down-to-line',
                                'routerLink': ['/cuentasxcp/1']})
        if 'CXP_LISTAR' in permisos_set:
            compras_list.append({'label': 'Cuentas por pagar', 'icon': 'fa-solid fa-person-arrow-up-from-line',
                                 'routerLink': ['/cuentasxcp/2']})
        if 'PROF_ADMIN' in permisos_set:
            ventas_list.append({'label': 'Proformas', 'icon': 'fa-solid fa-file-invoice',
                                'routerLink': ['/trndocs/4']})

        for key in all_menu.keys():
            if key in permisos_set:
                menu.append(all_menu[key])

        # menu_sorted = sorted(menu, key=lambda x: x['label'])

        return menu
