# coding: utf-8
"""
Fecha de creacion 5/3/21
@autor: mjapon
"""
import logging
from datetime import datetime
from functools import reduce
from itertools import groupby
from operator import itemgetter

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc, SecuenciaEnUsoExc
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasidetimp.tasidetimp_model import TAsidetimp
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento
from fusayrepo.logica.fusay.ttransaccimp.ttransaccimp_dao import TTransaccImpDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.logica.fusay.ttransaccrel.ttransaccrel_dao import TTransaccRelDao
from fusayrepo.utils import numeros, ctes, cadenas, fechas

log = logging.getLogger(__name__)


class AuxLogicAsiDao(BaseDao):

    @staticmethod
    def chk_sum_debe_haber(vdebehaber):
        itemsdebe = map(lambda x: float(x['dt_valor']), filter(lambda item: item['dt_debito'] == 1, vdebehaber))
        itemshaber = map(lambda x: float(x['dt_valor']), filter(lambda item: item['dt_debito'] == -1, vdebehaber))

        sumadebe = reduce(lambda a, b: a + b, itemsdebe, 0.0)
        sumahaber = reduce(lambda a, b: a + b, itemshaber, 0.0)

        sumadeberound = numeros.roundm2(sumadebe)
        sumahaberound = numeros.roundm2(sumahaber)
        if sumadeberound != sumahaberound:
            raise ErrorValidacionExc(
                'La suma del debe ({0}) y el haber({1}) no coinciden, favor verificar'.format(sumadeberound,
                                                                                              sumahaberound))

    def save_tasidet_fact(self, detalle, trn_codigo, tasiper_codigo):
        tasidetalle = TAsidetalle()
        per_cod_det = int(detalle['per_codigo'])
        if per_cod_det == 0:
            per_cod_det = tasiper_codigo

        tasidetalle.dt_codigo = None
        tasidetalle.trn_codigo = trn_codigo
        tasidetalle.cta_codigo = detalle['cta_codigo']
        tasidetalle.art_codigo = detalle['art_codigo']
        tasidetalle.per_codigo = per_cod_det
        tasidetalle.pry_codigo = detalle['pry_codigo']
        tasidetalle.dt_cant = detalle['dt_cant']
        tasidetalle.dt_precio = detalle['dt_precio']
        tasidetalle.dt_debito = detalle['dt_debito']
        tasidetalle.dt_preref = detalle['dt_preref']
        tasidetalle.dt_decto = detalle['dt_decto']
        tasidetalle.dt_valor = detalle['dt_valor']
        tasidetalle.dt_dectogen = detalle['dt_dectogen']
        tasidetalle.dt_tipoitem = ctes.DT_TIPO_ITEM_DETALLE
        tasidetalle.dt_valdto = detalle['dt_valdto']
        tasidetalle.dt_valdtogen = detalle['dt_valdtogen']
        tasidetalle.dt_codsec = detalle['dt_codsec']

        self.dbsession.add(tasidetalle)
        self.dbsession.flush()
        dt_codigo = tasidetalle.dt_codigo

        tasidetimp = TAsidetimp()
        tasidetimp.dai_codigo = None
        tasidetimp.dt_codigo = dt_codigo
        tasidetimp.dai_imp0 = detalle['dai_imp0'] if cadenas.es_nonulo_novacio(detalle['dai_imp0']) else None
        tasidetimp.dai_impg = detalle['dai_impg'] if cadenas.es_nonulo_novacio(detalle['dai_impg']) else None
        tasidetimp.dai_ise = detalle['dai_ise'] if cadenas.es_nonulo_novacio(detalle['dai_ise']) else None
        tasidetimp.dai_ice = detalle['dai_ice'] if cadenas.es_nonulo_novacio(detalle['dai_ice']) else None

        self.dbsession.add(tasidetimp)

        return dt_codigo

    def save_tasidet_imp(self, trn_codigo, per_codigo, impuesto, sec_codigo):
        detimpuesto = TAsidetalle()
        detimpuesto.trn_codigo = trn_codigo
        detimpuesto.per_codigo = per_codigo
        detimpuesto.cta_codigo = impuesto['cta_codigo']
        detimpuesto.art_codigo = 0
        detimpuesto.dt_debito = impuesto['dt_debito']
        detimpuesto.dt_valor = impuesto['dt_valor']
        detimpuesto.dt_tipoitem = ctes.DT_TIPO_ITEM_IMPUESTO
        detimpuesto.dt_codsec = sec_codigo
        self.dbsession.add(detimpuesto)

    def save_tasidet_pago(self, trn_codigo, per_codigo, pago):
        detpago = TAsidetalle()
        detpago.trn_codigo = trn_codigo
        detpago.per_codigo = per_codigo
        detpago.cta_codigo = pago['cta_codigo']
        detpago.art_codigo = 0
        detpago.dt_debito = pago['dt_debito']
        detpago.dt_valor = float(pago['dt_valor'])
        detpago.dt_tipoitem = ctes.DT_TIPO_ITEM_PAGO
        detpago.dt_codsec = pago['dt_codsec']

        self.dbsession.add(detpago)
        self.dbsession.flush()
        return detpago.dt_codigo

    def save_tasidet_asiento(self, trn_codigo, per_codigo, detalle, roundvalor=True):
        detasiento = TAsidetalle()
        detasiento.trn_codigo = trn_codigo
        detasiento.per_codigo = per_codigo
        detasiento.cta_codigo = detalle['cta_codigo']
        detasiento.art_codigo = 0
        detasiento.dt_debito = detalle['dt_debito']
        detasiento.dt_tipoitem = ctes.DT_TIPO_ITEM_DETASIENTO
        detasiento.dt_codsec = detalle['dt_codsec']

        if roundvalor:
            detasiento.dt_valor = numeros.roundm2(float(detalle['dt_valor']))
        else:
            detasiento.dt_valor = float(detalle['dt_valor'])

        self.dbsession.add(detasiento)
        self.dbsession.flush()
        return detasiento.dt_codigo

    def existe_doc_valido(self, trn_compro, tra_codigo, sec_codigo):
        sql = """
        select count(*) as cuenta from tasiento where trn_compro = '{0}' and tra_codigo = {1}         
        and trn_docpen = 'F' and trn_valido = 0 and sec_codigo = {2}
        """.format(cadenas.strip(trn_compro), tra_codigo, sec_codigo)

        return self.first_col(sql, 'cuenta') > 0

    @staticmethod
    def _get_trn_compro(estabptoemi, secuencia):
        return "{0}{1}".format(estabptoemi, str(secuencia).zfill(ctes.LEN_DOC_SECUENCIA))

    def aux_chk_existe_doc_valid(self, formcab, trn_compro, tra_codigo):
        if formcab['trn_docpen'] == 'F':
            if self.existe_doc_valido(trn_compro, tra_codigo=tra_codigo, sec_codigo=formcab['sec_codigo']):
                raise SecuenciaEnUsoExc('Ya existe un comprobante registrado con el número: {0}'.format(trn_compro))

    def aux_chk_existe_doc_valid_ref(self, formcab, trn_compro, tra_codigo, per_ciruc):
        if formcab['trn_docpen'] == 'F':
            if self.existe_doc_compra_valido(trn_compro, tra_codigo=tra_codigo, per_ciruc=per_ciruc):
                raise ErrorValidacionExc(
                    'Ya existe un comprobante registrado con el número: {0} para el referente {1}'.format(trn_compro,
                                                                                                          per_ciruc))

    def existe_doc_compra_valido(self, trn_compro, tra_codigo, per_ciruc):
        sql = """
                select count(*) as cuenta from tasiento asi
                join tpersona per on asi.per_codigo = per.per_id and per.per_ciruc = '{2}' 
                 where trn_compro = '{0}' and tra_codigo = {1} 
                and trn_docpen = 'F' and trn_valido = 0
                """.format(cadenas.strip(trn_compro), tra_codigo, cadenas.strip_upper(per_ciruc))
        return self.first_col(sql, 'cuenta') > 0

    def aux_gen_trn_compro(self, formcab, tps_codigo, secuencia, tra_codigo):
        transaccpdv_dao = TTransaccPdvDao(self.dbsession)
        estabptoemi = formcab['estabptoemi']
        trn_compro = self._get_trn_compro(estabptoemi, secuencia)
        try:
            self.aux_chk_existe_doc_valid(formcab, trn_compro, tra_codigo)
        except SecuenciaEnUsoExc as ex:
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)
            formcab['secuencia'] = int(secuencia) + 1
            return self.aux_gen_trn_compro(formcab, tps_codigo, int(secuencia) + 1, tra_codigo)

        return trn_compro

    def aux_set_datos_secuencia(self, tasiento, formcab, per_codigo, sec_codigo):
        transaccpdv_dao = TTransaccPdvDao(self.dbsession)
        tps_codigo = formcab['tps_codigo']
        secuencia = formcab['secuencia']
        tasiento.tra_codigo = formcab['tra_codigo']
        trn_compro = self.aux_gen_trn_compro(formcab, tps_codigo, secuencia, tasiento.tra_codigo)
        tasiento.trn_compro = trn_compro
        tasiento.trn_docpen = 'F'
        tasiento.per_codigo = per_codigo
        tasiento.sec_codigo = sec_codigo

        if tps_codigo is not None and tps_codigo > 0:
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

    def aux_set_datos_tasiento(self, usercrea, per_codigo, formcab, per_ciruc='', gen_secuencia=True):
        secuencia = formcab['secuencia']
        tra_codigo = formcab['tra_codigo']
        sec_codigo = formcab['sec_codigo']
        tps_codigo = formcab['tps_codigo']

        transaccpdv_dao = TTransaccPdvDao(self.dbsession)

        if int(tra_codigo) == ctes.TRA_COD_FACT_COMPRA:
            trn_compro = secuencia
            self.aux_chk_existe_doc_valid_ref(formcab, trn_compro, tra_codigo, per_ciruc)
        else:
            trn_compro = self._get_trn_compro(formcab['estabptoemi'], secuencia)
            try:
                self.aux_chk_existe_doc_valid(formcab, trn_compro, tra_codigo)
            except SecuenciaEnUsoExc as ex:
                if tps_codigo is not None and tps_codigo > 0 and gen_secuencia:
                    transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)
                    trn_compro = self.aux_gen_trn_compro(formcab, tps_codigo, int(secuencia) + 1, tra_codigo)
        secuencia = formcab['secuencia']
        trn_docpen = formcab['trn_docpen']
        trn_pagpen = formcab['trn_pagpen']
        trn_observ = formcab['trn_observ']
        tdv_codigo = formcab['tdv_codigo']
        fol_codigo = int(formcab['fol_codigo'])
        trn_tipcom = formcab['trn_tipcom']
        trn_suscom = formcab['trn_suscom']
        per_codres = None

        if int(formcab['tra_codigo']) == ctes.TRA_COD_ASI_CONTABLE:
            if not cadenas.es_nonulo_novacio(trn_observ):
                raise ErrorValidacionExc('Debe ingresar la observación del asiento contable')

        tasiento = TAsiento()
        tasiento.dia_codigo = formcab['dia_codigo']
        tasiento.trn_fecreg = fechas.parse_cadena(formcab['trn_fecreg'])
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = datetime.now()
        tasiento.trn_valido = 0
        tasiento.trn_docpen = trn_docpen
        tasiento.trn_pagpen = trn_pagpen
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = per_codigo
        tasiento.tra_codigo = formcab['tra_codigo']
        tasiento.us_id = usercrea
        tasiento.trn_observ = trn_observ
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = fol_codigo
        tasiento.trn_tipcom = trn_tipcom
        tasiento.trn_suscom = trn_suscom
        tasiento.per_codres = per_codres
        tasiento.trn_impref = formcab['trn_impref']

        if tps_codigo is not None and tps_codigo > 0 and gen_secuencia:
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        return tasiento

    def get_impuestos(self, tra_codigo, sec_codigo, totales):
        ttransaccimpdao = TTransaccImpDao(self.dbsession)
        configtransaccimp = ttransaccimpdao.get_config(tra_codigo=tra_codigo, sec_codigo=sec_codigo)

        impuestos = []
        if configtransaccimp is not None and totales is not None:
            ivaval = totales['iva']
            if ivaval is not None and ivaval > 0:
                impuestos.append({
                    'cta_codigo': configtransaccimp['tra_impg'],
                    'dt_debito': configtransaccimp['tra_signo'],
                    'dt_valor': ivaval
                })

        return impuestos

    @staticmethod
    def totalizar_facturas(listafact):
        totales = {'efectivo': 0.0, 'credito': 0.0, 'saldopend': 0.0, 'total': 0.0}
        for item in listafact:
            totales['efectivo'] += item['efectivo']
            totales['credito'] += item['credito']
            totales['saldopend'] += item['saldopend']
            totales['total'] += item['total']

        totales['efectivo'] = numeros.roundm2(totales['efectivo'])
        totales['credito'] = numeros.roundm2(totales['credito'])
        totales['saldopend'] = numeros.roundm2(totales['saldopend'])
        totales['total'] = numeros.roundm2(totales['total'])
        return totales

    def save_dets_imps_fact(self, detalles, tasiento, totales, valdebehaber):
        for detalle in detalles:
            self.save_tasidet_fact(detalle=detalle, trn_codigo=tasiento.trn_codigo,
                                   tasiper_codigo=tasiento.per_codigo)
            valdebehaber.append({'dt_debito': detalle['dt_debito'], 'dt_valor': detalle['dt_valor']})

        impuestos = self.get_impuestos(tra_codigo=tasiento.tra_codigo, sec_codigo=tasiento.sec_codigo, totales=totales)
        for impuesto in impuestos:
            self.save_tasidet_imp(trn_codigo=tasiento.trn_codigo, per_codigo=tasiento.per_codigo, impuesto=impuesto,
                                  sec_codigo=tasiento.sec_codigo)
            valdebehaber.append({'dt_debito': impuesto['dt_debito'], 'dt_valor': impuesto['dt_valor']})

        return valdebehaber

    def gen_nota_credito(self, trn_codfactura, alm_codigo, sec_codigo, tdv_codigo, usercrea):

        sql = ("select sec_codigo,per_codigo,tdv_codigo,trn_impref, trn_compro "
               "from tasiento where trn_codigo = {0}").format(trn_codfactura)
        tupla_desc = ('sec_codigo', 'per_codigo', 'tdv_codigo', 'trn_impref', 'trn_compro')
        datosfact = self.first(sql, tupla_desc)

        transaccpdv_dao = TTransaccPdvDao(self.dbsession)

        resptoemi = transaccpdv_dao.get_estabptoemi_secuencia(alm_codigo=alm_codigo,
                                                              tra_codigo=ctes.TRA_COD_NOTA_CREDITO,
                                                              tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)
        estabptoemi = resptoemi['estabptoemi']
        secuencia = resptoemi['secuencia']
        tps_codigo = resptoemi['tps_codigo']

        trn_compro = self._get_trn_compro(estabptoemi, secuencia)
        tra_codigo = ctes.TRA_COD_NOTA_CREDITO
        auxformcab = {'trn_docpen': 'F', 'sec_codigo': sec_codigo, 'estabptoemi': estabptoemi}
        try:
            self.aux_chk_existe_doc_valid(auxformcab, trn_compro, tra_codigo)
        except SecuenciaEnUsoExc as ex:
            if tps_codigo is not None and tps_codigo > 0:
                transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)
                trn_compro = self.aux_gen_trn_compro(auxformcab, tps_codigo, int(secuencia) + 1, tra_codigo)

        tasiento = TAsiento()

        tasiento.dia_codigo = 0
        tasiento.trn_fecreg = datetime.now()
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = datetime.now()
        tasiento.trn_valido = 0
        tasiento.trn_docpen = 'F'
        tasiento.trn_pagpen = 'F'
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = datosfact['per_codigo']
        tasiento.tra_codigo = tra_codigo
        tasiento.us_id = usercrea
        tasiento.trn_observ = ''
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = 0
        tasiento.trn_tipcom = None
        tasiento.trn_suscom = None
        tasiento.per_codres = None
        tasiento.trn_impref = datosfact['trn_impref']

        self.dbsession.add(tasiento)
        self.dbsession.flush()
        trn_cod_gen = tasiento.trn_codigo

        sql = """select
        dt_codigo, 
        cta_codigo,
        art_codigo,
        per_codigo,
        pry_codigo,
        dt_cant,
        dt_precio,
        dt_debito,
        dt_preref,
        dt_decto,
        dt_valor,
        dt_dectogen,
        dt_tipoitem,
        dt_valdto,
        dt_valdtogen,
        dt_codsec from tasidetalle where trn_codigo = {0}""".format(trn_codfactura)
        tupla_desc = ('dt_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant', 'dt_precio',
                      'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem', 'dt_valdto',
                      'dt_valdtogen', 'dt_codsec')
        detalles = self.all(sql, tupla_desc)
        dt_codigos = ','.join([str(det['dt_codigo']) for det in detalles])

        sql = ("select dt_codigo, dai_imp0, dai_impg, dai_ise, dai_ice from "
               "tasidetimp where dt_codigo in ({0})").format(dt_codigos)

        tupla_desc = ('dt_codigo', 'dai_imp0', 'dai_impg', 'dai_ise', 'dai_ice')
        dt_impuestos = self.all(sql, tupla_desc)

        lista_ordenada = sorted(dt_impuestos, key=itemgetter('dt_codigo'))

        impuestos_map = {k: list(v) for k, v in groupby(lista_ordenada, key=itemgetter('dt_codigo'))}
        for det in detalles:
            detalleit = TAsidetalle()
            pry_codigo = None
            if cadenas.es_nonulo_novacio(det['pry_codigo']):
                pry_codigo = det['pry_codigo']
            detalleit.trn_codigo = trn_cod_gen
            detalleit.cta_codigo = det['cta_codigo']
            detalleit.art_codigo = det['art_codigo']
            detalleit.per_codigo = det['per_codigo']
            detalleit.pry_codigo = pry_codigo
            detalleit.dt_cant = det['dt_cant']
            detalleit.dt_precio = det['dt_precio']
            detalleit.dt_debito = det['dt_debito']
            detalleit.dt_preref = det['dt_preref']
            detalleit.dt_decto = det['dt_decto']
            detalleit.dt_valor = det['dt_valor']
            detalleit.dt_dectogen = det['dt_dectogen']
            detalleit.dt_tipoitem = det['dt_tipoitem']
            detalleit.dt_valdto = det['dt_valdto']
            detalleit.dt_valdtogen = det['dt_valdtogen']
            detalleit.dt_codsec = det['dt_codsec']
            self.dbsession.add(detalleit)
            self.dbsession.flush()
            new_dt_cod = detalleit.dt_codigo
            if det['dt_codigo'] in impuestos_map:
                impuestos = impuestos_map[det['dt_codigo']]
                for imp in impuestos:
                    tasidetimp = TAsidetimp()
                    tasidetimp.dt_codigo = new_dt_cod
                    tasidetimp.dai_imp0 = imp['dai_imp0'] if cadenas.es_nonulo_novacio(imp['dai_imp0']) else None
                    tasidetimp.dai_impg = imp['dai_impg'] if cadenas.es_nonulo_novacio(imp['dai_impg']) else None
                    tasidetimp.dai_ise = imp['dai_ise'] if cadenas.es_nonulo_novacio(imp['dai_ise']) else None
                    tasidetimp.dai_ice = imp['dai_ice'] if cadenas.es_nonulo_novacio(imp['dai_ice']) else None
                    self.dbsession.add(tasidetimp)

        transaccreldao = TTransaccRelDao(self.dbsession)
        transaccreldao.crear_nota_credito(trn_cod_gen, trn_codfactura, usercrea)
        return trn_cod_gen
