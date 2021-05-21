# coding: utf-8
"""
Fecha de creacion 5/19/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.aguap.tagp_contrato.tagp_contrato_dao import TAgpContratoDao
from fusayrepo.logica.aguap.tagp_lectomed.tagp_lectomed_dao import LectoMedAguaDao
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.utils import numeros, fechas

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

        fecha_actual = datetime.now()
        fecha_consumo = ''
        fecha_max_pago = ''

        tasientodao = TasientoDao(self.dbsession)
        formcab = tasientodao.get_form_cabecera(tra_codigo=agp_tracod, alm_codigo=alm_codigo, sec_codigo=sec_codigo,
                                                tdv_codigo=tdv_codigo)

        for lectura in lecturas:
            pg_id = lectura['pg_id']
            consumo = float(lectura['lmd_consumo'])
            lmd_anio = lectura['lmd_anio']
            lmd_mes = lectura['lmd_mes']

            fecha_consumo = fechas.parse_cadena('01/{0}/{1}'.format(lmd_mes, lmd_anio))
            fecha_max_pago = fechas.sumar_meses(fecha_consumo, int(agp_permeses)).replace(day=int(agp_diacobro))

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
                consumo_exceso = 0
                consumo_base = consumo
                if consumo > trf_base:
                    consumo_exceso = numeros.roundm2(consumo - trf_base)
                    consumo_base = trf_base

                tarifaexceso = 0.0
                if consumo_exceso > 0:
                    datostarf_exceso = contratodao.get_tarifa_exceso(trf_id=trf_id, consumo=consumo_exceso)
                    if datostarf_exceso is None:
                        raise ErrorValidacionExc(
                            'No se ha configurado el costo por exceso de consumo (trf:{0})'.format(trf_id))

                    tarifaexceso = datostarf_exceso['etr_costo']

                datosprod = itemconfigdao.get_detalles_prod(ic_id=datoscontrato['ic_id'])
                icdp_precioventa = datosprod['icdp_precioventa']

                cna_teredad = datoscontrato['cna_teredad']

                costobase += icdp_precioventa
                costoexceso += numeros.roundm2(consumo_exceso * tarifaexceso)
                descuento += 0
                if cna_teredad:
                    descuento += numeros.roundm2(float(agp_pordescte) * costobase)
                if aplica_multa:
                    multa += float(agp_multa)

                total_it = costobase + costoexceso - descuento + multa
                total += numeros.roundm2(total_it)

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
            'formcab': formcab
        }

    def crear(self, form, user_crea, sec_codigo):
        referente = form['referente']
        medidor = form['datosmed']
        obs = form['obs']
        lecturas = form['lecturas']
        montos = form['montos']

        formcab = montos['formcab']

        lectomedagua_dao = LectoMedAguaDao(self.dbsession)
        ids = ','.join(['{0}'.format(it) for it in lecturas])
        lecturas = lectomedagua_dao.get_datos_lectura(ids=ids)

        tasientodao = TasientoDao(self.dbsession)
        transacpagodao = TTransaccPagoDao(self.dbsession)

        tparamsdao = TParamsDao(self.dbsession)
        agp_icexceso = tparamsdao.get_param_value('agp_icexceso')
        agp_icmulta = tparamsdao.get_param_value('agp_icmulta')

        if agp_icexceso is None:
            raise ErrorValidacionExc('El parámetro agp_icexceso no está configurado, favor verificar')

        if agp_icmulta is None:
            raise ErrorValidacionExc('El parámetro agp_icmulta no está configurado, favor verificar')

        formdet = tasientodao.get_form_detalle(sec_codigo=sec_codigo)
        itemconfigdao = TItemConfigDao(self.dbsession)

        contratodao = TAgpContratoDao(self.dbsession)
        formas_pago = transacpagodao.get_formas_pago(tra_codigo=formcab['tra_codigo'], sec_id=sec_codigo)
        fpago_efectivo = None
        for it in formas_pago:
            ic_clasecc = it['ic_clasecc']
            if ic_clasecc == 'E':
                fpago_efectivo = it

        pagos = []

        for lectura in lecturas:
            pg_id = lectura['pg_id']
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
