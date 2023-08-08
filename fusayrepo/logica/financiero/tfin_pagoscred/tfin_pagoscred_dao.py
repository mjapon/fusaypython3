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
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_dao import TFinAmortizaDao
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_model import TFinAmortiza
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_dao import TFinCreditoDao
from fusayrepo.logica.financiero.tfin_pagoscred.tfin_pagoscred_model import TFinPagosCredDet, TFinPagosCredCab
from fusayrepo.logica.fusay.tadjunto.tadjunto_dao import TAdjuntoDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
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
            'pg_amoid': 0,
            'pgc_fechapago': fechas.get_str_fecha_actual()
        }

        return form

    def get_form_calc_pago(self):
        return {
            'fecpago': fechas.get_str_fecha_actual(),
            'fecpagoobj': fechas.get_str_fecha_actual(),
            'cuotas': []
        }

    def get_ctas_for_pago(self):
        paramsdao = TParamsDao(self.dbsession)
        cj_ctas_cont_pagos = paramsdao.get_param_value('cj_ctas_cont_pagos')
        if cj_ctas_cont_pagos is None:
            raise ErrorValidacionExc('El parametro cj_ctas_cont_pagos no esta configurado favor verificar')

        itemconfidao = TItemConfigDao(self.dbsession)
        datos_cta_debe = itemconfidao.get_detalles_ctacontable_by_codes(ic_codes=cj_ctas_cont_pagos)
        cta_pago = 0
        if datos_cta_debe is not None and len(datos_cta_debe) > 0:
            cta_pago = datos_cta_debe[0]['ic_code']

        return {
            'cta_pago': cta_pago,
            'cta_pagos': datos_cta_debe
        }

    def calcular_cuotas_pagar(self, cuotas, fecha_pago=None, calcular_mora=True):
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
                round(amo_capital +amo_interes + amo_seguro,2) cuota,
                round(amo_capital,2) amo_capital, 
                round(amo_interes,2) amo_interes,
                round(amo_seguro,2) amo_seguro, 
                round(amo_saldo,2) amo_saldo
                from tfin_amortiza where amo_id in ({0}) and cre_id = {1}
                """.format(codspagoscad, cre_id)

        tupla_desc = ('amo_id', 'cre_id', 'amo_ncuota', 'amo_fechapago', 'saldoini', 'cuota',
                      'amo_capital', 'amo_seguro', 'amo_interes', 'amo_saldo')

        datos_cuotas = self.all(sql, tupla_desc)

        sql = "select cre_tasa from tfin_credito where cre_id = {0}".format(cre_id)
        cre_tasa = self.first_col(sql, 'cre_tasa')

        cuotaspagar = []
        total = 0.0
        total_capital = 0.0
        total_interes = 0.0
        total_seguro = 0.0
        total_intmora = 0.0
        for cuota in datos_cuotas:
            new_form = self.get_form(cre_id)
            new_form['pg_amoid'] = cuota['amo_id']
            new_form['pg_capital'] = cuota['amo_capital']
            new_form['pg_interes'] = cuota['amo_interes']
            new_form['pg_seguro'] = cuota['amo_seguro']
            new_form['pg_fecpagocalc'] = cuota['amo_fechapago']
            new_form['pg_npago'] = cuota['amo_ncuota']
            new_form['pg_mora'] = 0.0
            if calcular_mora:
                new_form['pg_mora'] = self.calcula_mora(fecha_planif_pago=cuota['amo_fechapago'],
                                                        capital=cuota['amo_capital'],
                                                        tasa_prestamo=cre_tasa, fecha_pago=fecha_pago)
            new_form['pg_total'] = numeros.roundm2(cuota['cuota'] + new_form['pg_mora'])
            total += new_form['pg_total']
            total_capital += new_form['pg_capital']
            total_interes += new_form['pg_interes']
            total_intmora += new_form['pg_mora']
            total_seguro += new_form['pg_seguro']
            cuotaspagar.append(new_form)

        infocontable = self.get_ctas_for_pago()

        return {
            'cre_id': cre_id,
            'pgc_total': numeros.roundm2(total),
            'adjunto': {},
            'pgc_obs': '',
            'pgc_adelanto': 0.0,
            'pgc_total_capital': total_capital,
            'pgc_total_interes': total_interes,
            'pgc_total_intmora': total_intmora,
            'pgc_total_seguro': total_seguro,
            'cuotaspagar': cuotaspagar,
            'cta_pago': infocontable['cta_pago'],
            'cta_pagos': infocontable['cta_pagos'],
            'pgc_fechapago': ''
        }

    def calcula_mora(self, fecha_planif_pago, capital, tasa_prestamo, fecha_pago):
        fechapago = fechas.parse_cadena(fecha_planif_pago)
        fecha_pago_obj = fechas.parse_cadena(fecha_pago)
        ndias = (fecha_pago_obj - fechapago).days
        mora = 0.0
        if ndias > 0:
            sql = """
            select mr_tasa from tfin_tasamora where {0} between mr_rangoini and mr_rangofin             
            """.format(ndias)
            tasa_mora = self.first_col(sql, 'mr_tasa')
            if tasa_mora is None:
                tasa_mora = 0.0

            tasa_mora_efectiva = float(tasa_prestamo) * float(tasa_mora)

            mora = numeros.roundm2(float(capital) * float(tasa_mora_efectiva) * (ndias / 360))

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
        round(amo_capital +amo_interes+amo_seguro,2) cuota,
        round(amo_capital,2) amo_capital, 
        round(amo_interes,2) amo_interes,
        round(amo_seguro,2) amo_seguro, 
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
            'amo_seguro',
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
            {'label': 'Pago Total', 'field': 'cuota', 'width': '12%'},
            {'label': 'Capital', 'field': 'amo_capital', 'width': '12%'},
            {'label': 'Interes', 'field': 'amo_interes', 'width': '12%'},
            {'label': 'Seguro', 'field': 'amo_seguro', 'width': '12%'},
            {'label': 'Saldo', 'field': 'amo_saldo', 'width': '10%'},
            {'label': 'Estado', 'field': 'estado', 'width': '12%'}
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
            pgc_total_capital = pagoscredcab.pgc_total_capital
            pgc_adelanto = pagoscredcab.pgc_adelanto
            credito_dao = TFinCreditoDao(self.dbsession)

            credito_dao.reversar_saldo_pend(cred_id=pagoscredcab.cre_id, capital=pgc_total_capital + pgc_adelanto,
                                            user_reversa=user_anula)

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

                credito = credito_dao.find_by_credid(cre_id=pagoscredcab.cre_id)
                if credito is not None:
                    credito.cre_cuota = pagoscredcab.pgc_valcuotantes
                    self.dbsession.add(credito)

            tasidao = TasientoDao(self.dbsession)
            trn_codigo_pago = pagoscredcab.pgc_trncod

            tasidao.anular(trn_codigo=trn_codigo_pago, user_anula=user_anula,
                           obs_anula="P/R Anulacion pago de credito")

    def marcar_como_pagado(self, form, user_crea):
        archivo = None
        if 'archivo' in form:
            archivo = form['archivo']

        adj_id = 0
        if archivo is not None:
            adjuntodao = TAdjuntoDao(self.dbsession)
            formadj = {'adj_filename': archivo['adj_filename']}
            adj_id = adjuntodao.crear(formadj, user_crea=user_crea, file=archivo['archivo'])

        cre_id = form['cre_id']

        credito_dao = TFinCreditoDao(self.dbsession)

        credito = credito_dao.find_by_credid(cre_id=cre_id)
        cre_saldopend = decimal.Decimal(numeros.roundm2(credito.cre_saldopend))

        pg_adelanto = 0.0

        pgc_total = decimal.Decimal(numeros.roundm2(form['pgc_total']))

        if numeros.roundm2(pgc_total) > numeros.roundm2(cre_saldopend):
            raise ErrorValidacionExc(
                'El pago total:{0} sobrepasa la deuda del crédito:{1}'.format(numeros.roundm2(pgc_total),
                                                                              numeros.roundm2(cre_saldopend)))

        pgc_total_capital = decimal.Decimal(numeros.roundm2(form['pgc_total_capital']))
        pgc_total_interes = decimal.Decimal(numeros.roundm2(form['pgc_total_interes']))
        pgc_total_intmora = decimal.Decimal(numeros.roundm2(form['pgc_total_intmora']))
        pgc_total_seguro = decimal.Decimal(numeros.roundm2(form['pgc_total_seguro']))
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
        pagoscredcab.pgc_total_seguro = pgc_total_seguro
        pagoscredcab.pgc_adj = adj_id
        pagoscredcab.pgc_fechapago = fechas.parse_cadena(form['pgc_fechapago'])

        cuotaspagar = form['cuotaspagar']

        capital_cuotas = decimal.Decimal(0.0)
        for cuota in cuotaspagar:
            capital_cuotas += decimal.Decimal(numeros.roundm2(cuota['pg_capital']))

        total_capital = capital_cuotas

        self.dbsession.add(pagoscredcab)
        new_saldo_pend = credito_dao.update_saldo_pend(cred_id=cre_id, capital=total_capital, user_upd=user_crea)

        pagoscredcab.pgc_saldopend = new_saldo_pend
        self.dbsession.add(pagoscredcab)

        self.dbsession.flush()
        pgc_id = pagoscredcab.pgc_id

        for cuota in cuotaspagar:
            self.crear_det(form=cuota, user_crea=user_crea, pgc_id=pgc_id)
            self.dbsession.flush()

        pagoscredcab.pgc_trncod = 0
        self.dbsession.add(pagoscredcab)

        msg = 'Registro exitoso'

        if new_saldo_pend == 0:
            msg += ", El crédito {0} ha sido cancelado en su totalidad".format(cre_id)

        return {
            'pgc_id': pgc_id,
            'msg': msg
        }

    def crear_pago(self, form, user_crea, sec_codigo):
        archivo = None
        if 'archivo' in form:
            archivo = form['archivo']

        adj_id = 0
        if archivo is not None:
            adjuntodao = TAdjuntoDao(self.dbsession)
            formadj = {'adj_filename': archivo['adj_filename']}
            adj_id = adjuntodao.crear(formadj, user_crea=user_crea, file=archivo['archivo'])

        cre_id = form['cre_id']

        credito_dao = TFinCreditoDao(self.dbsession)
        # Se debe actualizar el monto de la cuota mensual
        credito = credito_dao.find_by_credid(cre_id=cre_id)
        cre_saldopend = decimal.Decimal(numeros.roundm2(credito.cre_saldopend))

        pg_adelanto = decimal.Decimal(numeros.roundm2(form['pgc_adelanto']))

        pgc_total = decimal.Decimal(numeros.roundm2(form['pgc_total']))

        pgc_total_capital = decimal.Decimal(numeros.roundm2(form['pgc_total_capital']))
        pgc_total_interes = decimal.Decimal(numeros.roundm2(form['pgc_total_interes']))
        pgc_total_intmora = decimal.Decimal(numeros.roundm2(form['pgc_total_intmora']))
        pgc_total_seguro = decimal.Decimal(numeros.roundm2(form['pgc_total_seguro']))

        pgc_total_capital_adelanto = numeros.roundm2(decimal.Decimal(form['pgc_adelanto'])
                                                     + decimal.Decimal(form['pgc_total_capital']))
        # Validar montos
        if pg_adelanto < 0:
            raise ErrorValidacionExc('El abono de capital no puede ser negativo')

        if numeros.roundm2(pgc_total_capital_adelanto) > numeros.roundm2(cre_saldopend):
            raise ErrorValidacionExc(
                'El pago total de capital:{0} sobrepasa la deuda del crédito:{1} (adelanto + capital:{2}, adelanto: {3})'.format(
                    numeros.roundm2(pgc_total_capital),
                    numeros.roundm2(cre_saldopend),
                    pgc_total_capital_adelanto,
                    numeros.roundm2(pg_adelanto)
                )
            )

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
        pagoscredcab.pgc_total_seguro = pgc_total_seguro
        pagoscredcab.pgc_adj = adj_id
        pagoscredcab.pgc_fechapago = fechas.parse_cadena(form['pgc_fechapago'])

        cuotaspagar = form['cuotaspagar']

        capital_cuotas = decimal.Decimal(0.0)
        for cuota in cuotaspagar:
            capital_cuotas += decimal.Decimal(numeros.roundm2(cuota['pg_capital']))

        total_capital = capital_cuotas + pg_adelanto

        self.dbsession.add(pagoscredcab)
        new_saldo_pend = credito_dao.update_saldo_pend(cred_id=cre_id, capital=total_capital, user_upd=user_crea)

        pagoscredcab.pgc_saldopend = new_saldo_pend
        self.dbsession.add(pagoscredcab)

        self.dbsession.flush()
        pgc_id = pagoscredcab.pgc_id

        pg_fecpagomax = fechas.get_str_fecha_actual()
        for cuota in cuotaspagar:
            pg_fecpagocalc_it = cuota['pg_fecpagocalc']
            if fechas.es_fecha_a_mayor_o_igual_fecha_b(pg_fecpagocalc_it, pg_fecpagomax):
                pg_fecpagomax = pg_fecpagocalc_it

            self.crear_det(form=cuota, user_crea=user_crea, pgc_id=pgc_id)
            self.dbsession.flush()

        tasicred_dao = TAsicreditoDao(self.dbsession)

        datos_credito = credito_dao.get_datos_credito(cre_id=cre_id)
        trn_codigo_pago = tasicred_dao.create_asiento_pago(per_codigo=datos_credito['per_id'], sec_codigo=sec_codigo,
                                                           total=pgc_total, capital=total_capital,
                                                           interes=pgc_total_interes,
                                                           mora=pgc_total_intmora, cta_pago=form['cta_pago'],
                                                           usercrea=user_crea, seguro=pgc_total_seguro)
        pagoscredcab.pgc_trncod = trn_codigo_pago
        self.dbsession.add(pagoscredcab)

        msg = 'Registro exitoso'

        if pg_adelanto > 0 and new_saldo_pend > 0:
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
                    fecha_prestamo=fechas.parse_cadena(pg_fecpagomax),
                    ncuotas=new_plazo,
                    user_crea=user_crea,
                    sumancuota=ncuotas_pagadas,
                    pgc_id=pgc_id
                )
                msg += ",se hizo una actualización de la tabla de amortización"

                # credito.cre_totalint = result_tbl['total_int']
                cre_cuota_antes = credito.cre_cuota
                credito.cre_cuota = result_tbl['cuota_mensual']

                pagoscredcab.pgc_trncod = trn_codigo_pago
                pagoscredcab.pgc_valcuotantes = cre_cuota_antes
                pagoscredcab.pgc_valcuotadesp = credito.cre_cuota
                self.dbsession.add(pagoscredcab)
                self.dbsession.add(credito)

        if new_saldo_pend == 0:
            # Se debe cambiar el stado del credito a cancelado
            msg += ", El crédito {0} ha sido cancelado en su totalidad".format(cre_id)

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
        pg_seguro = form['pg_seguro']
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
        pago.pg_seguro = pg_seguro

        self.dbsession.add(pago)

    def get_detalles_pago(self, pgc_id):
        sql = """
        select pgc_id, cre_id, pgc_usercrea, pgc_total, pgc_adj, pgc_obs, 
        pgc_adelanto, pgc_fechacrea, pgc_estado, pgc_useranul, pgc_fechanul,
        pgc_obsanul, pgc_saldopend, pgc_total_capital, pgc_total_interes, pgc_total_interes, pgc_total_intmora,
        pgc_total_seguro, adj.adj_filename, vu.referente as user, pgc_fechapago
        from tfin_pagoscredcab cab
        left join vusers vu on cab.pgc_usercrea = vu.us_id
        left join tadjunto adj on cab.pgc_adj = adj.adj_id
        where cab.pgc_id = {0}
        """.format(pgc_id)

        tupla_desc = (
            'pgc_id', 'cre_id', 'pgc_usercrea', 'pgc_total', 'pgc_adj', 'pgc_obs', 'pgc_adelanto', 'pgc_fechacrea',
            'pgc_estado', 'pgc_useranul', 'pgc_fechanul', 'pgc_obsanul', 'pgc_saldopend', 'pgc_total_capital',
            'pgc_total_interes', 'pgc_total_intmora', 'pgc_total_seguro', 'adj_filename', 'user', 'pgc_fechapago')

        datos_pago = self.first(sql, tupla_desc)
        return datos_pago
