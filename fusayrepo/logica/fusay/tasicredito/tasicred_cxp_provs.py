# coding: utf-8
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.utils import fechas, cadenas
from fusayrepo.utils.numeros import roundm2

log = logging.getLogger(__name__)


class CuentasPorPagarProvsService(BaseDao):

    def get_report_for_export(self, from_date, to_date, provider_code, limit=50):
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
            it_grid_result = self.get_report(from_date, to_date, provider_code, firstit, limit)
            if firstit == 0:
                total = it_grid_result['total']
                cols = it_grid_result['cols']
                mxrexport = 1000
                if total > mxrexport:
                    raise ErrorValidacionExc('El total de resultados supera el límite máximo ')
            data = it_grid_result['data']
            for it in data:
                alldata.append(it)
                # cantventa += it['cantidad_venta']
                # totprecioventa += it['total_precioventa']
                # cantcompra += it['cantidad_compra']
                # totpreciocompra += it['total_preciocompra']
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

    def get_report(self, from_date, to_date, provider_code, first=0, limit=50):
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
        # qoffset = f"offset {int(page) * int(limit)}"
        qoffset = f"offset {int(first)}"

        filtro = ""
        if cadenas.es_nonulo_novacio(from_date) and cadenas.es_nonulo_novacio(to_date):
            filtro += " and (tasi.trn_fecreg between '{0}' and '{1}' )".format(
                fechas.format_cadena_db(from_date),
                fechas.format_cadena_db(to_date)
            )

        if provider_code is not None and str(provider_code).strip() != '' and int(provider_code) > 0:
            filtro += f" and tasi.per_codigo = {provider_code} "

        sql = f"""
        select         
       art.ic_id art_cod,
       art.ic_code codbarra,
       art.ic_nombre articulo,
       stock.ice_stock stock,
       case td.icdp_grabaiva when true then 'Si' else 'No' end as iva,
       case td.icdp_grabaiva when true then round(public.poner_iva_12(td.icdp_precioventa),4) 
        else round(td.icdp_precioventa,4) end as precioventa,
       case td.icdp_grabaiva when true then round(public.poner_iva_gen(imp.imp_valor, td.icdp_preciocompra),4) 
        else round(td.icdp_preciocompra,4) end as preciocompra,       
       sum(detart.dt_cant) nventas,
       round(sum(detart.dt_valor) + (sum(detart.dt_valor)*coalesce(detimp.dai_impg,0))) totventas
       --round((sum(detart.dt_cant) * td.icdp_preciocompra),2) totventpc 
       from tasiento tasi 
        join tasidetalle detart  on detart.trn_codigo  = tasi.trn_codigo and detart.dt_tipoitem = 1
        left join tasidetimp detimp on detart.dt_codigo = detimp.dt_codigo
        join titemconfig art on art.ic_id = detart.art_codigo
        join titemconfig_stock stock on stock.ic_id = art.ic_id  
        join titemconfig_datosprod td on art.ic_id = td.ic_id
        join timpuestos imp on td.icdp_tipoiva = imp.imp_id
        left join titemconfig_datosprod prov on art.ic_id  = prov.ic_id 
        where tasi.tra_codigo in (1,2) and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
        {filtro}
        group by art.ic_id, art.ic_code, art.ic_nombre, stock.ice_stock, td.icdp_precioventa, td.icdp_preciocompra, td.icdp_grabaiva, 
        imp.imp_valor, detimp.dai_impg
        order by art.ic_nombre
        {qlimit} {qoffset}
        """

        tupla_desc = ('art_cod', 'codbarra', 'articulo', 'stock', 'iva','precioventa', 'preciocompra', 'nventas', 'totventas')
        data = self.all(sql, tupla_desc)

        columnas = [
            {"label": "Cod. Barra", "field": "codbarra"},
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
            'cols': columnas
        }

        # self.anexar_detalles_compras_ventas(result, filtro)

        if int(first) == 0:
            sql_count = f"""
            select count(*) from (
                select art.ic_id
                from tasiento tasi 
                join tasidetalle detart  on detart.trn_codigo  = tasi.trn_codigo and detart.dt_tipoitem = 1
                join titemconfig art on art.ic_id = detart.art_codigo
                join titemconfig_stock stock on stock.ic_id = art.ic_id  
                join titemconfig_datosprod td on art.ic_id = td.ic_id
                left join titemconfig_datosprod prov on art.ic_id  = prov.ic_id 
                where tasi.tra_codigo in (1,2) and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
                {filtro}
                group by art.ic_id
            ) as t
            """
            count_res = self.first_raw(sql_count)
            result['total'] = count_res[0] if count_res else 0

        return result

    def anexar_detalles_compras_ventas(self, res, filtro):
        data = res['data']
        if not data:
            return res

        art_ids = [str(it['art_cod']) for it in data]
        param_lista = ",".join(art_ids)

        sql_compras = f"""
        select  det.art_codigo,  round(sum(det.dt_cant),2) cantidad_compra, round(sum(det.dt_valor),4) total_preciocompra from tasiento tasi
        join tasidetalle det on det.trn_codigo = tasi.trn_codigo and det.dt_tipoitem = 1 
        where tasi.trn_valido  = 0 and tasi.trn_docpen = 'F' and tra_codigo in (7) and det.art_codigo = ANY(ARRAY[{param_lista}]::int[]) {filtro} group by det.art_codigo
        """

        tupla_ventas = ('art_codigo', 'cantidad_venta', 'total_precioventa')
        tupla_compras = ('art_codigo', 'cantidad_compra', 'total_preciocompra')

        compras_res = self.all(sql_compras, tupla_compras)

        map_compras = {it['art_codigo']: it for it in compras_res}

        for it in data:
            art_cod = it['art_cod']
            compras_it = map_compras.get(art_cod)
            it['cantidad_compra'] = compras_it['cantidad_compra'] if compras_it else 0.0
            it['total_preciocompra'] = compras_it['total_preciocompra'] if compras_it else 0.0

        res['cols'].extend([
            {"label": "Cant. Venta", "field": "cantidad_venta"},
            {"label": "Total Venta", "field": "total_precioventa"},
            {"label": "Cant. Compra", "field": "cantidad_compra"},
            {"label": "Total Compra", "field": "total_preciocompra"}
        ])

        return res
