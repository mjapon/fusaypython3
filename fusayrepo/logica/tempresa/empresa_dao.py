# coding: utf-8
"""
Fecha de creacion 3/25/19
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc

log = logging.getLogger(__name__)


class TEmpresaDao(BaseDao):

    def get(self):
        sql = """select emp_id, emp_ruc, emp_razonsocial, emp_nombrecomercial, 
        emp_nroautorizacion, emp_fechaautorizacion from tempresa"""

        return self.first(sql=sql, tupla_desc=('emp_id', 'emp_ruc',
                                               'emp_razonsocial', 'emp_nombrecomercial',
                                               'emp_nroautorizacion', 'emp_fechaautorizacion'))

    def get_info_by_schema(self, emp_esquema):
        sql = """select emp_id,          
                        emp_ruc,
                        emp_razonsocial,
                        emp_nombrecomercial,
                        emp_nroautorizacion,
                        emp_fechaautorizacion,
                        emp_esquema,          
                        emp_codigo,           
                        emp_menu from public.tempresa where emp_esquema = '{0}'""".format(emp_esquema)
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

    def get_datos_emp_public(self, emp_codigo):
        sql = """
        select emp_ruc, emp_razonsocial, emp_nombrecomercial, 
        emp_nroautorizacion, emp_fechaautorizacion from public.tempresa where emp_codigo = '{0}' 
        """.format(emp_codigo)
        tupla_desc = ('emp_ruc', 'emp_razonsocial', 'emp_nombrecomercial',
                      'emp_nroautorizacion', 'emp_fechaautorizacion')
        return self.first(sql, tupla_desc)

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

    def crear(self, form, user_crea):
        raise ErrorValidacionExc('No implementado')

    def update(self, emp_codigo, form, user_edit):
        raise ErrorValidacionExc('No implementado')
