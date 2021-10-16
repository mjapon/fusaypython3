# coding: utf-8
"""
Fecha de creacion 5/19/21
@autor: mjapon
"""
import logging
from datetime import datetime

import simplejson

from fusayrepo.logica.aguap.tagp_contrato.tagp_contrato_dao import TAgpContratoDao
from fusayrepo.logica.aguap.tagp_lectomed.tagp_lectomed_dao import LectoMedAguaDao
from fusayrepo.logica.aguap.tagp_models import TagpPago
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.utils import numeros, fechas, cadenas
from fusayrepo.utils.jsonutil import SimpleJsonUtil

log = logging.getLogger(__name__)


class TagpCobroDao(BaseDao):

    @staticmethod
    def get_form():
        steps = [
            {'label': 'Buscar referente'},
            {'label': 'Seleccionar medidor'},
            {'label': 'Registra pago'}
        ]
        form = {
            'referente': {},
            'datosmed': {},
            'obs': '',
            'lecturas': [],
            'montos': {}
        }

        return {
            'form': form,
            'steps': steps
        }

    def get_datos_pago(self, trn_codigo):

        sql = "select  pg_id, lmd_id, pg_estado, pg_usercrea, pg_fechacrea, trn_codigo, pg_json from tagp_pago where trn_codigo = {0}".format(
            trn_codigo)

        tupla_desc = ('pg_id', 'lmd_id', 'pg_estado', 'pg_usercrea', 'pg_fechacrea', 'trn_codigo', 'pg_json')

        datospago = self.first(sql, tupla_desc)
        if datospago is not None:
            pg_json = datospago['pg_json']
            if cadenas.es_nonulo_novacio(pg_json):
                datospago['pg_json_obj'] = simplejson.loads(pg_json)

        return datospago

    def is_lecto_with_pago(self, lmd_id):
        sql = """
        select count(*) as cuenta from tagp_pago where lmd_id = {0} and pg_estado = 1
        """.format(lmd_id)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def get_calculo_pago(self, lectoids, alm_codigo, tdv_codigo, sec_codigo):
        lectomedagua_dao = LectoMedAguaDao(self.dbsession)
        contratodao = TAgpContratoDao(self.dbsession)
        itemconfigdao = TItemConfigDao(self.dbsession)
        tparamsdao = TParamsDao(self.dbsession)

        agp_diacobro = tparamsdao.get_param_value('agp_diacobro')
        agp_permeses = tparamsdao.get_param_value('agp_permeses')
        agp_multa = tparamsdao.get_param_value('agp_multa')
        agp_pordescte = tparamsdao.get_param_value('agp_pordescte')
        agp_tracod = tparamsdao.get_param_value('agp_tracod')
        agp_iccomavil = tparamsdao.get_param_value('agp_iccomavil')
        # agp_fecinicobrotarfbase = tparamsdao.get_param_value('agp_fecinicbtfb')
        agp_numdiasmulta = tparamsdao.get_param_value('agp_numdiasmulta')

        if agp_diacobro is None:
            raise ErrorValidacionExc('El parámetro agp_diacobro no está configurado, favor verificar')
        if agp_permeses is None:
            raise ErrorValidacionExc('El parámetro agp_permeses no está configurado, favor verificar')
        if agp_multa is None:
            raise ErrorValidacionExc('El parámetro agp_multa no está configurado, favor verificar')
        if agp_pordescte is None:
            raise ErrorValidacionExc('El parámetro agp_pordescte no está configurado, favor verificar')
        if agp_tracod is None:
            raise ErrorValidacionExc('El parámetro agp_tracod no está configurado, favor verificar')
        if agp_iccomavil is None:
            raise ErrorValidacionExc('El parámetro agp_iccomavil no está configurado, favor verificar')
        # if agp_fecinicobrotarfbase is None:
        #    raise ErrorValidacionExc('El parámetro agp_fecinicbtfb no está configurado, favor verificar')
        if agp_numdiasmulta is None:
            raise ErrorValidacionExc('El parámetro agp_numdiasmulta no está configurado, favor verificar')

        ids = ','.join(['{0}'.format(it) for it in lectoids])
        lecturas = lectomedagua_dao.get_datos_lectura(ids=ids)

        costobase = 0.0
        costoexceso = 0.0
        descuento = 0.0
        consumo_base = 0
        consumo_exceso = 0
        tarifaexceso = 0.0
        multa = 0.0
        total = 0.0
        comision_mavil = 0.0

        fecha_actual = datetime.now()
        fecha_consumo = ''
        fecha_max_pago = ''

        tasientodao = TasientoDao(self.dbsession)
        formcab = tasientodao.get_form_cabecera(tra_codigo=agp_tracod, alm_codigo=alm_codigo, sec_codigo=sec_codigo,
                                                tdv_codigo=tdv_codigo)

        is_tercera_edad = False

        ic_comavil = itemconfigdao.get_detalles_prod(ic_id=agp_iccomavil)

        pagosdet = {}
        for lectura in lecturas:
            lmd_id = lectura['lmd_id']
            pg_id = lectura['pg_id']
            consumo = float(lectura['lmd_consumo'])
            lmd_anio = lectura['lmd_anio']
            lmd_mes = lectura['lmd_mes']

            # Obtener el ultimo dia del mes
            dia_cobro = fechas.get_maxday_month(int(agp_diacobro), lmd_anio, lmd_mes)

            fecha_consumo_str = '01/{0}/{1}'.format(lmd_mes, lmd_anio)
            fecha_consumo = fechas.parse_cadena(fecha_consumo_str)

            fecha_cobro_str = '{0}/{1}/{2}'.format(dia_cobro, lmd_mes, lmd_anio)
            fecha_cobro = fechas.parse_cadena(fecha_cobro_str)
            fecha_max_pago = fechas.sumar_dias(fecha_cobro, int(agp_numdiasmulta))
            # fecha_max_pago = fechas.sumar_meses(fecha_consumo, int(agp_permeses)).replace(day=int(agp_diacobro))

            # Cambiar logica para aplicacion de multa la multas e d
            aplica_multa = False
            if fecha_actual.date() > fecha_max_pago.date():
                aplica_multa = True

            if pg_id == 0:
                datoscontrato = contratodao.find_by_mdg_id(mdg_id=lectura['mdg_id'])
                if datoscontrato is None:
                    raise ErrorValidacionExc(
                        'No pude obtener los datos del contrato (cod:{0})'.format(lectura['mdg_id']))

                trf_id = datoscontrato['trf_id']
                datostarifa = contratodao.get_datos_tarifa(trf_id=trf_id)
                if datostarifa is None:
                    raise ErrorValidacionExc(
                        'No pude obtener datos de la tarifa (cod:{0})'.format(trf_id))

                trf_base = datostarifa['trf_base']
                consumo_exceso_it = 0
                consumo_base_it = consumo
                if consumo > trf_base:
                    consumo_exceso_it = numeros.roundm2(consumo - trf_base)
                    consumo_base_it = trf_base

                consumo_base += consumo_base_it
                consumo_exceso += consumo_exceso_it

                """
                tarifaexceso = 0.0
                if consumo_exceso_it > 0:
                    datostarf_exceso = contratodao.get_tarifa_exceso(trf_id=trf_id, consumo=consumo_exceso)
                    if datostarf_exceso is None:
                        raise ErrorValidacionExc(
                            'No se ha configurado el costo por exceso de consumo (trf:{0})'.format(trf_id))

                    tarifaexceso = datostarf_exceso['etr_costo']
                """

                datosprod = itemconfigdao.get_detalles_prod(ic_id=datoscontrato['ic_id'])
                icdp_precioventa = datosprod['icdp_precioventa']

                cna_teredad = datoscontrato['cna_teredad']
                cna_discapacidad = datoscontrato['cna_discapacidad']

                costoexceso_item = 0
                if consumo_exceso_it <= 5:
                    costoexceso_item = numeros.roundm2(consumo_exceso_it * 0.25)
                else:
                    resto = consumo_exceso_it
                    itercosto = 0.25
                    while resto > 5:
                        costoexceso_item += numeros.roundm2(5 * itercosto)
                        resto = resto - 5
                        itercosto += 0.05

                    if resto > 0:
                        costoexceso_item += numeros.roundm2(resto * itercosto)

                # costoexceso_item = numeros.roundm2(consumo_exceso_it * tarifaexceso)
                costoexceso += costoexceso_item
                descuento_it = 0
                multa_it = 0
                if cna_teredad or cna_discapacidad:
                    is_tercera_edad = True
                    descuento_it = numeros.roundm2(float(agp_pordescte) * icdp_precioventa)
                if aplica_multa:
                    multa_it += float(agp_multa)

                total_it = icdp_precioventa + costoexceso_item - descuento_it + multa_it
                descuento += descuento_it
                multa += multa_it
                total += numeros.roundm2(total_it)

                aplica_costobase = True
                # if fechas.es_fecha_a_mayor_o_igual_fecha_b(fecha_consumo_str, agp_fecinicobrotarfbase):
                #    aplica_costobase = True

                if aplica_costobase:
                    costobase += icdp_precioventa

                pagosdet[lmd_id] = {
                    'costobase': icdp_precioventa if aplica_costobase else 0.0,
                    'costoexceso': costoexceso_item,
                    'descuento': descuento_it,
                    'multa': multa_it
                }

        comision_mavil = ic_comavil['icdp_precioventa']
        if is_tercera_edad:
            comision_mavil = comision_mavil - (comision_mavil * float(agp_pordescte))

        comavil_round = numeros.roundm2(comision_mavil * len(lecturas))
        total += comavil_round

        return {
            'costobase': costobase,
            'tarifaexceso': tarifaexceso,
            'costoexceso': costoexceso,
            'descuento': descuento,
            'consumo_base': consumo_base,
            'consumo_exceso': consumo_exceso,
            'fecha_consumo': fechas.parse_fecha(fecha_consumo),
            'fecha_max_pago': fechas.parse_fecha(fecha_max_pago),
            'fecha_actual': fechas.parse_fecha(fecha_actual),
            'multa': multa,
            'total': total,
            'formcab': formcab,
            'pagosdet': pagosdet,
            'comision_mavil': comavil_round
        }

    def aux_get_det(self, sec_codigo, datosprod, dt_debito, dt_valor):
        tasientodao = TasientoDao(self.dbsession)
        formdet = tasientodao.get_form_detalle(sec_codigo=sec_codigo)
        formdet['cta_codigo'] = datosprod['icdp_modcontab']
        formdet['art_codigo'] = datosprod['ic_id']
        formdet['dt_precio'] = dt_valor
        formdet['dt_debito'] = dt_debito
        formdet['dt_valor'] = dt_valor
        formdet['dai_impg'] = 0.0
        return formdet

    def crear(self, form, user_crea, sec_codigo):
        referente = form['referente']
        # medidor = form['datosmed']
        obs = form['obs']
        lecturas = form['lecturas']
        montos = form['montos']

        formcab = montos['formcab']
        formcab['trn_observ'] = obs
        pagosdet = montos['pagosdet']
        comision_mavil = montos['comision_mavil']

        lectomedagua_dao = LectoMedAguaDao(self.dbsession)
        ids = ','.join(['{0}'.format(it) for it in lecturas])
        lecturas = lectomedagua_dao.get_datos_lectura(ids=ids)

        tasientodao = TasientoDao(self.dbsession)
        transacpagodao = TTransaccPagoDao(self.dbsession)

        tparamsdao = TParamsDao(self.dbsession)
        agp_icexceso = tparamsdao.get_param_value('agp_icexceso')
        agp_icmulta = tparamsdao.get_param_value('agp_icmulta')
        agp_iccomavil = tparamsdao.get_param_value('agp_iccomavil')

        if agp_icexceso is None:
            raise ErrorValidacionExc('El parámetro agp_icexceso no está configurado, favor verificar')

        if agp_icmulta is None:
            raise ErrorValidacionExc('El parámetro agp_icmulta no está configurado, favor verificar')

        if agp_iccomavil is None:
            raise ErrorValidacionExc('El parámetro agp_iccomavil no está configurado, favor verificar')

        itemconfigdao = TItemConfigDao(self.dbsession)

        contratodao = TAgpContratoDao(self.dbsession)
        formas_pago = transacpagodao.get_formas_pago(tra_codigo=formcab['tra_codigo'], sec_id=sec_codigo)
        fpago_efectivo = None
        for it in formas_pago:
            ic_clasecc = it['ic_clasecc']
            if ic_clasecc == 'E':
                fpago_efectivo = it

        pago_efectivo = tasientodao.get_form_pago()

        pago_efectivo['dt_debito'] = fpago_efectivo['dt_debito']
        pago_efectivo['cta_codigo'] = fpago_efectivo['cta_codigo']
        pago_efectivo['dt_valor'] = montos['total']
        pago_efectivo['ic_clasecc'] = fpago_efectivo['ic_clasecc']

        pagos = []
        detalles = []

        pagos.append(pago_efectivo)

        dt_debito_det = fpago_efectivo['dt_debito'] * -1
        totales = {
            'total': montos['total'],
            'iva': 0.0
        }

        for lectura in lecturas:
            lmd_id = lectura['lmd_id']
            pagodet = pagosdet[str(lmd_id)]
            pg_id = lectura['pg_id']
            if pg_id == 0:
                datoscontrato = contratodao.find_by_mdg_id(mdg_id=lectura['mdg_id'])
                if datoscontrato is None:
                    raise ErrorValidacionExc(
                        'No pude obtener los datos del contrato (cod:{0})'.format(lectura['mdg_id']))

                trf_id = datoscontrato['trf_id']
                datostarifa = contratodao.get_datos_tarifa(trf_id=trf_id)
                if datostarifa is None:
                    raise ErrorValidacionExc(
                        'No pude obtener datos de la tarifa (cod:{0})'.format(trf_id))

                datosprod = itemconfigdao.get_detalles_prod(ic_id=datostarifa['ic_id'])
                formdet = tasientodao.get_form_detalle(sec_codigo=sec_codigo)
                formdet['cta_codigo'] = datosprod['icdp_modcontab']
                formdet['art_codigo'] = datosprod['ic_id']
                formdet['dt_precio'] = pagodet['costobase']
                formdet['dt_decto'] = pagodet['descuento']
                formdet['dt_debito'] = dt_debito_det
                formdet['dt_valor'] = formdet['dt_precio'] - formdet['dt_decto']

                impuestos = formcab['impuestos']
                formdet['dai_impg'] = 0.0
                if datosprod['icdp_grabaiva']:
                    formdet['dai_impg'] = impuestos['iva']
                    formdet['icdp_grabaiva'] = datosprod['icdp_grabaiva']

                detalles.append(formdet)

                costoexceso = pagodet['costoexceso']
                if costoexceso > 0:
                    datosprodex = itemconfigdao.get_detalles_prod(ic_id=agp_icexceso)
                    formdetex = self.aux_get_det(sec_codigo=sec_codigo, datosprod=datosprodex,
                                                 dt_debito=dt_debito_det, dt_valor=costoexceso)
                    detalles.append(formdetex)

                multa = pagodet['multa']
                if multa > 0:
                    datosprodmul = itemconfigdao.get_detalles_prod(ic_id=agp_icmulta)
                    formdetmul = self.aux_get_det(sec_codigo=sec_codigo, datosprod=datosprodmul,
                                                  dt_debito=dt_debito_det, dt_valor=multa)
                    detalles.append(formdetmul)

        if comision_mavil > 0:
            datosprodcm = itemconfigdao.get_detalles_prod(ic_id=agp_iccomavil)
            formdetcm = self.aux_get_det(sec_codigo=sec_codigo, datosprod=datosprodcm,
                                         dt_debito=dt_debito_det, dt_valor=comision_mavil)
            detalles.append(formdetcm)

        if len(detalles) == 0:
            raise ErrorValidacionExc('No hay detalles no se puede crear la factura')

        trn_codigo = tasientodao.crear(form=formcab, form_persona=referente, user_crea=user_crea, detalles=detalles,
                                       pagos=pagos, totales=totales, creaupdpac=False)

        pg_json = {
            "trn": trn_codigo,
            "pexceso": montos['consumo_exceso'],
            "pvconsumo": montos['costobase'] + montos['comision_mavil'],
            "pvexceso": montos['costoexceso'],
            "pvsubt": montos['costobase'] + montos['costoexceso'],
            "pvdesc": montos['descuento'],
            "pvmulta": montos['multa'],
            "pvtotal": montos['total'],
            "pfechamaxpago": montos['fecha_max_pago']

        }

        for lectura in lecturas:
            pg_id = lectura['pg_id']
            if pg_id == 0:
                tagp_pago = TagpPago()
                tagp_pago.lmd_id = lectura['lmd_id']
                tagp_pago.pg_estado = 1
                tagp_pago.pg_usercrea = user_crea
                tagp_pago.pg_fechacrea = datetime.now()
                tagp_pago.trn_codigo = trn_codigo
                tagp_pago.pg_json = self.dumps(pg_json)
                self.dbsession.add(tagp_pago)

        return trn_codigo
