# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TtpdvDao(BaseDao):

    def get_tdv_numero(self, tdv_codigo):
        sql = "select tdv_numero from ttpdv where tdv_codigo={0}".format(tdv_codigo)
        return self.first_col(sql, 'tdv_numero')

    def get_alm_codigo_from_tdv_codigo(self, tdv_codigo):
        sql = "select alm_codigo from ttpdv where tdv_codigo = {0}".format(tdv_codigo)
        return self.first_col(sql, 'alm_codigo')
