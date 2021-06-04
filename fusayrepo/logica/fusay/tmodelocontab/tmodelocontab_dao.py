# coding: utf-8
"""
Fecha de creacion 3/12/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TModelocontabDao(BaseDao):

    def listar(self):
        sql = """        
        select mc_id, mc_nombre, mc_estado from tmodelocontab
        where mc_estado = 1 order by mc_nombre 
        """
        tupla_desc = ('mc_id', 'mc_nombre', 'mc_estado')
        return self.all(sql, tupla_desc)

    def get_datos_modelocontable(self, mc_id, tra_codigo):
        sql = """
        select cta_codigo, mcd_signo from tmodelocontabdet where tra_codigo = {0} and mc_id = {1}
        """.format(tra_codigo, mc_id)

        tupla_desc = ('cta_codigo', 'mcd_signo')
        return self.first(sql, tupla_desc)

    def get_itemconfig_with_mc(self, ic_id, tra_codigo):
        sql = """
        select mcd.cta_codigo, mcd.mcd_signo, mcd.mc_id from
        tmodelocontabdet mcd
        join titemconfig_datosprod icdp on icdp.ic_id = {ic_id}
        where mcd.tra_codigo = {tra_cod} and mcd.mc_id = icdp.icdp_modcontab          
        """.format(ic_id=ic_id, tra_cod=tra_codigo)

        tupla_desc = ('cta_codigo', 'mcd_signo', 'mc_id')
        return self.first(sql, tupla_desc)