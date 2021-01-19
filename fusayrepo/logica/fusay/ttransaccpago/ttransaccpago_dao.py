# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTransaccPagoDao(BaseDao):

    def get_formas_pago(self, tra_codigo):
        sql = """        
        select a.ttp_codigo, a.tra_codigo, a.cta_codigo, b.ic_alias as ic_nombre, a.ttp_signo as dt_debito, 
        0.0 as dt_valor, 1 as dt_codsec, a.ttp_coddocs, a.ttp_tipcomprob, b.ic_clasecc
        from ttransaccpago a join titemconfig b on a.cta_codigo = b.ic_id  where a.tra_codigo = {0} order by a.ttp_orden
        """.format(tra_codigo)
        tupla_desc = (
            'ttp_codigo', 'tra_codigo', 'cta_codigo', 'ic_nombre', 'dt_debito', 'dt_valor', 'dt_codsec',
            'ttp_coddocs', 'ttp_tipcomprob', 'ic_clasecc')
        return self.all(sql, tupla_desc)
