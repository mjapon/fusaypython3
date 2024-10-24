# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.compele.compele_util import CompeleUtilDao
from fusayrepo.logica.fusay.talmacen.talmacen_dao import TAlmacenDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasiento.auxlogicchangesec import AuxLogigChangeSeccion
from fusayrepo.logica.fusay.tasiento.librodiario_dao import LibroDiarioDao
from fusayrepo.logica.fusay.tasiento.reportescontables import ReportesContablesDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.logica.fusay.ttransaccrel.ttransaccrel_dao import TTransaccRelDao
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
            tdv_codigo = self.get_tdv_codigo()
            ttpdvdao = TtpdvDao(self.dbsession)
            secid = self.get_sec_id()
            alm_codigo = ttpdvdao.get_alm_codigo_from_sec_codigo(secid)
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)
            form_cab = tasientodao.get_form_cabecera(tra_codigo, alm_codigo, secid, tdv_codigo,
                                                     tra_emite=ttransacc['tra_tipdoc'])
            formaspago = transaccpago.get_formas_pago(tra_codigo=tra_codigo, sec_id=self.get_sec_id())
            pagosefectivo = transaccpago.get_pagos_efectivo(sec_id=self.get_sec_id())
            form_det = tasientodao.get_form_detalle(sec_codigo=secid)

            compeleutil = CompeleUtilDao(self.dbsession)
            facte_tipoamb = compeleutil.get_facte_tipoamb(sec_id=self.get_sec_id())

            return self.res200(
                {
                    'formcab': form_cab,
                    'ttransacc': ttransacc,
                    'formaspago': formaspago,
                    'pagosef': pagosefectivo,
                    'formdet': form_det,
                    'impuestos': form_cab['impuestos'],
                    'secid': secid,
                    'facte_tipoamb': facte_tipoamb
                }
            )

        elif accion == 'gdetdoc':
            trn_codigo = self.get_request_param('trncod')
            isforedit = False
            foredit = self.get_request_param('foredit')
            if foredit is not None:
                isforedit = foredit == '1'

            doc = tasientodao.get_documento(trn_codigo=trn_codigo, foredit=isforedit)
            ttransacclreldao = TTransaccRelDao(self.dbsession)
            datosnotacred = ttransacclreldao.get_datos_notacred_for_factura(trn_codfact=trn_codigo)
            return self.res200({'doc': doc, 'notacred': datosnotacred})
        elif accion == 'gfact':
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1

            docs, totales = tasientodao.listar_documentos(per_codigo=per_codigo, clase=clase,
                                                          sec_codigo=self.get_sec_id())
            return self.res200({'docs': docs, 'totales': totales})
        elif accion == 'gcred':
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1

            creds = tasicredao.listar_creditos(per_codigo=per_codigo, tipopago=0, clase=clase,
                                               sec_codigo=self.get_sec_id())
            return self.res200({'creds': creds})
        elif accion == 'gridventas':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            filtro = self.get_request_param('filtro')
            tracod = self.get_request_param('tracod')
            tipo = self.get_request_param('tipo')
            limit = self.get_request_param('limit')
            first = self.get_request_param('first')
            doexp = self.get_request_param('doexp')  # Indica si se debe buscar para exportacion de datos
            if doexp == '1':
                grid = tasientodao.listar_grid_ventas_for_export(desde, hasta, filtro, tracod, tipo,
                                                                 sec_id=self.get_sec_id(), limit=limit)
            else:
                grid = tasientodao.listar_grid_ventas(desde, hasta, filtro, tracod, tipo,
                                                      sec_id=self.get_sec_id(), limit=limit, first=first)

            totales = grid['sumatorias'] if 'sumatorias' in grid else {}
            return self.res200({'grid': grid, 'totales': totales})
        elif accion == 'formasiento':
            form = tasientodao.get_form_asiento(sec_codigo=self.get_sec_id())
            return self.res200({'form': form})
        elif accion == 'getasientos':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            cta_codigo = self.get_request_param('cta')
            librodiariodao = LibroDiarioDao(self.dbsession)
            items, totales = librodiariodao.listar_asientos(desde, hasta, sec_id=self.get_sec_id(),
                                                            cta_codigo=cta_codigo)
            return self.res200({'items': items, 'totales': totales})
        elif accion == 'getmovscta':
            cta_codigo = self.get_request_param('cta')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            res = tasientodao.listar_movs_ctacontable(cta_codigo=cta_codigo, desde=desde, hasta=hasta,
                                                      sec_id=self.get_sec_id())
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
            chkperparam = self.get_request_param('chkper')
            chk_per = True
            if chkperparam is not None and chkperparam == '0':
                chk_per = False

            reportes_cont_dao = ReportesContablesDao(self.dbsession)
            datos_balance = reportes_cont_dao.build_balance_gen_mayorizado(desde=desde, hasta=hasta,
                                                                           sec_id=self.get_sec_id(), chk_per=chk_per)

            return self.res200(
                {'balance': datos_balance['balance_list'],
                 'balancetree': datos_balance['balance_tree'],
                 'total_grupos': datos_balance['total_grupos'],
                 'resultado_ejercicio': datos_balance['resultado_ejercicio'],
                 'cta_contab_result': datos_balance['cta_contab_result']}
            )
        elif accion == 'getestadoresultados':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            reportes_cont_dao = ReportesContablesDao(self.dbsession)
            estado_resultados = reportes_cont_dao.get_resultado_ejercicio_mayorizado(desde=desde, hasta=hasta,
                                                                                     sec_id=self.get_sec_id())

            return self.res200(estado_resultados)
        elif accion == 'gettransaccs':
            tipo = self.get_request_param('tipo')
            items = tasientodao.listar_transacc_min(tipo)
            transaccsret = [{'tra_codigo': 0, 'tra_nombre': 'Todos'}]
            for cuenta in items:
                transaccsret.append(cuenta)
            return self.res200({'items': transaccsret})
        elif accion == 'formfiltrolibd':
            librodiariodao = LibroDiarioDao(self.dbsession)
            form = librodiariodao.get_form_filtro()
            return self.res200({'form': form})
        elif accion == 'formchangesec':
            auxlogichandao = AuxLogigChangeSeccion(self.dbsession)
            form = auxlogichandao.get_form_change_seccion(trn_codigo=self.get_request_param('trncod'))
            return self.res200(form)

    def collection_post(self):
        accion = self.get_request_param('accion')
        tasientodao = TasientoDao(self.dbsession)
        if accion == 'creadoc':
            form = self.get_json_body()
            formcab = form['form_cab']
            tra_codigo = int(formcab['tra_codigo'])
            trn_codigo = int(formcab['trn_codigo'])
            creando = False
            if trn_codigo > 0:
                tasientodao.editar(trn_codigo=trn_codigo, user_edita=self.get_user_id(), sec_codigo=self.get_sec_id(),
                                   detalles=form['detalles'], pagos=form['pagos'],
                                   totales=form['totales'], formcab=formcab, formref=form['form_persona'],
                                   creaupdref=True)
            else:
                trn_codigo = tasientodao.crear(form=formcab, form_persona=form['form_persona'],
                                               user_crea=self.get_user_id(),
                                               detalles=form['detalles'], pagos=form['pagos'],
                                               totales=form['totales'])
                creando = True
            msg = 'Registro exitoso'

            almdao = TAlmacenDao(self.dbsession)
            alm_tipoamb = almdao.get_alm_tipoamb()

            compelutil = CompeleUtilDao(self.dbsession)
            genera_factele = compelutil.is_generate_facte(sec_id=self.get_sec_id())
            compelenviado = False
            estado_envio = 0
            is_cons_final = False
            if genera_factele and creando and tra_codigo == ctes.TRA_COD_FACT_VENTA:
                log.info("Configurado facturacion se envia su generacion--trn_codigo:{0}".format(trn_codigo))

                is_cons_final = int(form['form_persona']['per_id']) < 0
                compelutil.redis_enviar(trn_codigo=trn_codigo, emp_codigo=self.get_emp_codigo(),
                                        emp_esquema=self.get_emp_esquema())
                compelenviado = True
                estado_envio = 0

            return self.res200(
                {'trn_codigo': trn_codigo, 'msg': msg, 'alm_tipoamb': alm_tipoamb,
                 'compelenviado': compelenviado, 'estado_envio': estado_envio, 'is_cons_final': is_cons_final})
        elif accion == 'anular':
            form = self.get_json_body()
            tasientodao.anular(trn_codigo=form['trncod'], user_anula=self.get_user_id(), obs_anula=form['obs'])
            msg = 'Comprobante anulado exitósamente'
            return self.res200({'msg': msg})
        elif accion == 'notacred':
            form = self.get_json_body()
            ttpdvdao = TtpdvDao(self.dbsession)
            sec_codigo = self.get_sec_id()
            alm_codigo = ttpdvdao.get_alm_codigo_from_sec_codigo(sec_codigo)
            trn_codigo_gen = tasientodao.generar_nota_credito(trn_codfactura=form['trn_codigo'], alm_codigo=alm_codigo,
                                                              sec_codigo=sec_codigo, tdv_codigo=self.get_tdv_codigo(),
                                                              usercrea=self.get_user_id())
            compelutil = CompeleUtilDao(self.dbsession)
            genera_factele = compelutil.is_generate_facte(sec_id=self.get_sec_id())
            resgen = {}
            if genera_factele:
                compelutil.redis_enviar_notacred(trn_codigo=trn_codigo_gen, emp_codigo=self.get_emp_codigo(),
                                                 emp_esquema=self.get_emp_esquema())
            return self.res200({'trncodgen': trn_codigo_gen, 'aut': resgen})

        elif accion == 'errar':
            form = self.get_json_body()
            tasientodao.marcar_errado(trn_codigo=form['trncod'], user_do=self.get_user_id())
            msg = 'Operación exitosa'
            return self.res200({'msg': msg})
        elif accion == 'duplicar':
            body = self.get_json_body()
            trn_codigo = tasientodao.duplicar_comprobante(trn_codigo=body['trn_codigo'],
                                                          user_crea=self.get_user_id(),
                                                          tra_codigo=ctes.TRA_COD_FACT_VENTA)
            return self.res200({'trn_codig': trn_codigo, 'msg': 'Duplicado exitoso'})
        elif accion == 'creasiento':
            body = self.get_json_body()
            trn_codigo = tasientodao.crear_asiento(formcab=body['formcab'], formref=body['formref'],
                                                   usercrea=self.get_user_id(),
                                                   detalles=body['detalles'])
            return self.res200({'msg': 'Asiento registrado exitósamente', 'trn_codigo': trn_codigo})
        elif accion == 'editasiento':
            body = self.get_json_body()
            trn_codigo = tasientodao.editar_asiento(formcab=body['formcab'], formref=body['formref'],
                                                    useredita=self.get_user_id(),
                                                    detalles=body['detalles'], obs='')
            return self.res200({'msg': 'Asiento actualizado exitósamente', 'trn_codigo': trn_codigo})
        elif accion == 'changesec':
            body = self.get_json_body()
            auxlogichandao = AuxLogigChangeSeccion(self.dbsession)
            changed = auxlogichandao.change_seccion(trn_codigo=body['trn_codigo'], new_sec_codigo=body['sec_codigo'])
            msg = 'No fue posible realizar el cambio de sección'
            if changed:
                msg = 'Cmabio de sección satisfactorio'

            return self.res200({'changed': changed, 'msg': msg})
