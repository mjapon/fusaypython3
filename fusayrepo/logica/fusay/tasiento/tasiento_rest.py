# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.utils import ctes, cadenas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasiento', path='/api/tasiento/{trn_codigo}', cors_origins=('*',))
class TAsientoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasientodao = TasientoDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)
        tasicredao = TAsicreditoDao(self.dbsession)
        transaccpago = TTransaccPagoDao(self.dbsession)

        if accion == 'formcab':
            tra_codigo = self.get_request_param('tra_cod')
            tdv_codigo = self.get_request_param('tdv_codigo')
            ttpdvdao = TtpdvDao(self.dbsession)
            secid = self.get_sec_id()
            alm_codigo = ttpdvdao.get_alm_codigo_from_sec_codigo(secid)
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)
            form_cab = tasientodao.get_form_cabecera(tra_codigo, alm_codigo, secid, tdv_codigo,
                                                     tra_tipdoc=ttransacc['tra_tipdoc'])
            formaspago = transaccpago.get_formas_pago(tra_codigo=tra_codigo)
            form_det = tasientodao.get_form_detalle(sec_codigo=secid)

            return self.res200(
                {
                    'formcab': form_cab,
                    'ttransacc': ttransacc,
                    'formaspago': formaspago,
                    'formdet': form_det,
                    'impuestos': form_cab['impuestos'],
                    'secid': secid
                }
            )

        elif accion == 'gdetdoc':
            trn_codigo = self.get_request_param('trncod')
            doc = tasientodao.get_documento(trn_codigo=trn_codigo)
            return self.res200({'doc': doc})
        elif accion == 'gfact':
            tra_codigo = 1
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1

            docs = tasientodao.listar_documentos(per_codigo=per_codigo, tra_codigo=tra_codigo,
                                                 find_pagos=True,
                                                 clase=clase)
            return self.res200({'docs': docs})
        elif accion == 'gcred':
            tra_codigo = 1
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1

            creds = tasicredao.listar_creditos(per_codigo=per_codigo, tra_codigo=tra_codigo,
                                               solo_pendientes=False, clase=clase)
            return self.res200({'creds': creds})
        elif accion == 'gridventas':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            filtro = self.get_request_param('filtro')
            tracod = self.get_request_param('tracod')
            tipo = self.get_request_param('tipo')
            grid, totales = tasientodao.listar_grid_ventas(desde, hasta, filtro, tracod, tipo)
            return self.res200({'grid': grid, 'totales': totales})
        elif accion == 'formasiento':
            form = tasientodao.get_form_asiento(sec_codigo=self.get_sec_id())
            return self.res200({'form': form})
        elif accion == 'getasientos':
            items, totales = tasientodao.listar_asientos()
            return self.res200({'items': items, 'totales': totales})
        elif accion == 'getmovscta':
            cta_codigo = self.get_request_param('cta')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            res = tasientodao.listar_movs_ctacontable(cta_codigo=cta_codigo, desde=desde, hasta=hasta)
            return self.res200({'res': res})
        elif accion == 'getformlibromayor':
            forml = tasientodao.get_form_libromayor()
            return self.res200({'form': forml})
        elif accion == 'getdatosasiconta':
            trn_codigo = self.get_request_param('cod')
            res = tasientodao.get_datos_asientocontable(trn_codigo=trn_codigo)
            return self.res200({'datoasi': res})
        elif accion == 'getbalancegeneral':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            balancegen, parents, parentestres, restulttree = tasientodao.buid_rep_conta(desde, hasta,
                                                                                        wherecodparents="ic_code like '1%' or ic_code like '2%' or ic_code like '3%'")
            return self.res200(
                {'balance': balancegen, 'parents': parents, 'parentres': parentestres, 'balancetree': restulttree})
        elif accion == 'getestadoresultados':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            balancegen, parents, parentestres, restulttree = tasientodao.buid_rep_conta(desde, hasta,
                                                                                        wherecodparents="ic_code like '4%' or ic_code like '5%'",
                                                                                        isestadores=True)
            return self.res200({'balance': balancegen, 'parents': parents, 'balancetree': restulttree})
        elif accion == 'gettransaccs':
            tipo = self.get_request_param('tipo')
            items = tasientodao.listar_transacc_min(tipo)
            transaccsret = [{'tra_codigo': 0, 'tra_nombre': 'Todos'}]
            for cuenta in items:
                transaccsret.append(cuenta)
            return self.res200({'items': transaccsret})

    def collection_post(self):
        accion = self.get_request_param('accion')
        tasientodao = TasientoDao(self.dbsession)
        if accion == 'creadoc':
            form = self.get_json_body()
            trn_codigo = tasientodao.crear(form=form['form_cab'], form_persona=form['form_persona'],
                                           user_crea=self.get_user_id(),
                                           detalles=form['detalles'], pagos=form['pagos'],
                                           totales=form['totales'])
            msg = 'Registro exitoso'
            return self.res200({'trn_codigo': trn_codigo, 'msg': msg})
        elif accion == 'anular':
            form = self.get_json_body()
            tasientodao.anular(trn_codigo=form['trncod'], user_anula=self.get_user_id(), obs_anula=form['obs'])
            msg = 'Comprobante anulado exitosamente'
            return self.res200({'msg': msg})
        elif accion == 'errar':
            form = self.get_json_body()
            tasientodao.marcar_errado(trn_codigo=form['trncod'], user_do=self.get_user_id())
            msg = 'Operación exitosa'
            return self.res200({'msg': msg})
        elif accion == 'duplicar':
            body = self.get_json_body()
            trn_codigo = tasientodao.duplicar_comprobante(trn_codigo=body['trn_codigo'],
                                                          user_crea=self.get_user_id(),
                                                          tra_codigo=ctes.TRA_CODIGO_FACTURA_VENTA)
            return self.res200({'trn_codig': trn_codigo, 'msg': 'Duplicado exitoso'})
        elif accion == 'creasiento':
            body = self.get_json_body()
            trn_codigo = tasientodao.crear_asiento(formcab=body['formcab'], formref=body['formref'],
                                                   usercrea=self.get_user_id(),
                                                   detalles=body['detalles'])
            return self.res200({'msg': 'Asiento registrado exitosamente', 'trn_codigo': trn_codigo})
        elif accion == 'editasiento':
            body = self.get_json_body()
            trn_codigo = tasientodao.editar_asiento(formcab=body['formcab'], formref=body['formref'],
                                                    useredita=self.get_user_id(),
                                                    detalles=body['detalles'], obs='')
            return self.res200({'msg': 'Asiento actualizado exitosamente', 'trn_codigo': trn_codigo})
