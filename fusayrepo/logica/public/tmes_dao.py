# coding: utf-8
"""
Fecha de creacion 5/17/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.utils import fechas

log = logging.getLogger(__name__)


class PublicTMesDao(BaseDao):

    def listar(self):
        sql = """
        select mes_id, mes_nombre, mes_corto from public.tmes order by mes_id
        """
        tupla_desc = ('mes_id', 'mes_nombre', 'mes_corto')
        return self.all(sql, tupla_desc)

    def get_current_previus(self):
        mes = fechas.get_mes_actual()
        mes_ant = mes - 1
        if mes_ant <= 0:
            mes_ant = 12

        sql = """
        select mes_id, mes_nombre from public.tmes where mes_id in ({0},{1}) 
        """.format(mes_ant, mes)

        tupla_desc = ('mes_id', 'mes_nombre')
        return self.all(sql, tupla_desc)

    @staticmethod
    def get_current_previus_year():
        anio = fechas.get_anio_actual()
        anio_ant = anio - 1
        return [{'label': anio, 'value': anio},
                {'label': anio_ant, 'value': anio_ant}, ]
