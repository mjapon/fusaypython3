# coding: utf-8
"""
Fecha de creacion 5/19/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_pago.tagp_adelantos import AdelantosManageUtil
from fusayrepo.logica.aguap.tagp_pago.tagp_pago_dao import TagpCobroDao
from fusayrepo.logica.aguap.tagp_pago.tagp_pagomavil_dao import TagpPagoMavilDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagpcobro', path='/api/tagpcobro/{mdg_id}', cors_origins=('*',))
class TagpCobroRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        cobrodao = TagpCobroDao(self.dbsession)
        if accion == 'form':
            form = cobrodao.get_form()
            return self.res200({'form': form})
        elif accion == 'formpmavil':
            pagomavildao = TagpPagoMavilDao(self.dbsession)
            form = pagomavildao.get_form()
            return self.res200({'form': form})
        elif accion == 'gdatospago':
            trncod = self.get_request_param('trncod')
            datospago = cobrodao.get_datos_pago(trn_codigo=trncod)
            return self.res200({'datospago': datospago})
        elif accion == 'gformpagadel':
            adelantosdao = AdelantosManageUtil(self.dbsession)
            form = adelantosdao.get_form_pago_adelantado(per_id=self.get_request_param('per'))
            return self.res200({'form': form})
        elif accion == 'getadelantos':
            adelantosdao = AdelantosManageUtil(self.dbsession)
            adelantos = adelantosdao.get_adelantos(per_id=self.get_request_param('per'))
            return self.res200({'adelantos': adelantos})

    def collection_post(self):
        accion = self.get_rqpa()
        cobrodao = TagpCobroDao(self.dbsession)
        if accion == 'gcalpag':
            body = self.get_json_body()
            secdao = TSeccionDao(self.dbsession)
            alm_codigo = secdao.get_alm_codigo_from_sec_codigo(sec_codigo=self.get_sec_id())
            datospago = cobrodao.get_calculo_pago(lectoids=body['lectos'], alm_codigo=alm_codigo,
                                                  tdv_codigo=self.get_tdv_codigo(), sec_codigo=self.get_sec_id())
            return self.res200({'datospago': datospago})
        elif accion == 'crea':
            form = self.get_json_body()
            trn_codigo = cobrodao.crear(form=form, user_crea=self.get_user_id(), sec_codigo=self.get_sec_id())
            msg = 'Cobro registrado exitósamente, ¿Desea imprimir el comprobante?'
            return self.res200({'msg': msg, 'trncod': trn_codigo})
        elif accion == 'repagmavil':
            form = self.get_json_body()
            pagomavildao = TagpPagoMavilDao(self.dbsession)
            reporte = pagomavildao.get_reporte_pagos_mavil(anio=form['pgm_anio'], mes=form['pgm_mes'])
            return self.res200({'reporte': reporte})
        elif accion == 'saverepagmavil':
            pagomavildao = TagpPagoMavilDao(self.dbsession)
            form = self.get_json_body()
            pagomavildao.crear(form, user_crea=self.get_user_id())
            return self.res200({'msg': 'Pago registrado exitosamente'})
        elif accion == 'anular':
            pagomavildao = TagpPagoMavilDao(self.dbsession)
            form = self.get_json_body()
            pagomavildao.anular(form=form, useranula=self.get_user_id())
            return self.res200({'msg': 'Anulado exitoso'})
        elif accion == 'creapagoadelantado':
            adelantosdao = AdelantosManageUtil(self.dbsession)
            form = self.get_json_body()
            trn_codigo = adelantosdao.crear_pago_adelantado(form=form, usercrea=self.get_user_id(),
                                                            sec_codigo=self.get_sec_id())
            return self.res200({'trn_codigo': trn_codigo, 'msg': 'Pago adelantado registrado exitosamente'})
        elif accion == 'anularAboPagoAdel':
            form = self.get_request_json_body()
            tasiabondao = TAsiAbonoDao(self.dbsession)
            trn_cod_abo = form['trn_cod_abo']
            tasiabondao.anular(abo_codigo=form['codabo'], user_anula=self.get_user_id(), obs_anula=form['obs'])
            pagomavil = TagpPagoMavilDao(self.dbsession)
            datospago = pagomavil.find_by_trn_codigo(trn_codigo=trn_cod_abo)
            if datospago is None:
                raise ErrorValidacionExc('No pude recuperar datos del pago ')

            pagomavil.anula_solo_pago(pg_id=datospago['pg_id'])
            msg = 'Pago anulado anulado exitosamente'
            return self.res200({'msg': msg})
