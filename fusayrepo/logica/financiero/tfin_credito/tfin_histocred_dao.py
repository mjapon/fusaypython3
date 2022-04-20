# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_model import TFinCredito, TFinHistoCred

log = logging.getLogger(__name__)


class TFinHistoCredDao(BaseDao):

    def crear(self, cre_id, user_crea, previus_state, new_state, obs):
        histocred = TFinHistoCred()
        histocred.cre_id = cre_id
        histocred.hc_estado = new_state
        histocred.hc_estadoprevio = previus_state
        histocred.hc_usercrea = user_crea
        histocred.hc_fechacrea = datetime.datetime.now()
        histocred.hc_obs = obs

        self.dbsession.add(histocred)
