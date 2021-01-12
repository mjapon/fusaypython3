# coding: utf-8
"""
Fecha de creacion 1/8/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_model import TAsicredito
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao

log = logging.getLogger(__name__)


class TAsicreditoDao(BaseDao):

    def crear(self, form, alm_codigo, tdv_codigo, sec_codigo):
        tasicredito = TAsicredito()

        tra_codigo = 8
        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
        resestabsec = ttransacc_pdv.get_estabptoemi_secuencia(alm_codigo=alm_codigo, tra_codigo=tra_codigo,
                                                              tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)
        secuencia = resestabsec['secuencia']
        len_compro = 15
        cre_compro = "{0}".format(str(secuencia)).zfill(len_compro)

        tasicredito.dt_codigo = form['dt_codigo']
        tasicredito.cre_fecini = form['cre_fecini']
        tasicredito.cre_fecven = form['cre_fecven']
        tasicredito.cre_intere = form['cre_intere']
        tasicredito.cre_intmor = form['cre_intmor']
        tasicredito.cre_compro = form['cre_compro']
        tasicredito.cre_codban = form['cre_codban']
        tasicredito.cre_saldopen = form['cre_saldopen']

        self.dbsession.add(tasicredito)
