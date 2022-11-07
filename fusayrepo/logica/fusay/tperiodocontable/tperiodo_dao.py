# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TPeriodoContableDao(BaseDao):

    def get_datos_periodo_contable(self):
        sql = "select pc_id, pc_desde, pc_hasta, pc_fechacrea from tperiodocontable where pc_activo = true"
        tupla_desc = ('pc_id', 'pc_desde', 'pc_hasta', 'pc_fechacrea')
        return self.first(sql, tupla_desc)
