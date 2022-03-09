# coding: utf-8
from fusayrepo.logica.aguap.tagp_lectomed.tagp_lectomed_dao import LectoMedAguaDao
from fusayrepo.logica.aguap.tagp_models import TAgpLectoMed
from fusayrepo.logica.aguap.tagp_pago.tagp_pago_dao import TagpCobroDao
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tbilletera.tbilleteramov_dao import TBilleteraMovDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils import fechas, numeros


class AdelantosManageUtil(BaseDao):

    def get_form_pago_adelantado(self, per_id):
        form = {
            'fecha': fechas.get_str_fecha_actual(),
            'monto': 0.0,
            'per_id': per_id
        }
        return form

    def has_adelantos(self, per_id):
        adelantos = self.get_adelantos(per_id)
        return adelantos is not None and len(adelantos) > 0

    def get_saldo_adelantos(self, per_id):
        adelantos = self.get_adelantos(per_id)
        saldo_adelantos = 0
        if adelantos is not None and len(adelantos) > 0:
            saldo_adelantos = adelantos[0]['cre_saldopen']

        return saldo_adelantos

    def get_pagos_con_adelanto(self, trn_codigo):
        tasiabonodao = TAsiAbonoDao(self.dbsession)
        abonos = tasiabonodao.listar_abonos(trn_codigo=trn_codigo)

    def get_adelantos(self, per_id):
        paramsado = TParamsDao(self.dbsession)
        cta_code_haber = paramsado.get_param_value('cta_adelagua_haber')

        sql = """
        select asi.trn_fecha, asi.trn_fecreg, asi.trn_observ,  det.trn_codigo, det.dt_valor, cred.cre_saldopen, 
        det.dt_codigo, cred.cre_codigo from tasidetalle det
        join tasiento asi on det.trn_codigo = asi.trn_codigo
        join titemconfig ic on det .cta_codigo = ic.ic_id
        join tasicredito cred on det.dt_codigo = cred.dt_codigo
        where asi.per_codigo = {0} and det.dt_debito = -1 and ic.ic_code = '{1}' and asi.trn_valido = 0
        and cred.cre_saldopen>0
        """.format(per_id, cta_code_haber)

        tupla_desc = ('trn_fecha', 'trn_fecreg', 'trn_observ', 'trn_codigo', 'dt_valor', 'cre_saldopen', 'dt_codigo')

        items = self.all(sql, tupla_desc)
        return items

    def check_saldo_adelanto_contra_total_fact(self, lecto_id, saldo_adelanto, sec_codigo, tdv_codigo):
        lectoids = [lecto_id]
        secdao = TSeccionDao(self.dbsession)
        cobrodao = TagpCobroDao(self.dbsession)
        alm_codigo = secdao.get_alm_codigo_from_sec_codigo(sec_codigo=sec_codigo)
        datospago = cobrodao.get_calculo_pago(lectoids=lectoids, alm_codigo=alm_codigo,
                                              tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)

        return numeros.roundm2(datospago['total']) <= saldo_adelanto

    def crear_factura(self, lecto_id, per_id, user_crea, sec_codigo, tdv_codigo):
        cobrodao = TagpCobroDao(self.dbsession)
        secdao = TSeccionDao(self.dbsession)
        lectodao = LectoMedAguaDao(self.dbsession)

        datos_lectura = lectodao.get_info_basic_lectura(lecto_id)
        form = {'referente': {'per_id': per_id},
                'obs': 'Registro de pago automático, haciendo uso de adelanto registrado AÑO:{anio}, MES:{mes}'.format(
                    anio=datos_lectura['lmd_anio'],
                    mes=datos_lectura['mes_nombre'])}
        lectoids = [lecto_id]
        form['lecturas'] = lectoids

        alm_codigo = secdao.get_alm_codigo_from_sec_codigo(sec_codigo=sec_codigo)
        datospago = cobrodao.get_calculo_pago(lectoids=lectoids, alm_codigo=alm_codigo,
                                              tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)

        #

        form['montos'] = datospago

        tagp_pago_dao = TagpCobroDao(self.dbsession)

        trn_codigo = tagp_pago_dao.crear(form=form, user_crea=user_crea, sec_codigo=sec_codigo, abono_cxpagar=True)
        return trn_codigo

    def crear_pago_adelantado(self, form, usercrea, sec_codigo):
        fecha = form['fecha']
        monto = form['monto']
        per_id = form['per_id']

        paramsado = TParamsDao(self.dbsession)
        cta_code_debe = paramsado.get_param_value('cta_adelagua_debe')
        cta_code_haber = paramsado.get_param_value('cta_adelagua_haber')

        if cta_code_debe is None:
            raise ErrorValidacionExc('No se ha definido el parámetro cta_adelagua_debe')
        if cta_code_haber is None:
            raise ErrorValidacionExc('No se ha definido el parámetro cta_code_haber')

        try:
            monto_number = float(monto)
        except:
            raise ErrorValidacionExc('Monto incorrecto, favor verificar')

        if monto_number <= 0:
            raise ErrorValidacionExc('El monto no puede ser negativo ni cero')

        itemconfigdao = TItemConfigDao(self.dbsession)
        tasientodao = TasientoDao(self.dbsession)

        datos_cta_debe = itemconfigdao.get_detalles_ctacontable_by_code(ic_code=cta_code_debe)
        datos_cta_haber = itemconfigdao.get_detalles_ctacontable_by_code(ic_code=cta_code_haber)

        if datos_cta_debe is None:
            raise ErrorValidacionExc('No pude recuperar datos de la cuenta contable {0}'.format(cta_code_debe))
        if datos_cta_haber is None:
            raise ErrorValidacionExc('No pude recuperar datos de la cuenta contable {0}'.format(datos_cta_haber))

        formasi = tasientodao.get_form_asiento(sec_codigo=sec_codigo)
        formasiento = formasi['formasiento']

        persondao = TPersonaDao(self.dbsession)
        person = persondao.buscar_porcodigo(per_id)
        formasiento['trn_fecreg'] = fecha
        formasiento['trn_observ'] = 'P/R Pago adelantado por servicio de agua potable referente: {0} - {1} {2}' \
            .format(person['per_ciruc'],
                    person['per_nombres'],
                    person['per_apellidos'])
        formref = formasi['formref']
        formdet = formasi['formdet']
        formref['per_id'] = per_id

        detalles = []

        newformdet = TBilleteraMovDao.clone_formdet(formdet)
        newformdet['dt_debito'] = 1
        newformdet['dt_valor'] = monto
        newformdet['cta_codigo'] = datos_cta_debe['ic_id']
        detalles.append(newformdet)

        newformdet = TBilleteraMovDao.clone_formdet(formdet)
        newformdet['dt_debito'] = -1
        newformdet['ic_clasecc'] = 'XP'
        newformdet['dt_valor'] = monto
        newformdet['cta_codigo'] = datos_cta_haber['ic_id']
        detalles.append(newformdet)
        trn_codigo = tasientodao.crear_asiento_cxcp(formcab=formasiento, per_codigo=per_id, user_crea=usercrea,
                                                    detalles=detalles)
        return trn_codigo
