# coding: utf-8
"""
Fecha de creacion 4/28/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.utils import fechas, numeros, cadenas

log = logging.getLogger(__name__)


class LibroDiarioDao(BaseDao):

    @staticmethod
    def get_form_filtro():
        hoy = fechas.get_str_fecha_actual()
        desde = fechas.get_str_fecha(fechas.sumar_dias(fechas.get_now(), -30))

        form = {
            'desde': desde,
            'hasta': hoy,
            'cta_codigo': 0
        }

        return form

    def aux_get_all_asientos(self, desde, hasta, sec_id=0, cta_codigo=0):

        sfechas = ' '
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sfechas = " and (a.trn_fecreg between '{0}' and '{1}')".format(fechas.format_cadena_db(desde),
                                                                           fechas.format_cadena_db(hasta))
        scta_codigo = ' '
        if cadenas.es_nonulo_novacio(cta_codigo) and int(cta_codigo) > 0:
            scta_codigo = " and b.cta_codigo = {0}".format(cta_codigo)

        sql = """
        with asientos as (
        select a.trn_codigo, a.tra_codigo, a.trn_fecreg, extract(day from a.trn_fecreg) ||'-'|| m.mes_corto as fecdesc,
               a.trn_compro::int, a.trn_fecha, a.trn_valido, a.trn_docpen,
               a.per_codigo, a.us_id, a.trn_observ,               
               a.dt_debito, a.cta_codigo, a.ic_code, a.ic_nombre, a.dt_valor, 0 as bmo_id
        from vasientosgen a
            join titemconfig ic on a.cta_codigo = ic.ic_id
            join tasiento asi on a.trn_codigo = asi.trn_codigo and asi.sec_codigo = {sec_id}            
            join public.tmes m on  m.mes_id =  extract(month from a.trn_fecreg)
        where a.trn_valido = 0 {sfechas}
        union
        select a.trn_codigo, a.tra_codigo, a.trn_fecreg, extract(day from a.trn_fecreg) ||'-'|| m.mes_corto as fecdesc,
               a.trn_compro::int, a.trn_fecha, a.trn_valido, a.trn_docpen,
               a.per_codigo, a.us_id, a.trn_observ,
               b.dt_debito, b.cta_codigo, c.ic_code, c.ic_nombre, b.dt_valor, coalesce(bilmov.bmo_id, 0) as bmo_id 
        from tasiento a
                 join tasidetalle b on b.trn_codigo = a.trn_codigo
                 left join tbilleteramov bilmov on a.trn_codigo = bilmov.trn_codigo 
                 join titemconfig c on b.cta_codigo = c.ic_id
                 join public.tmes m on  m.mes_id =  extract(month from a.trn_fecreg)
        where a.sec_codigo = {sec_id} and tra_codigo = 13 and trn_valido = 0 and a.trn_docpen = 'F' {sfechas} {scta_codigo})
        select trn_codigo,tra_codigo,trn_fecreg, fecdesc, trn_compro, trn_fecha, trn_valido, trn_docpen,
               per_codigo, us_id, trn_observ, dt_debito, cta_codigo, ic_code, ic_nombre, dt_valor, bmo_id from asientos
        order by trn_fecreg desc, trn_compro desc, dt_debito desc
        """.format(sfechas=sfechas, sec_id=sec_id, scta_codigo=scta_codigo)

        tupla_desc = (
            'trn_codigo', 'tra_codigo', 'trn_fecreg', 'fecdesc', 'trn_compro', 'trn_fecha', 'trn_valido', 'trn_docpen',
            'per_codigo', 'us_id', 'trn_observ', 'dt_debito', 'cta_codigo', 'ic_code', 'ic_nombre', 'dt_valor',
            'bmo_id')
        return self.all(sql, tupla_desc)

    @staticmethod
    def _aux_add_rowlibrodiario(rlist, rowdata):
        rlist.append({
            'trn_codigo': rowdata['trn_codigo'],
            'tra_codigo': rowdata['tra_codigo'],
            'cta_codigo': '',
            'ic_code': '',
            'trn_fecreg': '',
            'ic_nombre': rowdata['trn_observ'],
            'dt_debito': 0,
            'debe': '',
            'haber': '',
            'tr': 2,
            'bmo_id': rowdata['bmo_id']
        })

    def listar_asientos(self, desde, hasta, sec_id=0, cta_codigo=0):
        items = self.aux_get_all_asientos(desde, hasta, sec_id=sec_id, cta_codigo=cta_codigo)
        resultlist = []
        lasttrncod = 0
        asiprevius = None
        totales = {
            'debe': 0.0,
            'haber': 0.0
        }
        for item in items:
            trn_codigo = item['trn_codigo']
            cab = False

            idx = items.index(item)
            idxprev = idx - 1
            if idxprev >= 0:
                asiprevius = items[idxprev]

            if trn_codigo != lasttrncod:
                cab = True
                lasttrncod = trn_codigo
                if idx > 0:
                    self._aux_add_rowlibrodiario(rlist=resultlist, rowdata=asiprevius)

            if cab:
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'tra_codigo': item['tra_codigo'],
                    'cta_codigo': '',
                    'ic_code': '',
                    'trn_fecreg': item['fecdesc'],
                    'ic_nombre': '{0}'.format(item['trn_compro']),
                    'dt_debito': 0,
                    'debe': '',
                    'haber': '',
                    'tr': 0,
                    'bmo_id': item['bmo_id']
                })
            if item['dt_debito'] == 1:
                totales['debe'] += item['dt_valor']
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'tra_codigo': item['tra_codigo'],
                    'cta_codigo': item['cta_codigo'],
                    'ic_code': item['ic_code'],
                    'trn_fecreg': '',
                    'ic_nombre': item['ic_nombre'],
                    'dt_debito': item['dt_debito'],
                    'debe': item['dt_valor'],
                    'haber': '',
                    'tr': 1,
                    'bmo_id': item['bmo_id']
                })
            elif item['dt_debito'] == -1:
                totales['haber'] += item['dt_valor']
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'tra_codigo': item['tra_codigo'],
                    'cta_codigo': item['cta_codigo'],
                    'ic_code': item['ic_code'],
                    'trn_fecreg': '',
                    'ic_nombre': item['ic_nombre'],
                    'dt_debito': item['dt_debito'],
                    'debe': '',
                    'haber': item['dt_valor'],
                    'tr': 1,
                    'bmo_id': item['bmo_id']
                })

            if item == items[len(items) - 1]:
                self._aux_add_rowlibrodiario(rlist=resultlist, rowdata=item)

        totales = {
            'debe': numeros.roundm2(totales['debe']),
            'haber': numeros.roundm2(totales['haber'])
        }

        return resultlist, totales
