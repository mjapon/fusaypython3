# coding: utf-8
"""
Fecha de creacion 11/16/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTransaccDao(BaseDao):

    def get_formas_pago(self, tra_codigo):
        sql = """        
        select a.ttp_codigo, a.tra_codigo, a.cta_codigo, b.ic_nombre, a.ttp_signo as dt_debito, 
        0.0 as dt_valor, 1 as dt_codsec, a.ttp_coddocs, a.ttp_tipcomprob, b.ic_clasecc
        from ttransaccpago a join titemconfig b on a.cta_codigo = b.ic_id  where a.tra_codigo = {0} order by a.ttp_orden
        """.format(tra_codigo)
        tupla_desc = (
            'ttp_codigo', 'tra_codigo', 'cta_codigo', 'ic_nombre', 'dt_debito', 'dt_valor', 'dt_codsec',
            'ttp_coddocs', 'ttp_tipcomprob', 'ic_clasecc')
        return self.all(sql, tupla_desc)

    def get_ttransacc(self, tra_codigo):
        sql = """
        select tra_codigo,
        tra_nombre,
        tra_obs, 
        tra_xmlsav,
        tra_tipart,
        tra_edcomp,
        tra_tipdoc,
        tra_tipoprecio,
        tra_codrep,
        tra_dupite,
        tra_preiva,
        tra_vietot,
        tra_contab,
        tra_inv,
        tra_seccion from ttransacc where tra_codigo = {0}
        """.format(tra_codigo)

        tupla_desc = ('tra_codigo',
                      'tra_nombre',
                      'tra_obs',
                      'tra_xmlsav',
                      'tra_tipart',
                      'tra_edcomp',
                      'tra_tipdoc',
                      'tra_tipoprecio',
                      'tra_codrep',
                      'tra_dupite',
                      'tra_preiva',
                      'tra_vietot',
                      'tra_contab',
                      'tra_inv',
                      'tra_seccion')

        return self.first(sql, tupla_desc)
