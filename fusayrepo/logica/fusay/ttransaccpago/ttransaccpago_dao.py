# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.utils import ctes

log = logging.getLogger(__name__)


class TTransaccPagoDao(BaseDao):

    def get_pagos_efectivo(self, sec_id):
        sql = """
                select b.ic_id, b.ic_code, b.ic_nombre from titemconfig b
                join titemconfig_sec c on b.ic_id = c.ic_id and c.sec_id = {0} 
                where b.ic_clasecc = '{1}' and b.ic_estado = 1
                """.format(sec_id, ctes.CLASECC_EFECTIVO)
        tupla_desc = ('ic_id', 'ic_code', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def get_formas_pago(self, tra_codigo, sec_id):
        sql = """        
        select a.ttp_codigo, a.tra_codigo, a.cta_codigo, b.ic_alias as ic_nombre, a.ttp_signo as dt_debito, 
        0.0 as dt_valor, 1 as dt_codsec, a.ttp_coddocs, a.ttp_tipcomprob, b.ic_clasecc
        from ttransaccpago a join titemconfig b on a.cta_codigo = b.ic_id  
        where a.tra_codigo = {0} and a.sec_codigo = {1}             
        order by a.ttp_orden
        """.format(tra_codigo, sec_id)
        tupla_desc = (
            'ttp_codigo', 'tra_codigo', 'cta_codigo', 'ic_nombre', 'dt_debito', 'dt_valor', 'dt_codsec',
            'ttp_coddocs', 'ttp_tipcomprob', 'ic_clasecc')
        return self.all(sql, tupla_desc)

    def get_datos_cuenta_credito(self, tra_codigo, sec_id):
        sql = "select tra_tipdoc from ttransacc where tra_codigo = {0}".format(tra_codigo)
        tra_tipdoc = self.first_col(sql, 'tra_tipdoc')
        if tra_tipdoc is not None:
            if int(tra_tipdoc) == 1:
                clasecuentaxcp = "XC"
            elif int(tra_tipdoc) == 2:
                clasecuentaxcp = "XP"
            else:
                raise ErrorValidacionExc(
                    'No puedo determinar la clase del tipo de cuenta por cobrar o pagar para esta transacción')
        else:
            raise ErrorValidacionExc(
                'La transacción {tracod} no tiene registrado tra_tipdoc, favor verificar'.format(tracod=tra_codigo))

        sql = """        
               select a.cta_codigo, a.ttp_signo as dt_debito, b.ic_clasecc
               from ttransaccpago a join titemconfig b on a.cta_codigo = b.ic_id and b.ic_clasecc = '{0}'  
               where a.tra_codigo = {1} and a.sec_codigo = {2}         
               order by a.ttp_orden
               """.format(clasecuentaxcp, tra_codigo, sec_id)
        tupla_desc = (
            'cta_codigo', 'dt_debito', 'ic_clasecc')
        items = self.all(sql, tupla_desc)

        if items is None or len(items) == 0:
            raise ErrorValidacionExc(
                'La transacción {0} no tiene una cuenta contable asociada tipo xp o xc en sus formas de pago, no puedo retornar formulario de creacion de cuenta por cobrar (pagar)'.format(
                    tra_codigo))

        return items[0]
