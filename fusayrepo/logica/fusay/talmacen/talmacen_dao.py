# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TAlmacenDao(BaseDao):

    def get_alm_numest(self, alm_codigo):
        sql = "select alm_numest from talmacen where alm_codigo={0}".format(alm_codigo)
        return self.first_col(sql, 'alm_numest')

    def get_nombre_comercial(self):
        sql = "select alm_nomcomercial from talmacen where alm_matriz = 1"
        return self.first_col(sql, 'alm_nomcomercial')

    def get_alm_tipoamb(self):
        sql = """
        select alm_tipoamb from talmacen where alm_matriz = 1
        """
        return self.first_col(sql, 'alm_tipoamb')
