# coding: utf-8
"""
Fecha de creacion 1/13/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.utils import fechas

log = logging.getLogger(__name__)


class TImpuestoDao(BaseDao):

    def get_impuestos(self):
        sql = """
        select imp_id, imp_tipo, imp_valor from timpuestos where imp_hasta is null; 
        """
        tupla_desc = ('imp_id', 'imp_tipo', 'imp_valor')

        impuestos = self.all(sql, tupla_desc)
        res = {'iva': 0.0, 'impserv': 0.0}

        for impuesto in impuestos:
            imp_tipo = impuesto['imp_tipo']
            if imp_tipo == 1:
                res['iva'] = impuesto['imp_valor']
            elif imp_tipo == 2:
                res['impserv'] = impuesto['imp_valor']

        return res