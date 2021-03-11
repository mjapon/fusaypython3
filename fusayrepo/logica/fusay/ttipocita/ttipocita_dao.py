# coding: utf-8
"""
Fecha de creacion 3/10/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTipoCitaDao(BaseDao):

    def get_datos_tipo(self, tipc_id):
        sql = """
        select tipc_id, tipc_calini, tipc_calfin, tipc_nombre from ttipocita where tipc_id = {0}
        """.format(tipc_id)
        tupla_desc = ('tipc_id', 'tipc_calini', 'tipc_calfin', 'tipc_nombre')

        return self.first(sql, tupla_desc)
