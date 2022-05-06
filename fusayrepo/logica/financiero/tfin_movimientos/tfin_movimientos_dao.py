# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_model import TFinMovimientos
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TFinMovimientosDao(BaseDao):

    def get_form(self, cue_id):
        form = {
            'cue_id': cue_id,
            'mov_numero_comprob': '',
            'mov_abreviado': '',
            'mov_deb_cred': 1,
            'mov_total_transa': 0.0,
            'mov_num_linea': 0,
            'mov_tipotransa': 0,
            'mov_obs': ''
        }

        sqltransa = """
        select tipt_id, tipt_nombre, tipt_cod from tfin_tipostran order by tipt_nombre 
        """
        tupla_desc = ('tipt_id', 'tipt_nombre', 'tipt_cod')

        transacciones = self.all(sqltransa, tupla_desc)

    def crear(self, form, user_crea):
        tfin_mov = TFinMovimientos()

        tfin_mov.cue_id = form['cue_id']
        tfin_mov.mov_fecha_sistema = datetime.datetime.now()
        tfin_mov.mov_numero_comprob = form['mov_numero_comprob']
        tfin_mov.mov_abreviado = form['mov_abreviado']
        tfin_mov.mov_deb_cred = form['mov_deb_cred']
        tfin_mov.mov_total_transa = form['mov_total_transa']
        tfin_mov.mov_num_linea = form['mov_num_linea']
        tfin_mov.mov_tipotransa = form['mov_tipotransa']
        tfin_mov.mov_obs = cadenas.strip(form['mov_obs'])
        tfin_mov.user_crea = user_crea

        self.dbsession.add(tfin_mov)

    def mov_apertura(self, user_crea):
        pass



