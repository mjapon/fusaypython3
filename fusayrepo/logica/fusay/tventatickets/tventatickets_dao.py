# coding: utf-8
"""
Fecha de creacion 9/14/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tventatickets.tventatickets_model import TVentaTickets
from fusayrepo.utils import cadenas, fechas

log = logging.getLogger(__name__)


class TVentaTicketsDao(BaseDao):

    def get_form(self):
        return {
            'vt_id': 0,
            'vt_monto': 0.0,
            'vt_tipo': 0,
            'vt_estado': 0,
            'vt_obs': '',
            'vt_clase': 1,
            'vt_fecha': fechas.get_str_fecha_actual()
        }

    def get_cuentas(self, tipo):
        sql = """
        select ic_id, ic_nombre from titemconfig
        where tipic_id = 4 and clsic_id = {tipo} order by ic_nombre asc;
        """.format(tipo=tipo)
        tupla_desc = ('ic_id', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def get_entity_byid(self, vt_id):
        return self.dbsession.query(TVentaTickets).filter(TVentaTickets.vt_id == vt_id).first()

    def get_tipos_cuentas(self):
        return [{
            'value': 1, 'label': 'Ingreso',
        },
            {
                'value': 2, 'label': 'Gasto',
            },
            {
                'value': 3, 'label': 'Patrimonio',
            }

        ]

    def agregar_todos_inlist(self, thelist):
        cuentares = [{'ic_id': 0, 'ic_nombre': 'Todos'}]
        for item in thelist:
            cuentares.append(item)

        return cuentares

    def crear(self, form):
        tventaTicket = TVentaTickets()
        monto = form['vt_monto']
        tipo = form['vt_tipo']
        estado = 0
        obs = form['vt_obs']
        clase = form['vt_clase']
        fecha = form['vt_fecha']
        fecha_parsed = fechas.parse_cadena(fecha)

        tventaTicket.vt_fechareg = datetime.now()
        tventaTicket.vt_monto = monto
        tventaTicket.vt_tipo = tipo
        tventaTicket.vt_estado = estado
        tventaTicket.vt_obs = cadenas.strip(obs)
        tventaTicket.vt_clase = clase
        tventaTicket.vt_fecha = fecha_parsed

        self.dbsession.add(tventaTicket)

    def cambiar_estado(self, vt_id, estado):
        tventaticket = self.get_entity_byid(vt_id)
        if tventaticket is not None:
            tventaticket.vt_estado = estado
            self.dbsession.add(tventaticket)

    def anular(self, vt_id):
        self.cambiar_estado(vt_id, estado=2)

    def confirmar(self, vt_id):
        self.cambiar_estado(vt_id, estado=1)

    def listar(self, tipo, cuenta):
        tgrid_dao = TGridDao(self.dbsession)
        andwhere = "";
        if cuenta is None or int(cuenta) == 0:
            andwhere = " and ic.clsic_id = {0}".format(tipo)
        else:
            andwhere = " and ic.clsic_id = {0} and vt_tipo={1} ".format(tipo, cuenta)

        data = tgrid_dao.run_grid(grid_nombre='ventatickets', andwhere=andwhere)

        return data
