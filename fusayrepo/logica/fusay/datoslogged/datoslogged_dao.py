# coding: utf-8
"""
Fecha de creacion 4/4/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_dao import TFuserRolDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.tempresa.empresa_dao import TEmpresaDao
from fusayrepo.utils import fechas, ctes

log = logging.getLogger(__name__)


class DataLoggedDao(BaseDao):

    def check_permiso(self, user_id, permiso):
        fuserroldao = TFuserRolDao(self.dbsession)
        return fuserroldao.user_has_permiso(user_id=user_id, prm_abreviacion=permiso)

    def get_datos_logged(self, user_id, emp_esquema, sec_id):
        fechaactual = fechas.get_fecha_letras_largo(fecha=datetime.now())

        fuserroldao = TFuserRolDao(self.dbsession)
        permisos = fuserroldao.listar_permisos(user_id)
        sec_calendar = TSeccionDao(self.dbsession).get_sec_calendar(sec_id)

        allaccesosdirmap = {
            'IG_LISTAR': [{
                'label': 'Ingresos y Gastos',
                'title': 'Adminsitrar ingresos y gastos',
                'icon': 'fa fa-comments-dollar',
                'route': 'vtickets',
                'css': 'btn-outline-secondary'
            }],
            'VN_LISTAR': [{
                'label': 'Ventas',
                'title': 'Listado de ventas',
                'icon': 'fas fa-store-alt',
                'route': 'trndocs/1',
                'css': 'btn-outline-secondary'
            }],
            'CXC_LISTAR': [{
                'label': 'Cuentas por cobrar',
                'title': 'Listado de cuentas por cobrar',
                'icon': 'fas fa-hand-holding-usd',
                'route': 'cuentasxcp/1',
                'css': 'btn-outline-secondary'
            }],
            'PRODS_LISTAR': [{
                'label': 'Inventarios',
                'title': 'Administración de productos y servicios',
                'icon': 'fas fa-cubes',
                'route': 'mercaderia',
                'css': 'btn-outline-secondary'
            }],
            'TK_LISTAR': [{
                'label': 'Tickets',
                'title': 'Ventas de tickets',
                'icon': 'fas fa-ticket-alt',
                'route': 'ticket/form',
                'css': 'btn-outline-secondary'
            }],
            'AGN_LISTAR': [{
                'label': 'Agenda',
                'title': 'Administrar su agenda',
                'icon': 'fas fa-calendar-check',
                'route': 'agenda/1',
                'css': 'btn-outline-secondary'
            }],
            'CM_LISTAR': [{
                'label': 'Compras',
                'title': 'Listado de compras',
                'icon': 'fas fa-shopping-cart',
                'route': 'trndocs/2',
                'css': 'btn-outline-secondary'}],
            'CXP_LISTAR': [{
                'label': 'Cuentas por pagar',
                'title': 'Listado de cuentas por pagar',
                'icon': 'fas fa-hand-holding-usd fa-flip-horizontal',
                'route': 'cuentasxcp/2',
                'css': 'btn-outline-secondary'
            }],
            'HIST_LISTAR': [{
                'label': 'Atención Médica',
                'title': 'Registrar atención médica',
                'icon': 'fas fa-stethoscope',
                'route': 'historiaclinica/1',
                'css': 'btn-outline-secondary'
            }],
            'HISTO_LISTAR': [{
                'label': 'Atención Odontológica',
                'title': 'Registrar atención odontológica',
                'icon': 'fas fa-tooth',
                'route': 'odonto',
                'css': 'btn-outline-secondary'
            }],
            'REF_LISTAR': [{
                'label': 'Referentes',
                'title': 'Administración de referentes',
                'icon': 'fas fa-address-book',
                'route': 'referentes',
                'css': 'btn-outline-secondary'
            }],
            'AGP_ADM': [{
                'label': 'Cobro de agua',
                'title': 'Sistema de cobro de agua potable',
                'icon': 'fas fa-tint',
                'route': 'aguap/home',
                'css': 'btn-outline-secondary'
            }],
            'FIN_CRED_LIST': [
                {
                    'label': 'Caja de Créditos',
                    'title': 'Sistema para cajas de ahorro y crédito',
                    'icon': 'fas fa-piggy-bank',
                    'route': 'finan/home',
                    'css': 'btn-outline-secondary'
                }
            ],
            'FIN_CREA_CTA': [
                {
                    'label': 'Apertura Cuentas',
                    'title': 'Permite apertura una cuenta para un socio',
                    'icon': 'fas fa-piggy-bank',
                    'route': 'finan/aperturacta',
                    'css': 'btn-outline-secondary'
                }
            ],
            'FIN_MOVS_CTA': [
                {
                    'label': 'Movimientos Cuentas',
                    'title': 'Permite administrar movimientos de una cuenta',
                    'icon': 'fas fa-piggy-bank',
                    'route': 'finan/movscta',
                    'css': 'btn-outline-secondary'
                }
            ]
        }

        accesosdir = []

        menu = fuserroldao.build_menu(permisos)
        tempresadao = TEmpresaDao(self.dbsession)
        datosemp = tempresadao.get_info_by_schema(emp_esquema)

        version = ctes.VERSION_APP

        for permiso in permisos:
            permabr = permiso['prm_abreviacion']
            if permabr in allaccesosdirmap.keys():
                if allaccesosdirmap[permabr] not in accesosdir:
                    accesosdir.extend(allaccesosdirmap[permabr])

        accesosdir.sort(key=lambda x: x['label'])

        return {
            'fecha': fechaactual,
            'accesosdir': accesosdir,
            'menu': menu,
            'datosemp': datosemp,
            'vapp': version,
            'emp': datosemp['emp_id'],
            'sec_calendar': sec_calendar
        }
