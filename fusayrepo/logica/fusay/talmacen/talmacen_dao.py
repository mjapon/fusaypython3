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

    def get_direccion_matriz(self):
        sql = "select alm_codigo, alm_ruc, alm_numest, alm_direcc, alm_matriz, alm_tipoamb, alm_nomcomercial " \
              "from talmacen where alm_matriz = 1"
        tupla_desc = (
            'alm_codigo', 'alm_ruc', 'alm_numest', 'alm_direcc', 'alm_matriz', 'alm_tipoamb', 'alm_nomcomercial')

        self.first(sql, tupla_desc)

    def get_alm_tipoamb(self):
        sql = """
        select alm_tipoamb from talmacen where alm_matriz = 1
        """
        return self.first_col(sql, 'alm_tipoamb')
