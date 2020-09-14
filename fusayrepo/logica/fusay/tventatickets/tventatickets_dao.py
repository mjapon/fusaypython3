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
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TVentaTicketsDao(BaseDao):

    def get_form(self):
        return {
            'vt_id': 0,
            'vt_monto': 0.0,
            'vt_tipo': 0,
            'vt_estado': 0,
            'vt_obs': ''
        }

    def get_tipos_rubro(self):
        sql = """
        select ic_id, ic_nombre from titemconfig
        where tipic_id = 4 order by ic_nombre asc;
        """
        tupla_desc = ('ic_id', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def get_entity_byid(self, vt_id):
        return self.dbsession.query(TVentaTickets).filter(TVentaTickets.vt_id == vt_id).first()

    def crear(self, form):
        tventaTicket = TVentaTickets()
        monto = form['vt_monto']
        tipo = form['vt_tipo']
        estado = 0
        obs = form['vt_obs']

        tventaTicket.vt_fechareg = datetime.now()
        tventaTicket.vt_monto = monto
        tventaTicket.vt_tipo = tipo
        tventaTicket.vt_estado = estado
        tventaTicket.vt_obs = cadenas.strip(obs)

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

    def listar(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='ventatickets')
        return data
