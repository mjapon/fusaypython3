# coding: utf-8
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.utils import fechas, cadenas
from fusayrepo.utils import numeros
from fusayrepo.utils.numeros import roundm2

log = logging.getLogger(__name__)


class CuentasPorPagarProvsService(BaseDao):

    def get_report_for_export(self, from_date, to_date, sec_codigo, provider_code, limit=50):
        total = 0
        mxrexport = 0  # Numero maximo de filas para exportar
        continuar = True
        firstit = 0
        cantventa = 0.0
        totprecioventa = 0.0
        cantcompra = 0.0
        totpreciocompra = 0.0
        cols = None
        alldata = []
        while continuar:
            it_grid_result = self.get_ventas(from_date, to_date, provider_code, sec_codigo, firstit, limit)
            if firstit == 0:
                total = it_grid_result['total']
                cols = it_grid_result['cols']
                mxrexport = 1000
                if total > mxrexport:
                    raise ErrorValidacionExc('El total de resultados supera el límite máximo ')
            data = it_grid_result['data']
            for it in data:
                alldata.append(it)
            firstit = firstit + int(str(limit))
            continuar = len(data) == int(str(limit))

        sumatorias = {'codbarra': '', 'articulo': '',
                      'cantidad_venta': roundm2(cantventa),
                      'total_precioventa': roundm2(totprecioventa),
                      'cantidad_compra': roundm2(cantcompra),
                      'total_preciocompra': roundm2(totpreciocompra)}

        return {
            'count': total,
            'totales': sumatorias,
            'data': alldata,
            'cols': cols,
            'mxrexport': mxrexport
        }

    def find_details(self, crpr_codigo):

        sql = f"""
        select tasi.trn_compro,
       tasi.trn_fecha,
       tasi.trn_fecreg,
       art.ic_nombre articulo,
       detart.dt_cant cantidad
       from tasicred_provs credprov
       join tasicred_provs_details credprovdetail on credprov.crpr_codigo = credprovdetail.crpr_codigo and credprovdetail.crp_status = 1
       join tasidetalle detart on credprovdetail.dt_codigo  = detart.dt_codigo and credprovdetail.crp_status = 1
       join titemconfig art on art.ic_id = detart.art_codigo 
       join tasiento tasi on detart.trn_codigo = tasi.trn_codigo
       where credprov.crpr_status =1 and credprov.crpr_codigo = {crpr_codigo}
        """

        tupla_desc = ('trn_compro', 'trn_fecha', 'trn_fecreg', 'articulo', 'cantidad')
        result = self.all(sql, tupla_desc)
        cols = [
            {"label": "Fecha Venta", "field": "trn_fecreg", "width": "10%"},
            {"label": "Nro Factura", "field": "trn_compro", "width": "20%"},
            {"label": "Artículo", "field": "articulo", "width": "50%"},
            {"label": "Cantidad", "field": "cantidad", "width": "20%"},
        ]
        return {
            "data": result,
            "cols": cols
        }

    def totalizar_grid(self, sqlfiltro):
        sql = f"""
        select round(sum(cred.cre_saldopen),2) as saldopend,
            round(sum(detcred.dt_valor),2) as monto
               from tasicredito cred
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo
        join tpersona per on tasi.per_codigo = per.per_id 
        where cred.cre_tipo = 2 and tasi.trn_docpen = 'F' and tasi.trn_valido = 0 {sqlfiltro}
        """
        totales = self.first_raw(sql)
        return {'credito': self.type_json(totales[1]), 'saldopend': self.type_json(totales[0])}

    def build_report(self, from_date, to_date, provider_code, sec_codigo, first=0, limit=0):
        """
        Este metodo construye la información para el pago a proveedores dada las ventas actuales
        """

        ventas = self.get_ventas(from_date, to_date, provider_code, sec_codigo, first, limit)
        data = ventas.get('data')
        ventas_agrupadas = {}
        if data is not None and len(data) > 0:
            for it in data:
                codprov = it['codprov']
                if codprov not in ventas_agrupadas:
                    ventas_agrupadas[codprov] = []
                ventas_agrupadas[codprov].append(it)

        providers_code_set = list(ventas_agrupadas.keys())

        tasicred_dao = TAsicreditoDao(self.dbsession)
        cuentas_por_pagar = tasicred_dao.list_accounts_payable_by_provider_codes(providers_code_set)

        # Agrupar cuentas_por_pagar por codprov
        cuentas_por_pagar_agrupadas = {}
        codigos_articulos_set = set([])
        if cuentas_por_pagar is not None and len(cuentas_por_pagar) > 0:
            for item in cuentas_por_pagar:
                codprov = item['codprov']
                if codprov not in cuentas_por_pagar_agrupadas:
                    cuentas_por_pagar_agrupadas[codprov] = []
                cuentas_por_pagar_agrupadas[codprov].append(item)
                item['articuloslist'] = [int(it) for it in item['articulos'].split(',')]
                codigos_articulos_set.update(item['articuloslist'])

        # De las cuentas por pagar obtenidas debo armar un diccionario donde tenga el codigo de un artiulo y el codigo o codios de los creditos que tenga ese articulo
        articulos_creditos_map = {}
        totales_by_creditos_map = {}
        for art_codigo in codigos_articulos_set:
            creditos = [cred for cred in cuentas_por_pagar if art_codigo in cred['articuloslist']]
            if creditos is not None and len(creditos) > 0:
                articulos_creditos_map[art_codigo] = [{'value': cred['cre_codigo'],
                                                       'label': cred['credtext']} for cred in creditos]
                totales_by_creditos_map[art_codigo] = {
                    'saldopend': sum([cred.get('saldopend', 0.0) for cred in creditos]),
                    'deudatotal': sum([cred.get('deudatotal', 0.0) for cred in creditos])
                }

        resumen_por_proveedor = {}
        for prov in cuentas_por_pagar_agrupadas:
            deudas_prov = cuentas_por_pagar_agrupadas.get(prov)
            saldepend_prov = sum([it.get('saldopend', 0.0) for it in deudas_prov])
            deudatotal_prov = sum([it.get('deudatotal', 0.0) for it in deudas_prov])
            resumen_por_proveedor[prov] = {'saldopend': saldepend_prov, 'deudatotal': deudatotal_prov}

        for it in data:
            codprov = it['codprov']
            art_cod = int(it['art_cod'])
            infoprovlist = resumen_por_proveedor.get(codprov)
            preciocompra = it.get('preciocompra', 0.0)
            nventas = it.get('nventas', 0.0)
            totalventapc = numeros.roundm2(preciocompra * nventas)
            it['totventaspc'] = totalventapc
            if infoprovlist is not None:
                it['saldopendtotal'] = infoprovlist['saldopend']
                it['deudatotaltotal'] = infoprovlist['deudatotal']
            art_creditos = articulos_creditos_map.get(art_cod)
            saldos_creditos_art = totales_by_creditos_map.get(art_cod)
            if art_creditos is not None:
                it['creditos'] = [it['value'] for it in art_creditos]
                it['credito_sel'] = art_creditos[0]['value']
                it['credito_sel_text'] = art_creditos[0]['label']
                it['creditos_combo'] = art_creditos

            if saldos_creditos_art is not None:
                it['saldopend'] = saldos_creditos_art.get('saldopend', 0.0)
                it['deudatotal'] = saldos_creditos_art.get('deudatotal', 0.0)

        return ventas

    def get_ventas(self, from_date, to_date, provider_code, sec_codigo, first=0, limit=50):
        """
        Lista informacion de deudas de articulos para los filtros especificados
        :param from_date: Fecha inicial del reporte
        :param to_date: Fecha final del reporte
        :param provider_code: Codigo del proveedor (per_id)
        :param first: Numero de pagina para la paginacion
        :param limit: Limite de registros por pagina
        :return: dict con la data, columnas y total de registros
        """
        qlimit = f"limit {limit}"
        qoffset = f"offset {int(first)}"

        filtro = ""
        if cadenas.es_nonulo_novacio(from_date) and cadenas.es_nonulo_novacio(to_date):
            filtro += " and (tasi.trn_fecreg between '{0}' and '{1}' )".format(
                fechas.format_cadena_db(from_date),
                fechas.format_cadena_db(to_date)
            )

        if provider_code is not None and str(provider_code).strip() != '' and int(provider_code) > 0:
            filtro += f" and datprod.icdp_proveedor = {provider_code} "

        sql = f"""
        select
       art.ic_id art_cod,
       per.per_id codprov,
       per.per_nombres prov,
       art.ic_code codbarra,
       art.ic_nombre articulo,
       stock.ice_stock stock,
       case datprod.icdp_grabaiva when true then 'Si' else 'No' end as iva,
       case datprod.icdp_grabaiva when true then round(public.poner_iva_12(datprod.icdp_precioventa),4) 
        else round(datprod.icdp_precioventa,4) end as precioventa,
       case datprod.icdp_grabaiva when true then round(public.poner_iva_gen(imp.imp_valor, datprod.icdp_preciocompra),4) 
        else round(datprod.icdp_preciocompra,4) end as preciocompra,       
       sum(detart.dt_cant) nventas,
       round(sum(detart.dt_valor) + (sum(detart.dt_valor)*coalesce(detimp.dai_impg,0))) totventas,
       string_agg(detart.dt_codigo::text, ',') detsfact
       from tasiento tasi 
        join tasidetalle detart on detart.trn_codigo  = tasi.trn_codigo and detart.dt_tipoitem = 1
        left join tasidetimp detimp on detart.dt_codigo = detimp.dt_codigo
        join titemconfig art on art.ic_id = detart.art_codigo
        join titemconfig_stock stock on stock.ic_id = art.ic_id and sec_id = {sec_codigo}  
        join titemconfig_datosprod datprod on art.ic_id = datprod.ic_id
        join tpersona per on datprod.icdp_proveedor = per.per_id 
        join timpuestos imp on datprod.icdp_tipoiva = imp.imp_id         
        where tasi.tra_codigo in (1,2) and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
        and detart.dt_codigo not in (select dt_codigo_venta from tasiabo_provs_details where abpd_status = 1)
        {filtro}
        group by art.ic_id, per.per_id, per.per_nombres, art.ic_code, art.ic_nombre, stock.ice_stock, datprod.icdp_precioventa, datprod.icdp_preciocompra, datprod.icdp_grabaiva, 
        imp.imp_valor, detimp.dai_impg
        order by per.per_id, art.ic_nombre
        """

        tupla_desc = ('art_cod', 'codprov', 'prov', 'codbarra', 'articulo', 'stock', 'iva', 'precioventa',
                      'preciocompra', 'nventas', 'totventas', 'detsfact')
        data = self.all(sql, tupla_desc)

        columnas = [
            {"label": "Cod. Barra", "field": "codbarra"},
            {"label": "Proveedor", "field": "prov"},
            {"label": "Artículo", "field": "articulo"},
            {"label": "Graba Iva", "field": "iva"},
            {"label": "Stock Actual", "field": "stock"},
            {"label": "Num Ventas", "field": "nventas"},
            {"label": "Total Ventas(PV)", "field": "totventas"},
            {"label": "Precio Compra", "field": "preciocompra"},
            {"label": "Precio Venta", "field": "precioventa"}
        ]

        result = {
            'data': data,
            'cols': columnas,
            'total': 0
        }
        
        return result
