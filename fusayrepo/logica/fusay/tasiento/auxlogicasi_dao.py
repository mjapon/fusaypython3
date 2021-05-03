# coding: utf-8
"""
Fecha de creacion 5/3/21
@autor: mjapon
"""
import logging
from functools import reduce

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasidetimp.tasidetimp_model import TAsidetimp
from fusayrepo.utils import numeros, ctes, cadenas

log = logging.getLogger(__name__)


class AuxLogicAsiDao(BaseDao):

    def get_tasidetalle_pago(self):
        return None

    def chk_sum_debe_haber(self, vdebehaber):
        itemsdebe = map(lambda x: x['dt_valor'], filter(lambda item: item['dt_debito'] == 1, vdebehaber))
        itemshaber = map(lambda x: x['dt_valor'], filter(lambda item: item['dt_debito'] == -1, vdebehaber))

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

    def get_row_debehaber(self, detalle):
        pass
