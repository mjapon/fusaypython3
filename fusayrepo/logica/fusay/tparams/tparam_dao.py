# coding: utf-8
"""
Fecha de creacion 3/27/19
@autor: mjapon
"""

import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tparams.tparam_model import TParams
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TParamsDao(BaseDao):

    def get_param_value(self, abreviacion):
        sql = "select tprm_val as val from tparams where tprm_abrev = '{0}'".format(abreviacion)
        val = self.first_col(sql, 'val')
        return val

    def update_param_value(self, abr, newvalue):
        tparam = self.dbsession.query(TParams.tprm_abrev == abr).first()
        if tparam is not None:
            tparam.tprm_val = cadenas.strip(newvalue)

    def update_sequence_billetera(self):
        abr_sequence = 'billSeqCode'
        self.aux_update_sequence(abr_sequence)

    def aux_update_sequence(self, seqname):
        tparam = self.dbsession.query(TParams).filter(TParams.tprm_abrev == seqname).first()
        if tparam is not None:
            current_val = int(tparam.tprm_val)
            newvalue = current_val + 1
            tparam.tprm_val = str(newvalue)

    def update_sequence_codbar(self):
        abr_sequence = 'artsSeqCodBar'
        self.aux_update_sequence(abr_sequence)
        """
        tparam = self.dbsession.query(TParams).filter(TParams.tprm_abrev == abr_sequence).first()
        if tparam is not None:
            current_val = int(tparam.tprm_val)
            newvalue = current_val + 1
            tparam.tprm_val = str(newvalue)
        """

    def get_next_sequence_billmov(self):
        next_sequence = self.get_param_value('billMovSeq')
        return int(next_sequence)

    def update_sequence_billmov(self):
        abr_sequence = 'billMovSeq'
        self.aux_update_sequence(abr_sequence)

    def get_next_sequence_bill(self):
        next_sequence = self.get_param_value('billSeqCode')
        return int(next_sequence)

    def get_next_sequence_codbar(self):
        next_sequence = self.get_param_value('artsSeqCodBar')
        return int(next_sequence)

    def get_ruta_savejobs(self):
        val = self.get_param_value('pathSaveJobs')
        if val is None:
            raise ErrorValidacionExc(
                u'El parametro pathSaveJobs no está registrado en la base de datos, favor verificar')
        return val

    def aplica_dental(self):
        prmvalue = self.get_param_value('ARTS_DENTAL')
        appldent = False
        if prmvalue is not None:
            appldent = prmvalue == '1'

        return appldent
