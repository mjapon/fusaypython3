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
        select imp_id, imp_tipo, imp_valor, round(imp_valor*100)||'%' as imp_name from timpuestos where imp_hasta is null order by imp_valor; 
        """
        tupla_desc = ('imp_id', 'imp_tipo', 'imp_valor', 'imp_name')

        impuestos = self.all(sql, tupla_desc)
        ivas = [imp for imp in impuestos if imp['imp_tipo'] == 1]
        res = {'iva': 0.0, 'impserv': 0.0, 'ivas': ivas}

        for impuesto in impuestos:
            imp_tipo = impuesto['imp_tipo']
            if imp_tipo == 1:
                res['iva'] = impuesto['imp_valor']
            elif imp_tipo == 2:
                res['impserv'] = impuesto['imp_valor']

        return res
