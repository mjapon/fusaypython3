# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_model import TFinAmortiza
from fusayrepo.utils import numeros, fechas

log = logging.getLogger(__name__)


class TFinAmortizaDao(BaseDao):

    def get_fila_tabla(self, saldo_ini, cuota_mensual, tasa, fecha):
        interes = saldo_ini * tasa / 12
        roud_interes = numeros.roundm2(interes)
        capital = cuota_mensual - interes
        round_capital = numeros.roundm2(capital)
        saldo = saldo_ini - capital
        next_date = fechas.sumar_meses(fecha, 1)
        return {
            'capital': round_capital,
            'interes': roud_interes,
            'saldo': saldo,
            'nextdate': next_date
        }

    def get_tabla(self, cre_id):
        sql = """
        select amo_id, cre_id, amo_ncuota, amo_fechapago, 
        round(amo_saldo + amo_capital +amo_interes,2) saldoini, 
        round(amo_capital +amo_interes,2) cuota,
        round(amo_capital,2) amo_capital, 
        round(amo_interes,2) amo_interes, 
        round(amo_saldo,2) amo_saldo,
        amo_estado, amo_fechacrea, amo_usercrea from tfin_amortiza where cre_id = {0} and amo_estado = 0
        """.format(cre_id)

        tupla_desc = ('amo_id', 'cre_id', 'amo_ncuota', 'amo_fechapago', 'saldoini', 'cuota',
                      'amo_capital', 'amo_interes', 'amo_saldo', 'amo_estado', 'amo_fechacrea',
                      'amo_usercrea')

        columnas = [
            {'label': '#', 'field': 'amo_ncuota', 'width': '5%'},
            {'label': 'Fecha Pago', 'field': 'amo_fechapago', 'width': '15%'},
            {'label': 'Saldo Inicial', 'field': 'saldoini', 'width': '14%'},
            {'label': 'Pago Total', 'field': 'cuota', 'width': '14%'},
            {'label': 'Capital', 'field': 'amo_capital', 'width': '14%'},
            {'label': 'Interes', 'field': 'amo_interes', 'width': '14%'},
            {'label': 'Saldo', 'field': 'amo_saldo', 'width': '14%'}
        ]

        data = self.all(sql, tupla_desc)
        return {
            'cols': columnas,
            'tabla': data
        }

    def calcular_tabla(self, monto_prestamo, tasa_interes, fecha_prestamo, ncuotas):
        tasa = tasa_interes / 100.0
        pago_mensual_dec = (tasa / 12) * (1 / (1 - (1 + tasa / 12) ** (-ncuotas))) * monto_prestamo
        pago_mensual = numeros.roundm2(pago_mensual_dec)

        saldo_it = monto_prestamo
        fecha_it = fecha_prestamo

        tablamor = []
        total_intereses = 0.0

        for i in range(1, ncuotas + 1):
            new_fila = {}
            saldo_ini = saldo_it
            fila_tbl_amor = self.get_fila_tabla(saldo_ini=saldo_it, cuota_mensual=pago_mensual_dec, tasa=tasa,
                                                fecha=fecha_it)
            total_intereses += fila_tbl_amor['interes']
            saldo_it = fila_tbl_amor['saldo']
            fecha_it = fila_tbl_amor['nextdate']
            new_fila['fila'] = i
            new_fila['saldoini'] = numeros.roundm2(saldo_ini)
            new_fila['fecha'] = fechas.parse_fecha(fecha_it)
            new_fila['cuota'] = pago_mensual
            new_fila['capital'] = numeros.roundm2(fila_tbl_amor['capital'])
            new_fila['interes'] = numeros.roundm2(fila_tbl_amor['interes'])
            new_fila['saldo'] = numeros.roundm2(saldo_it)

            tablamor.append(new_fila)

        columnas = [
            {'label': '#', 'field': 'fila', 'width': '5%'},
            {'label': 'Fecha Pago', 'field': 'fecha', 'width': '15%'},
            {'label': 'Saldo Inicial', 'field': 'saldoini', 'width': '14%'},
            {'label': 'Pago Total', 'field': 'cuota', 'width': '14%'},
            {'label': 'Capital', 'field': 'capital', 'width': '14%'},
            {'label': 'Interes', 'field': 'interes', 'width': '14%'},
            {'label': 'Saldo', 'field': 'saldo', 'width': '14%'}
        ]

        return {
            'total_int': numeros.roundm2(total_intereses),
            'total_prest': numeros.roundm2(monto_prestamo + total_intereses),
            'cuota_mensual': pago_mensual,
            'tabla': tablamor,
            'cols': columnas
        }

    def cambia_estado_cuotas_amort_impagas(self, cre_id, nuevo_estado, pgc_id):
        sql = """
        select amor.amo_id from tfin_amortiza amor
        where amor.amo_estado = 0 and amor.cre_id ={0} and 
        amor.amo_id not in (
            select pgd.pg_amoid from tfin_pagoscreddet pgd
            join tfin_pagoscredcab pgc on pgd.pgc_id = pgc.pgc_id
            where pgd.pg_estado = 1 and pgc.cre_id = {0} 
        )
        """.format(cre_id)

        lista_amortiza = self.all(sql, tupla_desc=('amo_id',))
        if lista_amortiza is not None and len(lista_amortiza) > 0:
            for amorti_row in lista_amortiza:
                tfinamortiza = self.dbsession.query(TFinAmortiza) \
                    .filter(TFinAmortiza.amo_id == amorti_row['amo_id']).first()
                tfinamortiza.amo_estado = nuevo_estado
                tfinamortiza.pgc_id = pgc_id
                self.dbsession.add(tfinamortiza)

    def anular_tabla(self, cred_id):
        sql = """
        select amor.amo_id from tfin_amortiza amor where amor.amo_estado = 0
        and amor.cre_id = {0}
        """.format(cred_id)

        lista_amortiza = self.all(sql, tupla_desc=('amo_id',))
        if lista_amortiza is not None and len(lista_amortiza) > 0:
            for amorti_row in lista_amortiza:
                tfinamortiza = self.dbsession.query(TFinAmortiza) \
                    .filter(TFinAmortiza.amo_id == amorti_row['amo_id']).first()
                tfinamortiza.amo_estado = 1
                self.dbsession.add(tfinamortiza)

    def generar_guardar_tabla(self, cred_id, monto_prestamo, tasa_interes, fecha_prestamo, ncuotas,
                              user_crea, sumancuota=0, pgc_id=None):
        tasa = tasa_interes / 100.0
        pago_mensual_dec = (tasa / 12) * (1 / (1 - (1 + tasa / 12) ** (-ncuotas))) * monto_prestamo
        pago_mensual = numeros.roundm2(pago_mensual_dec)

        total_intereses = 0.0

        saldo_it = monto_prestamo
        fecha_it = fecha_prestamo

        for i in range(1, ncuotas + 1):
            fila_tbl_amor = self.get_fila_tabla(saldo_ini=saldo_it, cuota_mensual=pago_mensual_dec, tasa=tasa,
                                                fecha=fecha_it)
            fecha_it = fila_tbl_amor['nextdate']
            total_intereses += fila_tbl_amor['interes']
            saldo_it = fila_tbl_amor['saldo']

            tcj_amortiza = TFinAmortiza()
            tcj_amortiza.cre_id = cred_id
            tcj_amortiza.amo_ncuota = i + sumancuota
            tcj_amortiza.amo_fechapago = fecha_it
            tcj_amortiza.amo_capital = fila_tbl_amor['capital']
            tcj_amortiza.amo_interes = fila_tbl_amor['interes']
            tcj_amortiza.amo_saldo = fila_tbl_amor['saldo']
            tcj_amortiza.amo_estado = 0
            tcj_amortiza.amo_fechacrea = datetime.datetime.now()
            tcj_amortiza.amo_usercrea = user_crea
            tcj_amortiza.pgc_id = pgc_id
            self.dbsession.add(tcj_amortiza)

        return {
            'total_int': numeros.roundm2(total_intereses),
            'total_prest': numeros.roundm2(monto_prestamo + total_intereses),
            'cuota_mensual': pago_mensual
        }
