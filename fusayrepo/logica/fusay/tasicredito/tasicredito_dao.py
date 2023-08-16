# coding: utf-8
"""
Fecha de creacion 1/8/21
@autor: mjapon
"""
import decimal
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasicredito.tasicredito_model import TAsicredito
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.utils import ctes, fechas, numeros, cadenas

log = logging.getLogger(__name__)


class TAsicreditoDao(BaseDao):

    def crear(self, form):
        tasicredito = TAsicredito()

        cre_tipo = tasicredito.cre_tipo = form['cre_tipo']

        tra_codigo_cred = ctes.TRA_COD_CRED_VENTA
        if int(cre_tipo) == 2:
            tra_codigo_cred = ctes.TRA_COD_CRED_COMPRA

        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
        resestabsec = ttransacc_pdv.get_estabptoemi_secuencia(alm_codigo=0, tra_codigo=tra_codigo_cred,
                                                              tdv_codigo=0, sec_codigo=0)
        secuencia = resestabsec['secuencia']
        len_compro = ctes.LEN_DOC_TRANSACC
        cre_compro = "{0}".format(str(secuencia)).zfill(len_compro)

        tasicredito.dt_codigo = form['dt_codigo']
        if form['cre_fecini'] is not None:
            tasicredito.cre_fecini = fechas.parse_cadena(form['cre_fecini'])
        if form['cre_fecven'] is not None:
            tasicredito.cre_fecven = fechas.parse_cadena(form['cre_fecven'])
        tasicredito.cre_intere = form['cre_intere']
        tasicredito.cre_intmor = form['cre_intmor']
        tasicredito.cre_compro = cre_compro
        tasicredito.cre_codban = form['cre_codban']
        tasicredito.cre_saldopen = form['cre_saldopen']
        tasicredito.cre_tipo = form['cre_tipo']

        self.dbsession.add(tasicredito)
        ttransacc_pdv.gen_secuencia(tps_codigo=resestabsec['tps_codigo'], secuencia=secuencia)
        self.flush()

        return tasicredito.cre_codigo

    def clone_formdet(self, formdet):
        newformdet = {}
        for key in formdet.keys():
            newformdet[key] = formdet[key]
        return newformdet

    def get_form(self, clase, per_codigo, sec_codigo):
        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)
        formasiento = tasientodao.get_form_asiento(sec_codigo=sec_codigo)

        tparamdao = TParamsDao(self.dbsession)
        cod_cta_caja = tparamdao.get_param_value('codCtaContabCaj')
        cod_cta_ban = tparamdao.get_param_value('codCtaContabBan')
        cod_cta_ing = "5.%"
        cod_cta_gast = "4.%"

        cajabancos = "({0}%|{1}%)".format(cod_cta_caja, cod_cta_ban)

        tra_codigo = ctes.TRA_COD_FACT_VENTA
        codeparent = '{0}'.format(cod_cta_ing)
        if int(clase) == 2:
            tra_codigo = ctes.TRA_COD_FACT_COMPRA
            codeparent = '{0}'.format(cod_cta_gast)

        ttransapgadodao = TTransaccPagoDao(self.dbsession)
        datoscuentacred = ttransapgadodao.get_datos_cuenta_credito(tra_codigo=tra_codigo, sec_id=sec_codigo)

        tupla_desc = ('ic_id', 'ic_code', 'ic_nombre', 'codnombre', 'ic_clasecc')
        filacodmerc = None
        if tra_codigo == ctes.TRA_COD_FACT_COMPRA:
            # En las cuentas disponibles agregar la cuenta en el modelo contable para esta transaccion
            sql = """
            select ic.ic_id, ic.ic_code, ic.ic_nombre, ic.ic_code ||' '||ic_nombre as codnombre, ic.ic_clasecc from tmodelocontabdet a
            join titemconfig ic on ic.ic_id = a.cta_codigo
            where mc_id = 1 and tra_codigo = {0} and sec_codigo = {1}
            """.format(tra_codigo, sec_codigo)
            filacodmerc = self.first(sql, tupla_desc)

        sql = """
                select ic.ic_id, ic_code, ic_nombre, ic_code ||' '||ic_nombre as codnombre, ic_clasecc 
                from titemconfig ic
                join titemconfig_sec ics on ics.ic_id = ic.ic_id and ics.sec_id = {sec_id}  
                where
                tipic_id = 3 and ic_estado = 1 and ic_haschild = false and  ic_code similar to '{parent}' 
                and ic_code not similar to '{cajabancos}'  order by ic_code desc, ic_nombre asc 
                """.format(parent=codeparent, cajabancos=cajabancos, sec_id=sec_codigo)

        cuentasformov = self.all(sql, tupla_desc)
        if filacodmerc is not None:
            cuentasformov.append(filacodmerc)

        titulo = "cuenta por cobrar"
        if int(clase) == 2:
            titulo = "cuenta por pagar"

        form = {
            'clase': clase,
            'monto': 0.0,
            'cta_codigo_main': datoscuentacred['cta_codigo'],
            'dt_debito_main': datoscuentacred['dt_debito'],
            'ic_clasecc': datoscuentacred['ic_clasecc'],
            'cta_codigo_aux': 0,
            'motivos': [{'cta_codigo': 0, 'dt_valor': 0.0}]
        }

        formasiento['formref']['per_id'] = per_codigo

        return {
            'titulo': titulo,
            'formtopost': {'form': form, 'formasiento': formasiento},
            'cuentasforcred': cuentasformov
        }

    def create_asiento_pago(self, per_codigo, sec_codigo, total, capital, interes, mora, cta_pago, usercrea, seguro,
                            observacion):

        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)

        formasiento = tasientodao.get_form_asiento(sec_codigo=sec_codigo)

        formasiento['formasiento']['trn_docpen'] = 'F'
        formasiento['formasiento']['trn_observ'] = observacion
        formasiento['formref']['per_id'] = per_codigo

        formdet = formasiento['formdet']
        detalles = []

        tparamsdao = TParamsDao(self.dbsession)

        ctahaber = tparamsdao.get_param_value('cj_cta_presta_debe')
        ctadebe = cta_pago

        ctahaber_interes = tparamsdao.get_param_value('cj_cta_int')
        ctahaber_mora = tparamsdao.get_param_value('cj_cta_mora')
        ctahaber_seguro = tparamsdao.get_param_value('cj_cta_seguro')

        if ctadebe is None:
            raise ErrorValidacionExc('Debe seleccionar la cuenta en la que se acredita el pago')

        if ctahaber is None:
            raise ErrorValidacionExc('Parámetro cj_cta_presta_debe no configurado, favor verificar')

        if ctahaber_interes is None:
            raise ErrorValidacionExc('Parámetro cj_cta_int no configurado, favor verificar')

        if ctahaber_mora is None:
            raise ErrorValidacionExc('Parámetro cj_cta_mora no configurado, favor verificar')

        if ctahaber_seguro is None:
            raise ErrorValidacionExc('Parámetro cj_cta_seguro no configurado, favor verificar')

        itemconfidao = TItemConfigDao(self.dbsession)
        datos_cta_debe = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctadebe)
        if datos_cta_debe is None:
            raise ErrorValidacionExc('No pude recuperar la informacion de la cuenta contable {0}'.format(ctadebe))

        datos_cta_haber = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctahaber)

        if datos_cta_haber is None:
            raise ErrorValidacionExc('No pude recuperar la informacion de la cuenta contable {0}'.format(ctadebe))

        datos_ctahaber_int = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctahaber_interes)

        if datos_ctahaber_int is None:
            raise ErrorValidacionExc(
                'No pude recuperar la informacion de la cuenta contable {0}'.format(datos_ctahaber_int))

        datos_ctahaber_mora = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctahaber_mora)
        if datos_ctahaber_mora is None:
            raise ErrorValidacionExc(
                'No pude recuperar la informacion de la cuenta contable {0}'.format(datos_ctahaber_mora))

        datos_ctahaber_seguro = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctahaber_seguro)
        if datos_ctahaber_seguro is None:
            raise ErrorValidacionExc(
                'No pude recuperar la informacion de la cuenta contable {0}'.format(datos_ctahaber_seguro))

        debedet = self.clone_formdet(formdet)
        debedet['dt_debito'] = 1
        debedet['dt_valor'] = numeros.roundm2(total)
        debedet['cta_codigo'] = datos_cta_debe['ic_id']
        debedet['ic_clasecc'] = ''
        detalles.append(debedet)

        haberdet = self.clone_formdet(formdet)
        haberdet['dt_debito'] = -1
        haberdet['dt_valor'] = numeros.roundm2(capital)
        haberdet['cta_codigo'] = datos_cta_haber['ic_id']
        haberdet['ic_clasecc'] = ''
        detalles.append(haberdet)

        haberdet_int = self.clone_formdet(formdet)
        haberdet_int['dt_debito'] = -1
        haberdet_int['dt_valor'] = numeros.roundm2(interes)
        haberdet_int['cta_codigo'] = datos_ctahaber_int['ic_id']
        haberdet_int['ic_clasecc'] = ''
        detalles.append(haberdet_int)

        if mora > 0:
            haberdet_mora = self.clone_formdet(formdet)
            haberdet_mora['dt_debito'] = -1
            haberdet_mora['dt_valor'] = numeros.roundm2(mora)
            haberdet_mora['cta_codigo'] = datos_ctahaber_mora['ic_id']
            haberdet_mora['ic_clasecc'] = ''
            detalles.append(haberdet_mora)
        if seguro > 0:
            haberdet_seguro = self.clone_formdet(formdet)
            haberdet_seguro['dt_debito'] = -1
            haberdet_seguro['dt_valor'] = numeros.roundm2(seguro)
            haberdet_seguro['cta_codigo'] = datos_ctahaber_seguro['ic_id']
            haberdet_seguro['ic_clasecc'] = ''
            detalles.append(haberdet_seguro)

        formasiento['detalles'] = detalles

        trn_codigo_gen = tasientodao.crear_asiento(formcab=formasiento['formasiento'],
                                                   formref=formasiento['formref'],
                                                   usercrea=usercrea,
                                                   detalles=formasiento['detalles'], update_datosref=False)

        return trn_codigo_gen

    def create_asiento_prestamo(self, per_codigo, sec_codigo, monto, usercrea):

        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)

        formasiento = tasientodao.get_form_asiento(sec_codigo=sec_codigo)

        formasiento['formasiento']['trn_docpen'] = 'F'
        formasiento['formasiento']['trn_observ'] = 'P/R Débito por aprobación de crédito'
        formasiento['formref']['per_id'] = per_codigo

        formdet = formasiento['formdet']
        detalles = []

        tparamsdao = TParamsDao(self.dbsession)

        ctadebe = tparamsdao.get_param_value('cj_cta_presta_debe')
        ctahaber = tparamsdao.get_param_value('cj_cta_presta_haber')

        if ctadebe is None:
            raise ErrorValidacionExc('Parámetro cj_cta_presta_debe no configurado, favor verificar')

        if ctahaber is None:
            raise ErrorValidacionExc('Parámetro cj_cta_presta_haber no configurado, favor verificar')

        itemconfidao = TItemConfigDao(self.dbsession)
        datos_cta_debe = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctadebe)
        datos_cta_haber = itemconfidao.get_detalles_ctacontable_by_code(ic_code=ctahaber)

        debedet = self.clone_formdet(formdet)
        debedet['dt_debito'] = 1
        debedet['dt_valor'] = numeros.roundm2(monto)
        debedet['cta_codigo'] = datos_cta_debe['ic_id']
        debedet['ic_clasecc'] = 'XC'
        detalles.append(debedet)

        haberdet = self.clone_formdet(formdet)
        haberdet['dt_debito'] = -1
        haberdet['dt_valor'] = numeros.roundm2(monto)
        haberdet['cta_codigo'] = datos_cta_haber['ic_id']
        haberdet['ic_clasecc'] = ''
        detalles.append(haberdet)

        formasiento['detalles'] = detalles

        trn_codigo_gen = tasientodao.crear_asiento(formcab=formasiento['formasiento'],
                                                   formref=formasiento['formref'],
                                                   usercrea=usercrea,
                                                   detalles=formasiento['detalles'],
                                                   update_datosref=False
                                                   )
        """
        trn_codigo_gen = tasientodao.crear_asiento_cxcp_fromref(formcab=formasiento['formasiento'],
                                                                formref=formasiento['formref'],
                                                                usercrea=usercrea,
                                                                detalles=formasiento['detalles'])
        """

        return trn_codigo_gen

    def create_from_referente(self, formtosave, usercrea):
        form = formtosave['form']
        formasiento = formtosave['formasiento']

        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)

        formasiento['formasiento']['trn_docpen'] = 'F'
        formdet = formasiento['formdet']
        detalles = []
        motivos = form['motivos']

        maindet = self.clone_formdet(formdet)
        maindet['dt_debito'] = form['dt_debito_main']
        maindet['dt_valor'] = form['monto']
        maindet['cta_codigo'] = form['cta_codigo_main']
        maindet['ic_clasecc'] = form['ic_clasecc']
        detalles.append(maindet)

        for motivo in motivos:
            auxdet = self.clone_formdet(formdet)
            auxdet['dt_debito'] = int(form['dt_debito_main']) * -1
            auxdet['dt_valor'] = motivo['dt_valor']
            auxdet['cta_codigo'] = motivo['cta_codigo']
            detalles.append(auxdet)

        formasiento['detalles'] = detalles

        trn_codigo_gen = tasientodao.crear_asiento_cxcp_fromref(formcab=formasiento['formasiento'],
                                                                formref=formasiento['formref'],
                                                                usercrea=usercrea,
                                                                detalles=formasiento['detalles'])
        return trn_codigo_gen

    def abonar_credito(self, dt_codcred, monto_abono):
        montoabodec = decimal.Decimal(monto_abono)
        if montoabodec is None or montoabodec <= 0:
            raise ErrorValidacionExc('Monto de abono incorrecto ({0}), no puede ser valores negativos o cero',
                                     format(monto_abono))

        tasicredito = self.dbsession.query(TAsicredito).filter(TAsicredito.dt_codigo == dt_codcred).first()
        if tasicredito is not None:
            cre_saldopen = tasicredito.cre_saldopen
            if cre_saldopen > 0:
                rmontoabo = numeros.roundm2(monto_abono)
                rsaldpen = numeros.roundm2(cre_saldopen)

                if rmontoabo > rsaldpen:
                    raise ErrorValidacionExc(
                        'El monto a abonar ({0}) es mayor al saldo pendiente ({1}), no es posible registrar'.format(
                            rmontoabo, rsaldpen))
                else:
                    newsaldopen = decimal.Decimal(tasicredito.cre_saldopen) - decimal.Decimal(monto_abono)
                    tasicredito.cre_saldopen = numeros.roundm2(newsaldopen)
                    self.dbsession.add(tasicredito)

        return tasicredito.cre_saldopen

    def anular_abono(self, dt_codcred, monto_abono_anular, monto_total_cred):
        tasicredito = self.dbsession.query(TAsicredito).filter(TAsicredito.dt_codigo == dt_codcred).first()
        if tasicredito is not None:
            cre_saldopen = tasicredito.cre_saldopen
            new_saldopen = cre_saldopen + decimal.Decimal(monto_abono_anular)
            new_saldopen_round = numeros.roundm2(new_saldopen)
            montototal_round = numeros.roundm2(monto_total_cred)
            if new_saldopen_round > montototal_round:
                raise ErrorValidacionExc(
                    'No es posible anular el abono para este crédito, el nuevo saldo({0}) supera el monto total del crédito ({1})'.format(
                        new_saldopen_round, montototal_round))
            tasicredito.cre_saldopen = new_saldopen
            self.dbsession.add(tasicredito)

    def get_datos_credito(self, cre_codigo):
        sql = """
        select cred.cre_codigo,
               cred.dt_codigo,
               cred.cre_fecini,
            cred.cre_fecven,
            cred.cre_intere,
            cred.cre_intmor,
            cred.cre_compro,
            cred.cre_codban,
            cred.cre_saldopen,
            detcred.dt_valor,
            detcred.cta_codigo,
            detcred.trn_codigo,
            cred.cre_tipo,                        
            ic.ic_clasecc,
               tasi.trn_compro,
               tasi.trn_fecha,
               tasi.trn_fecreg,
               tasi.trn_observ,
               per.per_id,
               per.per_nombres||' '||per.per_apellidos as referente,
               per.per_ciruc
               from tasicredito cred
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo 
        join tpersona per on tasi.per_codigo = per.per_id
        join titemconfig ic on detcred.cta_codigo = ic.ic_id 
        where cred.cre_codigo = {0}
        """.format(cre_codigo)

        tupla_desc = (
            'cre_codigo', 'dt_codigo', 'cre_fecini', 'cre_fecven', 'cre_intere', 'cre_intmor', 'cre_compro',
            'cre_codban', 'cre_saldopen', 'dt_valor', 'cta_codigo', 'trn_codigo', 'cre_tipo', 'ic_clasecc',
            'trn_compro', 'trn_fecha', 'trn_fecreg', 'trn_observ', 'per_id', 'referente', 'per_ciruc')

        return self.first(sql, tupla_desc)

    def get_total_deudas(self, per_codigo, clase):
        icclase = 'XC'
        if int(clase) == 2:
            icclase = 'XP'

        sql = """
                select 
                    sum(cred.cre_saldopen) as totaldeuda
                       from tasicredito cred
                join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
                join titemconfig ic on detcred.cta_codigo = ic.ic_id and ic.ic_clasecc = '{icclase}'
                join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo  
                and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
                join tpersona per on tasi.per_codigo = per.per_id and per.per_id = {per_codigo}
                """.format(icclase=icclase, per_codigo=per_codigo)
        totaldeuda = self.first_col(sql, 'totaldeuda')
        return self.type_json(totaldeuda)

    def listar(self, tipo, desde, hasta, filtro, sec_id):
        sqlfechas = ""
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sqlfechas = " and (tasi.trn_fecreg between '{0}' and '{1}' )".format(fechas.format_cadena_db(desde),
                                                                                 fechas.format_cadena_db(hasta))
        sqlfiltro = ' '
        if sec_id > 0:
            sqlfiltro = ' and tasi.sec_codigo = {0}'.format(sec_id)

        if cadenas.es_nonulo_novacio(filtro):
            filtroupper = cadenas.strip_upper(filtro)
            auxfiltroupper = '%'.join(filtroupper.split(' '))
            filtrocedula = " ( ( (per.per_nombres || ' ' || coalesce(per.per_apellidos, '')) like '%{0}%' ) or (per.per_ciruc like '%{0}%') ) ".format(
                auxfiltroupper)
            sqlfiltro += " and {0} ".format(filtrocedula)

        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='cxcp', tipo=tipo, sqlfiltro=sqlfiltro, sqlfechas=sqlfechas)

        # Totalizar
        totales = {'credito': 0.0, 'saldopend': 0.0}
        for item in data['data']:
            totales['credito'] += item['dt_valor']
            totales['saldopend'] += item['cre_saldopen']

        totales['credito'] = numeros.roundm2(totales['credito'])
        totales['saldopend'] = numeros.roundm2(totales['saldopend'])

        return data, totales

    def listar_creditos(self, per_codigo, solo_pendientes=True, clase=1, sec_codigo=0):
        tracodin = "1,2"
        if int(clase) == 2:
            tracodin = "7"

        sqlpendientes = " "
        if solo_pendientes:
            sqlpendientes = " and cred.cre_saldopen>0"

        sql = """
        select cred.cre_codigo,
               cred.dt_codigo,
               cred.cre_fecini,
            cred.cre_fecven,
            cred.cre_intere,
            cred.cre_intmor,
            cred.cre_compro,
            cred.cre_codban,
            cred.cre_saldopen,
            detcred.dt_valor,
            detcred.trn_codigo,
               tasi.trn_compro,
               tasi.trn_fecha,
               tasi.trn_fecreg,
               tasi.trn_observ,
               per.per_id,
               per.per_nombres||' '||per.per_apellidos as referente,
               per.per_ciruc
               from tasicredito cred
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo and tasi.trn_pagpen = 'F' 
             and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
        join tpersona per on tasi.per_codigo = per.per_id and per.per_id = {per_codigo}
        where cred.cre_tipo = {cre_tipo} {sqlpend} and tasi.sec_codigo = {sec_codigo}
        order by tasi.trn_fecreg desc
        """.format(tracodin=tracodin, per_codigo=per_codigo, cre_tipo=clase, sqlpend=sqlpendientes,
                   sec_codigo=sec_codigo)

        tupla_desc = (
            'cre_codigo', 'dt_codigo', 'cre_fecini', 'cre_fecven', 'cre_intere', 'cre_intmor', 'cre_compro',
            'cre_codban', 'cre_saldopen', 'dt_valor', 'trn_codigo', 'trn_compro', 'trn_fecha', 'trn_fecreg',
            'trn_observ', 'per_id', 'referente', 'per_ciruc')

        sumas = {
            'totalcred': 0.0,
            'totalsalpend': 0.0
        }

        items = self.all(sql, tupla_desc)

        if items is not None and len(items) > 0:
            for item in items:
                sumas['totalcred'] += item['dt_valor']
                sumas['totalsalpend'] += item['cre_saldopen']

        return items, sumas

    def find_datoscred_intransacc(self, trn_codigo):
        sql = """
        select det.dt_codigo, det.dt_valor, cred.cre_codigo from tasidetalle det
        join tasicredito cred on det.dt_codigo = cred.dt_codigo
        join tasiento asi on det.trn_codigo = asi.trn_codigo and asi.trn_docpen = 'F' and asi.trn_valido = 0
        where asi.trn_codigo = {0}
        """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'dt_valor', 'cre_codigo')
        return self.first(sql, tupla_desc)

    def get_cre_tipo(self, ic_clasecc):
        cre_tipo = 0
        if ic_clasecc == 'XC':
            cre_tipo = 1
        if ic_clasecc == 'XP':
            cre_tipo = 2

        return cre_tipo

    def get_form_asi(self, dt_codigo, trn_fecreg, monto_cred, cre_tipo):
        formcre = {
            'dt_codigo': dt_codigo,
            'cre_fecini': trn_fecreg,
            'cre_fecven': None,
            'cre_intere': 0.0,
            'cre_intmor': 0.0,
            'cre_codban': None,
            'cre_saldopen': monto_cred,
            'cre_tipo': cre_tipo
        }
        return formcre

    def is_clasecc_cred(self, ic_clasecc):

        return ic_clasecc == 'XC' or ic_clasecc == 'XP'

    def find_byid(self, cre_codigo):
        return self.dbsession.query(TAsicredito).filter(TAsicredito.cre_codigo == cre_codigo).first()

    def upd_cre_saldopen(self, cre_codigo, cre_saldopen):
        tasicredito = self.find_byid(cre_codigo=cre_codigo)
        if tasicredito is not None:
            tasicredito.cre_saldopen = cre_saldopen
            self.dbsession.add(tasicredito)
