# coding: utf-8
"""
Fecha de creacion 5/11/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class ComunidadAguaDao(BaseDao):

    def listar(self):
        sql = """
        select cmn_id, cmn_nombre from public.tcomunidad
        """

        tupla_desc = ('cmn_id', 'cmn_nombre')
        return self.all(sql, tupla_desc)
