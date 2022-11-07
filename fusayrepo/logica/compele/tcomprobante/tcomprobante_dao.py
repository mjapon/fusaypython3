# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.compele.tcomprobante.tcomprobante_model import TComprobante
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.utils import fechas

log = logging.getLogger(__name__)


class TComprobanteDao(BaseDao):

    def existe_clave_acceso(self, claveacceso):
        sql = """
        select count(*) as cuenta from comprobantes.tcomprobante where cmp_claveaccesso = '{0}'
        """.format(claveacceso)

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form):
        if not self.existe_clave_acceso(claveacceso=form['cmp_claveaccesso']):
            tcomprobante = TComprobante()
            tcomprobante.cmp_tipo = form['cmp_tipo']
            tcomprobante.cmp_numero = form['cmp_numero']
            tcomprobante.cmp_trncod = form['cmp_trncod']
            tcomprobante.cmp_claveaccesso = form['cmp_claveaccesso']
            tcomprobante.cnt_id = form['cnt_id']
            tcomprobante.emp_codigo = form['emp_codigo']
            tcomprobante.cmp_fecha = fechas.parse_cadena(form['cmp_fecha'])
            tcomprobante.cmp_total = form['cmp_total']
            tcomprobante.cmp_fecsys = datetime.datetime.now()
            tcomprobante.cmp_estado = form['cmp_estado']
            tcomprobante.cmp_ambiente = form['cmp_ambiente']

            self.dbsession.add(tcomprobante)

    def listar(self, cnt_id, tipo):
        sql = """
        select 
            c.cmp_numero,
            c.cmp_id,
            c.cmp_claveaccesso,
            c.cmp_fecha ,
            c.cmp_total,
            emp.emp_razons
            from comprobantes.tcomprobante c
            join comprobantes.tempresa emp on c.emp_codigo  = emp. emp_codigo 
            where c.cnt_id = {0} and c.cmp_tipo= {1} order by cmp_fecha ;   
        """.format(cnt_id, tipo)

        tupla_desc = ('cmp_numero',
                      'cmp_id',
                      'cmp_claveaccesso',
                      'cmp_fecha',
                      'cmp_total',
                      'emp_razons')

        return self.all(sql, tupla_desc)

    def listar_grid(self, cnt_id, tipo):
        data = self.listar(cnt_id, tipo)
        cols = [
            {"label": "Comercio", "field": "emp_razons", "width": "30%"},
            {"label": "Fecha", "field": "cmp_fecha", "width": "20%"},
            {"label": "Numero", "field": "cmp_numero", "width": "20%"},
            {"label": "Total", "field": "cmp_total", "width": "10%"}
        ]
        return {'data': data, 'cols': cols}
