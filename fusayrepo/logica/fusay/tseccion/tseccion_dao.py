# coding: utf-8
"""
Fecha de creacion 3/7/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TSeccionDao(BaseDao):

    def listar(self):
        sql = """select a.sec_id, a.sec_nombre, b.alm_codigo, b.alm_nomcomercial, b.alm_razsoc
        from tseccion a join talmacen b on a.alm_codigo = b.alm_codigo  where  sec_estado = 1 order by sec_id"""
        tupla_desc = ('sec_id', 'sec_nombre', 'alm_codigo', 'alm_nomcomercial', 'alm_razsoc')
        return self.all(sql, tupla_desc)

    def get_byid(self, sec_id):
        sql = "select sec_id, sec_nombre, alm_codigo from tseccion where  sec_estado = 1 and sec_id ={0} order by sec_id".format(
            sec_id)
        tupla_desc = ('sec_id', 'sec_nombre')
        return self.first(sql, tupla_desc)

    def get_alm_codigo_from_sec_codigo(self, sec_codigo):
        sql = "select alm_codigo from tseccion where sec_id = {0}".format(sec_codigo)
        alm_codigo = self.first_col(sql, 'alm_codigo')
        return alm_codigo

    def get_sec_tipoamb(self, sec_id):
        sql = "select sec_tipoamb from tseccion where sec_id = {0}".format(sec_id)
        return self.first_col(sql, 'sec_tipoamb')

    def get_sec_calendar(self, sec_id):
        sql = "select sec_calendar from tseccion where sec_id = {0}".format(sec_id)
        return self.first_col(sql, 'sec_calendar')
