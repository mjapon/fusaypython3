# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import decimal
import logging

from sqlalchemy import and_

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_dao import TFinAmortizaDao
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_model import TFinAmortiza
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_dao import TFinCreditoDao
from fusayrepo.logica.financiero.tfin_pagoscred.tfin_pagoscred_model import TFinPagosCredDet, TFinPagosCredCab
from fusayrepo.logica.fusay.tadjunto.tadjunto_dao import TAdjuntoDao
from fusayrepo.utils import numeros, fechas, cadenas

log = logging.getLogger(__name__)


class TFinPagosCredDao(BaseDao):

    def get_form(self, cred_id):
        form = {
            'cre_id': cred_id,
            'pg_total': 0.0,
            'pg_capital': 0.0,
            'pg_interes': 0.0,
            'pg_mora': 0.0,
            'pg_npago': 1,
            'pg_fecpagocalc': '',
            'pg_amoid': 0
        }
        return form

    def calcular_cuotas(self, cuotas):
        cre_id = cuotas[0]['cre_id']
        codigospagos = []
        for cuota in cuotas:
            codigospagos.append(str(cuota['amo_id']))

        codspagoscad = ",".join(codigospagos)
        sql = """
                select amo_id,
                cre_id, 
                amo_ncuota, amo_fechapago,
                round(amo_saldo + amo_capital +amo_interes,2) saldoini, 
                round(amo_capital +amo_interes,2) cuota,
                round(amo_capital,2) amo_capital, 
                round(amo_interes,2) amo_interes, 
                round(amo_saldo,2) amo_saldo
                from tfin_amortiza where amo_id in ({0}) and cre_id = {1}
                """.format(codspagoscad, cre_id)

        tupla_desc = ('amo_id', 'cre_id', 'amo_ncuota', 'amo_fechapago', 'saldoini', 'cuota', 'amo_capital',
                      'amo_interes', 'amo_saldo')

        datos_cuotoas = self.all(sql, tupla_desc)
        cuotaspagar = []
        total = 0.0
        total_capital = 0.0
        total_interes = 0.0
        total_intmora = 0.0
        for cuota in datos_cuotoas:
            new_form = self.get_form(cre_id)
            new_form['pg_amoid'] = cuota['amo_id']
            new_form['pg_capital'] = cuota['amo_capital']
            new_form['pg_interes'] = cuota['amo_interes']
            new_form['pg_fecpagocalc'] = cuota['amo_fechapago']
            new_form['pg_npago'] = cuota['amo_ncuota']
            new_form['pg_mora'] = self.calcula_mora(fecha_pago=cuota['amo_fechapago'], capital=cuota['amo_capital'])
            new_form['pg_total'] = cuota['cuota'] + new_form['pg_mora']
            total += new_form['pg_total']
            total_capital += new_form['pg_capital']
            total_interes += new_form['pg_interes']
            total_intmora += new_form['pg_mora']
            cuotaspagar.append(new_form)

        return {
            'cre_id': cre_id,
            'pgc_total': numeros.roundm2(total),
            'adjunto': {},
            'pgc_obs': '',
            'pgc_adelanto': 0.0,
            'pgc_total_capital': total_capital,
            'pgc_total_interes': total_interes,
            'pgc_total_intmora': total_intmora,
            'cuotaspagar': cuotaspagar
        }

    def calcula_mora(self, fecha_pago, capital):
        fechapago = fechas.parse_cadena(fecha_pago)
        hoy = datetime.datetime.now()
        ndias = (hoy - fechapago).days
        tasa = 0.0
        mora = 0.0
        if ndias > 0:
            sql = """
            select mr_tasa from tfin_tasamora where {0} between mr_rangoini and mr_rangofin             
            """.format(ndias)
            tasa = self.first_col(sql, 'mr_tasa')
            if tasa is None:
                tasa = 0.0

            mora = float(capital) * tasa * (ndias / 360)

        return mora

    def calcular_cuota(self, cre_id, amo_id):
        sql = """
        select amo_id,
        cre_id, 
        amo_ncuota, amo_fechapago,
        round(amo_saldo + amo_capital +amo_interes,2) saldoini, 
        round(amo_capital +amo_interes,2) cuota,
        round(amo_capital,2) amo_capital, 
        round(amo_interes,2) amo_interes, 
        round(amo_saldo,2) amo_saldo
        from tfin_amortiza where amo_id = {0} and cre_id = {1}
        """.format(amo_id, cre_id)

        tupla_desc = ('amo_id', 'cre_id', 'amo_ncuota', 'amo_fechapago', 'saldoini', 'cuota', 'amo_capital',
                      'amo_interes', 'amo_saldo')

        datos_cuota = self.first(sql, tupla_desc)
        fecha_pago_cuota = datos_cuota['amo_fechapago']

        if fechas.es_fecha_actual_mayor_a_fecha(fecha_pago_cuota):
            # Logica para calculo de multa
            pass

        form = self.get_form(cre_id)
        form['pg_amoid'] = amo_id
        form['pg_total'] = datos_cuota['cuota']
        form['pg_capital'] = datos_cuota['amo_capital']
        form['pg_interes'] = datos_cuota['amo_interes']
        form['pg_fecpagocalc'] = datos_cuota['amo_fechapago']
        form['pg_npago'] = datos_cuota['amo_ncuota']

        return form

    def get_tabla_pagos(self, cred_id):
        sql = """
        select amor.amo_id, amor.cre_id, amo_ncuota, amo_fechapago, 
        round(amo_saldo + amo_capital +amo_interes,2) saldoini, 
        round(amo_capital +amo_interes,2) cuota,
        round(amo_capital,2) amo_capital, 
        round(amo_interes,2) amo_interes, 
        round(amo_saldo,2) amo_saldo,
        amo_estado, amo_fechacrea, amo_usercrea,
        coalesce(pgd.pg_id,0) pg_id,
        case coalesce(pgd.pg_id,0) when 0 then 'Pendiente' else 'Pagado' end as estado,
        pgd.pg_total, pgd.pg_capital, pgd.pg_mora, pgd.pg_npago, pgd.pg_fecpagocalc, 
        pgd.pg_fechacrea, 
        pgd.pg_usercrea,
        pgd.pg_interes,
        coalesce(pgcab.pgc_id,0) as pgc_id,
        now()::date>((amo_fechapago - interval '68 day')::date) as enablepago
        from tfin_amortiza amor
        left join tfin_pagoscreddet pgd on pgd.pg_amoid = amor.amo_id and pgd.pg_estado = 1
        left join tfin_pagoscredcab pgcab on pgd.pgc_id = pgcab.pgc_id 
        where amor.amo_estado = 0 and amor.cre_id = {0}
        order by amo_ncuota
        
        """.format(cred_id)

        tupla_desc = (
            'amo_id',
            'cre_id',
            'amo_ncuota',
            'amo_fechapago',
            'saldoini',
            'cuota',
            'amo_capital',
            'amo_interes',
            'amo_saldo',
            'amo_estado',
            'amo_fechacrea',
            'amo_usercrea',
            'pg_id',
            'estado',
            'pg_total',
            'pg_capital',
            'pg_mora',
            'pg_npago',
            'pg_fecpagocalc',
            'pg_fechacrea',
            'pg_usercrea',
            'pg_interes',
            'pgc_id',
            'enablepago'
        )

        columnas = [
            {'label': '#', 'field': 'amo_ncuota', 'width': '5%'},
            {'label': 'Fecha Pago', 'field': 'amo_fechapago', 'width': '15%'},
            {'label': 'Pago Total', 'field': 'cuota', 'width': '14%'},
            {'label': 'Capital', 'field': 'amo_capital', 'width': '14%'},
            {'label': 'Interes', 'field': 'amo_interes', 'width': '14%'},
            {'label': 'Saldo', 'field': 'amo_saldo', 'width': '14%'},
            {'label': 'Estado', 'field': 'estado', 'width': '14%'}
        ]

        data = self.all(sql, tupla_desc)
        ncuotaspagadas = self.get_ncuotas_pagadas(cre_id=cred_id)
        return {
            'cols': columnas,
            'tabla': data,
            'ncuotaspag': ncuotaspagadas
        }

    def get_ncuotas_pagadas(self, cre_id):
        sql = """
        select count(*) as cuenta
        from tfin_amortiza amor
        join tfin_pagoscreddet pgc on pgc.pg_amoid = amor.amo_id and pgc.pg_estado = 1
        where amor.amo_estado = 0 and amor.cre_id = {0}
        """.format(cre_id)

        cuenta = 0
        cuentaux = self.first_col(sql, 'cuenta')
        if cuentaux is not None:
            cuenta = cuentaux

        return cuenta

    def find_by_pg_id(self, pg_id):
        return self.dbsession.query(TFinPagosCredDet).filter(TFinPagosCredDet.pg_id == pg_id).first()

    def anular_pago(self, pgc_id, user_anula, obs):
        pagoscredcab = self.dbsession.query(TFinPagosCredCab).filter(TFinPagosCredCab.pgc_id == pgc_id).first()
        if pagoscredcab is not None:
            pgc_total = pagoscredcab.pgc_total
            pgc_adelanto = pagoscredcab.pgc_total
            pgc_total_capital = pagoscredcab.pgc_total

            total_capital = pgc_total_capital + pgc_adelanto

            credito_dao = TFinCreditoDao(self.dbsession)
            credito_dao.reversar_saldo_pend(cred_id=pagoscredcab.cre_id, capital=total_capital, user_reversa=user_anula)

            pagoscredcab.pgc_estado = 2
            pagoscredcab.pgc_useranul = user_anula
            pagoscredcab.pgc_fechanul = datetime.datetime.now()
            pagoscredcab.pgc_obsanul = obs

            self.dbsession.add(pagoscredcab)

            # Anular los detalles
            detalles = self.dbsession.query(TFinPagosCredDet).filter(TFinPagosCredDet.pgc_id == pgc_id).all()
            if detalles is not None and len(detalles) > 0:
                for det in detalles:
                    det.pg_estado = 2
                    det.pg_useranul = user_anula
                    det.pg_fecanul = datetime.datetime.now()

            if pgc_adelanto > 0.0:
                # Si hizo un abono de capital entonces se debe reversar la tabla recalculada
                # Anulamos los registros de recalculo en la tabla de amortizacion
                amortiza_new_list = self.dbsession.query(TFinAmortiza).filter(and_(TFinAmortiza.pgc_id == pgc_id,
                                                                                   TFinAmortiza.amo_estado == 0)).all()
                if amortiza_new_list is not None and len(amortiza_new_list) > 0:
                    for amort_new_item in amortiza_new_list:
                        amort_new_item.amo_estado = 1
                        self.dbsession.add(amort_new_item)

                # Reversamos la tabla original que cambió a recalculado por el pago previo
                amortiza_recalc_list = self.dbsession.query(TFinAmortiza).filter(and_(TFinAmortiza.pgc_id == pgc_id,
                                                                                      TFinAmortiza.amo_estado == 2)).all()
                if amortiza_recalc_list is not None and len(amortiza_recalc_list) > 0:
                    for amort_recal_item in amortiza_recalc_list:
                        amort_recal_item.amo_estado = 0
                        self.dbsession.add(amort_recal_item)

    def crear_pago(self, form, user_crea):

        archivo = None
        if 'archivo' in form:
            archivo = form['archivo']

        adj_id = 0
        if archivo is not None:
            adjuntodao = TAdjuntoDao(self.dbsession)
            formadj = {'adj_filename': archivo['adj_filename']}
            adj_id = adjuntodao.crear(formadj, user_crea=user_crea, file=archivo['archivo'])

        cre_id = form['cre_id']
        pg_adelanto = decimal.Decimal(numeros.roundm2(form['pgc_adelanto']))
        pgc_total = decimal.Decimal(numeros.roundm2(form['pgc_total']))
        pgc_total_capital = decimal.Decimal(numeros.roundm2(form['pgc_total_capital']))
        pgc_total_interes = decimal.Decimal(numeros.roundm2(form['pgc_total_interes']))
        pgc_total_intmora = decimal.Decimal(numeros.roundm2(form['pgc_total_intmora']))
        pagoscredcab = TFinPagosCredCab()
        pagoscredcab.cre_id = cre_id
        pagoscredcab.pgc_usercrea = user_crea
        pagoscredcab.pgc_total = pgc_total
        pagoscredcab.pgc_adj = 0
        pagoscredcab.pgc_obs = cadenas.strip(form['pgc_obs'])
        pagoscredcab.pgc_adelanto = pg_adelanto
        pagoscredcab.pgc_fechacrea = datetime.datetime.now()
        pagoscredcab.pgc_estado = 1
        pagoscredcab.pgc_total_capital = pgc_total_capital
        pagoscredcab.pgc_total_interes = pgc_total_interes
        pagoscredcab.pgc_total_intmora = pgc_total_intmora
        pagoscredcab.pgc_adj = adj_id

        cuotaspagar = form['cuotaspagar']

        capital_cuotas = decimal.Decimal(0.0)
        for cuota in cuotaspagar:
            capital_cuotas += decimal.Decimal(numeros.roundm2(cuota['pg_capital']))

        total_capital = capital_cuotas + pg_adelanto

        self.dbsession.add(pagoscredcab)

        credito_dao = TFinCreditoDao(self.dbsession)
        new_saldo_pend = credito_dao.update_saldo_pend(cred_id=cre_id, capital=total_capital, user_upd=user_crea)

        pagoscredcab.pgc_saldopend = new_saldo_pend
        self.dbsession.add(pagoscredcab)

        self.dbsession.flush()
        pgc_id = pagoscredcab.pgc_id

        for cuota in cuotaspagar:
            self.crear_det(form=cuota, user_crea=user_crea, pgc_id=pgc_id)
            self.dbsession.flush()

        msg = 'Registro exitoso'
        if pg_adelanto > 0:
            datos_credito = credito_dao.get_datos_credito(cre_id=cre_id)

            cre_saldopend = datos_credito['cre_saldopend']
            if cre_saldopend > 0:
                amortiza_dao = TFinAmortizaDao(self.dbsession)
                amortiza_dao.cambia_estado_cuotas_amort_impagas(cre_id=cre_id, nuevo_estado=2, pgc_id=pgc_id)
                ncuotas_pagadas = self.get_ncuotas_pagadas(cre_id=cre_id)
                new_plazo = datos_credito['cre_plazo'] - ncuotas_pagadas

                result_tbl = amortiza_dao.generar_guardar_tabla(
                    cred_id=cre_id,
                    monto_prestamo=cre_saldopend,
                    tasa_interes=datos_credito['cre_tasa'],
                    fecha_prestamo=datetime.datetime.now(),
                    ncuotas=new_plazo,
                    user_crea=user_crea,
                    sumancuota=ncuotas_pagadas,
                    pgc_id=pgc_id
                )
                msg += ",se hizo una actualización de la tabla de amortización"

        return {
            'pgc_id': pgc_id,
            'msg': msg
        }

    def crear_det(self, form, user_crea, pgc_id):
        pg_total = form['pg_total']
        pg_capital = form['pg_capital']
        pg_interes = form['pg_interes']

        pg_mora = form['pg_mora']
        pg_npago = form['pg_npago']
        pg_fecpagocalc = form['pg_fecpagocalc']
        pg_amoid = form['pg_amoid']

        pago = TFinPagosCredDet()
        pago.pgc_id = pgc_id
        pago.pg_total = numeros.roundm2(pg_total)
        pago.pg_capital = numeros.roundm2(pg_capital)
        pago.pg_interes = numeros.roundm2(pg_interes)
        pago.pg_mora = numeros.roundm2(pg_mora)
        pago.pg_npago = pg_npago
        pago.pg_fecpagocalc = fechas.parse_cadena(pg_fecpagocalc)
        pago.pg_usercrea = user_crea
        pago.pg_estado = 1
        pago.pg_amoid = pg_amoid
        pago.pg_fechacrea = datetime.datetime.now()

        self.dbsession.add(pago)

    def get_detalles_pago(self, pgc_id):
        sql = """
        select pgc_id, cre_id, pgc_usercrea, pgc_total, pgc_adj, pgc_obs, 
        pgc_adelanto, pgc_fechacrea, pgc_estado, pgc_useranul, pgc_fechanul,
        pgc_obsanul, pgc_saldopend, pgc_total_capital, pgc_total_interes, pgc_total_intmora,
        adj.adj_filename, vu.referente as user
        from tfin_pagoscredcab cab
        left join vusers vu on cab.pgc_usercrea = vu.us_id
        left join tadjunto adj on cab.pgc_adj = adj.adj_id
        where cab.pgc_id = {0}
        """.format(pgc_id)

        tupla_desc = (
            'pgc_id', 'cre_id', 'pgc_usercrea', 'pgc_total', 'pgc_adj', 'pgc_obs', 'pgc_adelanto', 'pgc_fechacrea',
            'pgc_estado', 'pgc_useranul', 'pgc_fechanul', 'pgc_obsanul', 'pgc_saldopend', 'pgc_total_capital',
            'pgc_total_interes', 'pgc_total_intmora', 'adj_filename', 'user')

        datos_pago = self.first(sql, tupla_desc)
        return datos_pago
