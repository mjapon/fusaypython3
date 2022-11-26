# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from fusayrepo.logica.compele import ctes_facte
from fusayrepo.logica.compele.tcomprobante.tcomprobante_dao import TComprobanteDao
from fusayrepo.logica.compele.tcontribuyente.tcontribuyente_dao import TContribuyenteDao
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tasifacte.tasifacte_dao import TasiFacteDao

log = logging.getLogger(__name__)


class GenDataForFacte(BaseDao):

    def get_factura_data(self, trn_codigo):
        sql = """
        select 
                asi.trn_fecreg,
                talm.alm_ruc,
                asi.trn_compro,
                talm.alm_razsoc,
                talm.alm_nomcomercial,
                talm.alm_numest,
                ttpdv.tdv_numero,
                talm.alm_direcc,
                asi.per_codigo,
                per.per_ciruc,
                0 as propina,
                per.per_nombres||' '||coalesce(per.per_apellidos,'') per_nomapel,
                per.per_direccion,
                per.per_nombres,
                per.per_apellidos,
                per.per_telf,
                per.per_movil,
                per.per_email,
                asi.trn_compro,
                asi.sec_codigo 
                from tasiento asi
                join ttpdv on asi.tdv_codigo =   ttpdv.tdv_codigo
                join talmacen talm on ttpdv.alm_codigo = talm.alm_codigo
                join tpersona per on asi.per_codigo = per.per_id
                where asi.trn_codigo = {0}        
        """.format(trn_codigo)

        tupla_desc = ('trn_fecreg',
                      'alm_ruc',
                      'trn_compro',
                      'alm_razsoc',
                      'alm_nomcomercial',
                      'alm_numest',
                      'tdv_numero',
                      'alm_direcc',
                      'per_codigo',
                      'per_ciruc',
                      'propina',
                      'per_nomapel',
                      'per_direccion',
                      'per_nombres',
                      'per_apellidos',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'trn_compro',
                      'sec_codigo'
                      )

        datos_factura = self.first(sql, tupla_desc)

        tasidao = TasientoDao(self.dbsession)
        detalles = tasidao.get_detdoc_foredit(trn_codigo=trn_codigo, dt_tipoitem=1)
        pagos = tasidao.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=2, joinarts=False)
        totales = tasidao.calcular_totales(detalles)

        totales_facte = {
            'total_sin_impuesto': totales['subtotal'],
            'total_descuentos': totales['descuentos'],
            'base_imp_iva_12': totales['subtotal12'],
            'impuesto_iva_12': totales['iva'],
            'total': totales['total'],
            'pago_efectivo': totales['total'],
            'pago_credito': 0,  # TODO:
        }

        return {'cabecera': datos_factura,
                'detalles': detalles,
                'pagos': pagos,
                'totales': totales_facte}

    def get_datos_alm_matriz(self, sec_codigo):
        sqlbase = """
        select  alm.alm_codigo,
                alm_numest,
                alm_razsoc,
                alm_descri,
                alm_direcc,
                alm_repleg,
                alm_email,
                alm_websit,
                alm_fono1,
                alm_fono2,
                alm_movil,
                alm_ruc,
                alm_ciudad,
                alm_sector,
                alm_fecreg,
                cnt_codigo,
                alm_matriz,
                alm_tipoamb,
                alm_nomcomercial,
                alm_contab from talmacen alm
        """

        where = " where alm_matriz = 1 "
        if int(sec_codigo) > 1:
            where = """
            join tseccion sec on alm.alm_codigo = sec.alm_codigo 
            where sec.sec_id = {0}
            """.format(sec_codigo)

        sql = "{0} {1}".format(sqlbase, where)

        tupla_desc = (
            'alm_codigo',
            'alm_numest',
            'alm_razsoc',
            'alm_descri',
            'alm_direcc',
            'alm_repleg',
            'alm_email',
            'alm_websit',
            'alm_fono1',
            'alm_fono2',
            'alm_movil',
            'alm_ruc',
            'alm_ciudad',
            'alm_sector',
            'alm_fecreg',
            'cnt_codigo',
            'alm_matriz',
            'alm_tipoamb',
            'alm_nomcomercial',
            'alm_contab'
        )

        return self.first(sql, tupla_desc)

    def save_proxy_send_response(self, trn_codigo, ambiente, proxy_response):
        tasifacte_dao = TasiFacteDao(self.dbsession)
        data = {
            'tfe_estado': proxy_response['estado'],
            'tfe_estadosri': proxy_response['estadoSRI'],
            'tfe_fecautoriza': proxy_response['fechaAutorizacion'],
            'tfe_mensajes': str(proxy_response['mensajes']) if 'mensajes' in proxy_response else '',
            'tfe_numautoriza': proxy_response['numeroAutorizacion'],
            'tfe_ambiente': ambiente,
            'tfe_claveacceso': proxy_response['claveAcceso']
        }

        tasifacte_dao.create_or_update(trn_codigo=trn_codigo, data=data)

    def save_contrib_and_compro(self, datosfact, claveacceso, trn_cod, emp_codigo, total_fact, estado_envio,
                                ambiente):
        self.set_esquema(ctes_facte.ESQUEMA_FACTE_COMPROBANTES)
        tcontribdao = TContribuyenteDao(self.dbsession)
        tcomprobdao = TComprobanteDao(self.dbsession)

        form_contrib = {
            'cnt_ciruc': datosfact['per_ciruc'],
            'cnt_nombres': datosfact['per_nombres'],
            'cnt_apellidos': datosfact['per_apellidos'],
            'cnt_direccion': datosfact['per_direccion'],
            'cnt_telf': datosfact['per_telf'],
            'cnt_email': datosfact['per_email'],
            'cnt_movil': datosfact['per_movil']
        }
        cnt_id = tcontribdao.create_or_update(form=form_contrib)

        form_comprob = {
            'cmp_claveaccesso': claveacceso,
            'cmp_tipo': ctes_facte.COD_DOC_FACTURA,
            'cmp_numero': datosfact['trn_compro'],
            'cmp_trncod': trn_cod,
            'cnt_id': cnt_id,
            'emp_codigo': emp_codigo,
            'cmp_fecha': datosfact['trn_fecreg'],
            'cmp_total': total_fact,
            'cmp_estado': estado_envio,
            'cmp_ambiente': ambiente
        }

        tcomprobdao.crear(form=form_comprob)
