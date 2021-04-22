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

    def get_alm_codigo_from_sec_codigo(self, sec_codigo):
        sql = "select alm_codigo from tseccion where sec_id = {0}".format(sec_codigo)
        return self.first_col(sql, 'alm_codigo')

    def listar_min(self, alm_codigo):
        sql = "select tdv_codigo, tdv_numero, tdv_nombre from ttpdv where alm_codigo = {0} order by tdv_numero".format(
            alm_codigo)

        tupla_desc = ('tdv_codigo', 'tdv_numero', 'tdv_nombre')
        return self.all(sql, tupla_desc)

    def listar_min_from_sec_codigo(self, sec_id):
        sql = """
        select alm_codigo from tseccion where sec_id = {0}
        """.format(sec_id)
        alm_codigo = self.first_col(sql, 'alm_codigo')
        return self.listar_min(alm_codigo=alm_codigo)

    def get_byid(self, tdv_codigo):
        sql = """select tdv_codigo, tdv_numero, tdv_descri, tdv_estado, 
        tdv_maxitem, alm_codigo from ttpdv where tdv_codigo = {0}
        """.format(tdv_codigo)
        tupla_desc = ('tdv_codigo', 'tdv_numero', 'tdv_descri', 'tdv_estado', 'tdv_maxitem', 'alm_codigo')
        return self.first(sql, tupla_desc)
