# coding: utf-8
"""
Fecha de creacion 1/26/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TPersonCitaDao(BaseDao):

    def listar(self):
        sql = """
        select a.pc_id, a.per_id, b.per_ciruc, b.per_nombres||' '||b.per_apellidos as referente from
        tpersoncita a join tpersona b on a.per_id = b.per_id order by a.pc_id
        """
        tupla_desc = ('pc_id', 'per_id', 'per_ciruc', 'referente')
        return self.all(sql, tupla_desc)
