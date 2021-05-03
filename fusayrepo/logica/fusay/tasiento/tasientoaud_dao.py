# coding: utf-8
"""
Fecha de creacion 3/31/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsientoAud
from fusayrepo.utils import ctes

log = logging.getLogger(__name__)


class TAsientoAudDao(BaseDao):

    def craer(self, trn_codigo, aud_accion, aud_user, aud_obs):
        tasientoaud = TAsientoAud()
        tasientoaud.trn_codigo = trn_codigo
        tasientoaud.aud_accion = aud_accion
        tasientoaud.aud_fecha = datetime.now()
        tasientoaud.aud_user = aud_user
        tasientoaud.aud_obs = aud_obs
        self.dbsession.add(tasientoaud)

    def save_anula_transacc(self, tasiento, user_anula, obs_anula=''):
        tasiento.trn_valido = 1
        self.dbsession.add(tasiento)
        tasientoaud = TAsientoAud()
        tasientoaud.trn_codigo = tasiento.trn_codigo
        tasientoaud.aud_accion = ctes.AUD_ASIENTO_ANULAR
        tasientoaud.aud_obs = obs_anula
        tasientoaud.aud_user = user_anula
        self.dbsession.add(tasientoaud)
