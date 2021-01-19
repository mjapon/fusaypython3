# coding: utf-8
"""
Fecha de creacion 1/14/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTransaccImpDao(BaseDao):

    def get_config(self, tra_codigo):
        sql = """select tra_codigo, tra_impg, tra_imp0, tra_iserv, tra_ice, 
        tra_ivagasto, tra_signo from ttransaccimp where tra_codigo = {0} """.format(tra_codigo)

        tupla_desc = ('tra_codigo', 'tra_impg', 'tra_imp0', 'tra_iserv', 'tra_ice',
                      'tra_ivagasto', 'tra_signo')

        return self.first(sql, tupla_desc)
