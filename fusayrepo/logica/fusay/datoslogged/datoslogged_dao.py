# coding: utf-8
"""
Fecha de creacion 4/4/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_dao import TFuserRolDao
from fusayrepo.logica.tempresa.empresa_dao import TEmpresaDao
from fusayrepo.utils import fechas, ctes

log = logging.getLogger(__name__)


class DataLoggedDao(BaseDao):

    def check_permiso(self, user_id, permiso):
        fuserroldao = TFuserRolDao(self.dbsession)
        return fuserroldao.user_has_permiso(user_id=user_id, prm_abreviacion=permiso)

    def get_datos_logged(self, user_id, emp_codigo):
        fechaactual = fechas.get_fecha_letras_largo(fecha=datetime.now())

        fuserroldao = TFuserRolDao(self.dbsession)
        permisos = fuserroldao.listar_permisos(user_id)

        allaccesosdirmap = {
            'IG_LISTAR': {
                'label': 'Ingresos y Gastos',
                'title': 'Adminsitrar ingresos y gastos',
                'icon': 'fas fa-retweet',
                'route': 'vtickets',
                'css': 'btn-outline-secondary'
            },
            # 'US_LISTAR': {
            #     'label': 'Usuarios',
            #     'title': 'Adminsitrar de usuarios del sistema',
            #     'icon': 'fas fa-users',
            #     'route': 'usuarios',
            #     'css': 'btn-outline-secondary'
            # },
            'VN_LISTAR': {
                'label': 'Ventas',
                'title': 'Listado de ventas',
                'icon': 'fas fa-store-alt',
                'route': 'trndocs/1',
                'css': 'btn-outline-secondary'
            },
            'PRODS_LISTAR': {
                'label': 'Inventarios',
                'title': 'Administración de productos y servicios',
                'icon': 'fas fa-cubes',
                'route': 'mercaderia',
                'css': 'btn-outline-secondary'
            },
            'TK_LISTAR': {
                'label': 'Tickets',
                'title': 'Ventas de tickets',
                'icon': 'fas fa-ticket-alt',
                'route': 'ticket/form',
                'css': 'btn-outline-secondary'
            },
            'AGN_LISTAR': {
                'label': 'Agenda',
                'title': 'Administrar su agenda',
                'icon': 'fas fa-calendar-check',
                'route': 'agenda/1',
                'css': 'btn-outline-secondary'
            },
            'CM_LISTAR': {
                'label': 'Compras',
                'title': 'Listado de compras',
                'icon': 'fas fa-shopping-cart',
                'route': 'trndocs/2',
                'css': 'btn-outline-secondary'
            },
            'HIST_LISTAR': {
                'label': 'Atención Médica',
                'title': 'Registrar atención médica',
                'icon': 'fas fa-stethoscope',
                'route': 'historiaclinica/1',
                'css': 'btn-outline-secondary'
            },
            'HISTO_LISTAR': {
                'label': 'Atención Odontológica',
                'title': 'Registrar atención odontológica',
                'icon': 'fas fa-tooth',
                'route': 'odonto',
                'css': 'btn-outline-secondary'
            },
            'REF_LISTAR': {
                'label': 'Referentes',
                'title': 'Administración de referentes',
                'icon': 'fas fa-address-book',
                'route': 'referentes',
                'css': 'btn-outline-secondary'
            }
        }

        accesosdir = []

        menu = fuserroldao.build_menu(permisos)
        tempresadao = TEmpresaDao(self.dbsession)
        datosemp = tempresadao.get_datos_emp_public(emp_codigo=emp_codigo)

        version = ctes.VERSION_APP

        for permiso in permisos:
            permabr = permiso['prm_abreviacion']
            if permabr in allaccesosdirmap.keys():
                if allaccesosdirmap[permabr] not in accesosdir:
                    accesosdir.append(allaccesosdirmap[permabr])

        return {
            'fecha': fechaactual,
            'accesosdir': accesosdir,
            'menu': menu,
            'datosemp': datosemp,
            'vapp': version
        }
