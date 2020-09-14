# coding: utf-8
"""
Fecha de creacion 3/25/19
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TEmpresaDao(BaseDao):

    def get(self):
        sql = """select emp_id, emp_ruc, emp_razonsocial, emp_nombrecomercial, 
        emp_nroautorizacion, emp_fechaautorizacion from tempresa"""

        return self.first(sql=sql, tupla_desc=('emp_id', 'emp_ruc',
                                               'emp_razonsocial', 'emp_nombrecomercial',
                                               'emp_nroautorizacion', 'emp_fechaautorizacion'))

    def buscar_por_codigo(self, emp_codigo):

        sql = """select emp_id,          
                emp_ruc,
                emp_razonsocial,
                emp_nombrecomercial,
                emp_nroautorizacion,
                emp_fechaautorizacion,
                emp_esquema,          
                emp_codigo,           
                emp_menu from public.tempresa where emp_codigo = '{0}'""".format(emp_codigo)
        tupla_desc = ('emp_id',
                      'emp_ruc',
                      'emp_razonsocial',
                      'emp_nombrecomercial',
                      'emp_nroautorizacion',
                      'emp_fechaautorizacion',
                      'emp_esquema',
                      'emp_codigo',
                      'emp_menu')
        return self.first(sql, tupla_desc)
