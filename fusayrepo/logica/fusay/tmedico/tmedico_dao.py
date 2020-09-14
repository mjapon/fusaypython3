# coding: utf-8
"""
Fecha de creacion 9/11/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tmedico.tmedico_model import TMedico, TMedicoEspe

log = logging.getLogger(__name__)


class TMedicoDao(BaseDao):

    def crear_medico(self, per_id, especialidades):
        tmedico = TMedico()
        tmedico.per_id = per_id
        tmedico.med_fecreg = datetime.datetime.now()

        self.dbsession.add(tmedico)
        self.dbsession.flush()

        med_id = tmedico.med_id

        for especialidad in especialidades:
            tmedespe = TMedicoEspe()
            tmedespe.med_id = med_id
            tmedespe.esp_id = especialidad['lval_id']
            tmedespe.medesp_estado = 0
            self.dbsession.add(tmedespe)
