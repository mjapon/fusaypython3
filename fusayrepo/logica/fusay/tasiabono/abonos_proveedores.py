# coding: utf-8
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasiabono.tasiabono_provs_dao import AbonosProveedoresDAO
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tbilletera.tbilleterahist_dao import TBilleteraHistoDao
from fusayrepo.utils import ctes, numeros

log = logging.getLogger(__name__)


class AbonosProveedoresService(BaseDao):

    def crear_abonos(self, formdata, sec_codigo, usercrea):
        from_date = formdata.get('from')
        to_date = formdata.get('to')
        items = formdata.get('items', [])

        ventas_por_proveedor = {}
        ventas_por_credito = {}
        if items is not None and len(items) > 0:
            for item in items:
                codprov = item.get('codprov')
                if codprov not in ventas_por_proveedor:
                    ventas_por_proveedor[codprov] = []
                ventas_por_proveedor[codprov].append(item)
                credito_it = item.get('credito_sel')
                if credito_it not in ventas_por_credito:
                    ventas_por_credito[credito_it] = []
                ventas_por_credito[credito_it].append(item)

            for cod_credito_it in ventas_por_credito.keys():
                ventas_del_credito = ventas_por_credito.get(cod_credito_it)
                if len(ventas_del_credito) > 0:
                    first_venta_credito = ventas_del_credito[0]
                    saldo_pend_credito_it = numeros.roundm2(first_venta_credito.get('saldopend', 0.0))
                    if saldo_pend_credito_it > 0:
                        det_ventas_credito = []
                        det_ventas_credito_text = []
                        for venta in ventas_del_credito:
                            det_ventas_it = [int(c) for c in venta['detsfact'].split(',')]
                            det_ventas_credito.extend(det_ventas_it)
                            det_ventas_credito_text.append('{0}, cant:{1}'.format(venta.get('articulo', ''),
                                                                                  venta.get('nventas', '')))
                        monto_abonar_credito = sum([float(v.get('totventaspc', 0.0)) for v in ventas_del_credito])
                        if numeros.roundm2(monto_abonar_credito) <= numeros.roundm2(saldo_pend_credito_it):
                            cod_prov_it = first_venta_credito.get('codprov')
                            self.crear_abono_proveedor(cod_prov_it, monto_abonar_credito, cod_credito_it, from_date,
                                                       to_date, det_ventas_credito, det_ventas_credito_text, sec_codigo,
                                                       usercrea)
                        else:
                            credito_sel_text = first_venta_credito.get('credito_sel_text')
                            error_text = f'El monto a abonar {monto_abonar_credito} es mayor al saldo pendiente {saldo_pend_credito_it} del credito {credito_sel_text}'
                            log.error(error_text)
                            raise Exception(error_text)

    def crear_abono_proveedor(self, codprov, monto_abonar, credito_prov, from_date, to_date, dt_codigos_ventas,
                              dt_codigos_text_list, sec_codigo, usercrea):
        from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasiabonodao = TAsiAbonoDao(self.dbsession)
        tasientodao = TasientoDao(self.dbsession)
        form_abono = tasiabonodao.get_form_abono(tra_codigo=ctes.TRA_COD_ABO_COMPRA, sec_codigo=sec_codigo)
        formcab = form_abono.get('formcab')
        formcab['trn_observ'] = "Abono registrado por ventas de {0}".format(','.join(dt_codigos_text_list))
        formdet = form_abono.get('formdet')
        datos_credito = TAsicreditoDao(self.dbsession).get_datos_credito(cre_codigo=credito_prov)

        round_monto_abonar = numeros.roundm2(monto_abonar)
        detdebe = tasientodao.get_form_detalle_asiento()
        detdebe['cta_codigo'] = datos_credito.get('cta_codigo')
        detdebe['dt_debito'] = 1
        detdebe['ic_clasecc'] = datos_credito.get('ic_clasecc')
        detdebe['dt_valor'] = round_monto_abonar

        dethaber = tasientodao.get_form_detalle_asiento()
        dethaber['cta_codigo'] = formdet.get('cta_codigo')
        dethaber['dt_debito'] = -1
        dethaber['dt_valor'] = round_monto_abonar

        detalles = [detdebe, dethaber]

        tasiento = tasientodao.aux_set_datos_tasiento(usercrea=usercrea, per_codigo=codprov, formcab=formcab)
        trn_codigo = tasiento.trn_codigo

        abo_codigo = None
        for det in detalles:
            dt_codigo = tasientodao.save_tasidet_asiento(trn_codigo=trn_codigo, per_codigo=codprov, detalle=det,
                                                         roundvalor=True)
            if det.get('ic_clasecc') is not None and det.get('ic_clasecc') == 'XP':
                abo_codigo = tasiabonodao.crear(dt_codigo, datos_credito.get('dt_codigo'), monto_abono=monto_abonar)

        tbillhist_dao = TBilleteraHistoDao(self.dbsession)
        tbillhist_dao.generate_history_mov(trn_codigo)

        abono_proveedor_dao = AbonosProveedoresDAO(self.dbsession)
        abono_proveedor_dao.crear_abono_proveedor(credito_prov=credito_prov,
                                                  abo_codigo=abo_codigo,
                                                  from_date=from_date,
                                                  to_date=to_date,
                                                  dt_codigos_ventas=dt_codigos_ventas,
                                                  user_create=usercrea)
        return trn_codigo
