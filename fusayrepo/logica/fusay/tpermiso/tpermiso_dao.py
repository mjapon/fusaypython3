# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TPermisoDao(BaseDao):

    def listar(self):
        sql = """select prm_id, prm_nombre, prm_abreviacion, prm_detalle 
        from tpermiso where prm_estado = 0 order by prm_nombre"""

        tupla_desc = ('prm_id', 'prm_nombre', 'prm_abreviacion', 'prm_detalle')

        return self.all(sql, tupla_desc)
