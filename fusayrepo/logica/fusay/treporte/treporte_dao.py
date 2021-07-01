# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TReporteDao(BaseDao):

    def listar(self):
        sql = """
        select rep_id, rep_nombre, rep_detalle, rep_params, rep_cat from treporte
        order by rep_nombre asc
        """

        tupla_desc = ('rep_id', 'rep_nombre', 'rep_detalle', 'rep_params', 'rep_cat')

        return self.all(sql, tupla_desc)
