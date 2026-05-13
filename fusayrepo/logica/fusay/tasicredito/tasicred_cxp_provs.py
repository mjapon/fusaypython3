# coding: utf-8
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasicredito.tasicredito_provs_dao import TAsicreditoProvsDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tmodelocontab.tmodelocontab_dao import TModelocontabDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.utils import fechas, cadenas, ctes
from fusayrepo.utils.cloneutils import clone_formdet
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
         join tasicred_provs credprov on cred.cre_codigo = credprov.cre_codigo and credprov.crpr_status = 1
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo
        join tpersona per on tasi.per_codigo = per.per_id 
        where cred.cre_tipo = 2 and tasi.trn_docpen = 'F' and tasi.trn_valido = 0 {sqlfiltro}
        """
        totales = self.first_raw(sql)
        return {'credito': self.type_json(totales[1]), 'saldopend': self.type_json(totales[0])}

    def find(self, provider_code, tipopago, first=0, limit=50):
        qlimit = f"limit {limit}"
        qoffset = f"offset {int(first)}"

        filtros = []
        if provider_code is not None and str(provider_code).strip() != '' and int(provider_code) > 0:
            filtros.append(f"per.per_id = {provider_code}")

        if tipopago == 1:  # Busco todas las cuentas por cobrar que tienen aun un saldo pendiente
            filtros.append("cred.cre_saldopen>0")
        elif tipopago == 2:
            filtros.append("cred.cre_saldopen=0")

        filtro = " and ".join(filtros)
        if len(filtros) > 0:
            filtro = f" and {filtro}"

        sql = f"""select cred.cre_codigo,
       cred.dt_codigo,
       credprov.crpr_codigo,
       cred.cre_saldopen,
       detcred.dt_valor,
       detcred.trn_codigo,
       tasi.trn_compro,
       tasi.trn_fecha,
       tasi.trn_fecreg,
       tasi.trn_observ,
       per.per_id,
       per.per_nombres || ' ' || per.per_apellidos as referente,
       per.per_ciruc
from tasicredito cred
         join tasicred_provs credprov on cred.cre_codigo = credprov.cre_codigo and credprov.crpr_status = 1
         join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
         join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo
         join tpersona per on tasi.per_codigo = per.per_id 
where cred.cre_tipo = 2 and tasi.trn_docpen = 'F' and tasi.trn_valido = 0 {filtro}
order by tasi.trn_fecha desc {qlimit} {qoffset}"""

        tupla_cols = ("cre_codigo", "dt_codigo", "crpr_codigo", "cre_saldopen", "dt_valor", "trn_codigo", "trn_compro",
                      "trn_fecha", "trn_fecreg", "trn_observ", "per_id", "referente", "per_ciruc")

        data = self.all(sql, tupla_cols)

        columnas = [
            {"label": "Fecha", "field": "trn_fecreg", "width": "7%"},
            {"label": "Nro Factura", "field": "trn_compro", "width": "12%"},
            {"label": "Referente", "field": "referente", "width": "18%"},
            {"label": "Ci/ruc", "field": "per_ciruc", "width": "9%"},
            {"label": "Observación", "field": "trn_observ", "width": "20%"},
            {"label": "Crédito", "field": "dt_valor", "width": "9%"},
            {"label": "Saldo", "field": "cre_saldopen", "width": "9%"}
        ]

        result = {
            'data': data,
            'cols': columnas
        }

        if int(first) == 0:
            sql_count = f"""select count(*)
            from (select cred.cre_codigo from tasicredito cred
               join tasicred_provs credprov on cred.cre_codigo = credprov.cre_codigo and credprov.crpr_status = 1
               join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
               join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo
               join tpersona per on tasi.per_codigo = per.per_id 
      where cred.cre_tipo = 2 and tasi.trn_docpen = 'F' and tasi.trn_valido = 0 {filtro}
      order by tasi.trn_fecha desc) as t"""

            count_res = self.first_raw(sql_count)
            totales = self.totalizar_grid(filtro)
            result['total'] = count_res[0] if count_res else 0
            result['totales'] = totales

        return result

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
        qoffset = f"offset {int(first)}"

        filtro = ""
        if cadenas.es_nonulo_novacio(from_date) and cadenas.es_nonulo_novacio(to_date):
            filtro += " and (tasi.trn_fecreg between '{0}' and '{1}' )".format(
                fechas.format_cadena_db(from_date),
                fechas.format_cadena_db(to_date)
            )

        if provider_code is not None and str(provider_code).strip() != '' and int(provider_code) > 0:
            filtro += f" and td.icdp_proveedor = {provider_code} "

        sql = f"""
        select         
       art.ic_id art_cod,
       per.per_id codprov,
       per.per_nombres prov,
       art.ic_code codbarra,
       art.ic_nombre articulo,
       stock.ice_stock stock,
       case td.icdp_grabaiva when true then 'Si' else 'No' end as iva,
       case td.icdp_grabaiva when true then round(public.poner_iva_12(td.icdp_precioventa),4) 
        else round(td.icdp_precioventa,4) end as precioventa,
       case td.icdp_grabaiva when true then round(public.poner_iva_gen(imp.imp_valor, td.icdp_preciocompra),4) 
        else round(td.icdp_preciocompra,4) end as preciocompra,       
       sum(detart.dt_cant) nventas,
       round(sum(detart.dt_valor) + (sum(detart.dt_valor)*coalesce(detimp.dai_impg,0))) totventas,
       string_agg(detart.dt_codigo::text, ',') detsfact
       --round((sum(detart.dt_cant) * td.icdp_preciocompra),2) totventpc 
       from tasiento tasi 
        join tasidetalle detart  on detart.trn_codigo  = tasi.trn_codigo and detart.dt_tipoitem = 1
        left join tasidetimp detimp on detart.dt_codigo = detimp.dt_codigo
        join titemconfig art on art.ic_id = detart.art_codigo
        join titemconfig_stock stock on stock.ic_id = art.ic_id  
        join titemconfig_datosprod td on art.ic_id = td.ic_id
        join tpersona per on td.icdp_proveedor = per.per_id 
        join timpuestos imp on td.icdp_tipoiva = imp.imp_id
        left join titemconfig_datosprod prov on art.ic_id  = prov.ic_id 
        where tasi.tra_codigo in (1,2) and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
        and detart.dt_codigo not in (select dt_codigo from tasicred_provs_details where crp_status = 1)
        {filtro}
        group by art.ic_id, per.per_id, per.per_nombres, art.ic_code, art.ic_nombre, stock.ice_stock, td.icdp_precioventa, td.icdp_preciocompra, td.icdp_grabaiva, 
        imp.imp_valor, detimp.dai_impg
        order by art.ic_nombre
        {qlimit} {qoffset}
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
            'cols': columnas
        }

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

    def crear_asientos_cuenta_por_pagar(self, lista_data, user_crea, sec_id, sales_from, sales_to):
        """
        Crea un asiento de cuenta por pagar a partir de la lista de data proporcionada
        :param lista_data: Lista de diccionarios con la información para crear el asiento
        :param user_crea: Usuario que crea el asiento
        :return: Código del asiento creado
        """

        transaccpago = TTransaccPagoDao(self.dbsession)
        formas_pago = transaccpago.get_formas_pago(tra_codigo=ctes.TRA_COD_FACT_COMPRA, sec_id=sec_id)
        cta_contable_haber = next((fp for fp in formas_pago if fp['ic_clasecc'] == ctes.CLASECC_CTAXPAGAR), None)

        tmodelocontab = TModelocontabDao(self.dbsession)
        cta_contable_debe = tmodelocontab.get_datos_modelocontable_sec(mc_id=1, tra_codigo=ctes.TRA_COD_FACT_COMPRA,
                                                                       sec_codigo=sec_id)

        # El listado que llega es del tipo:
        # art_cod, codprov, prov, codbarra, articulo, stock, iva, precioventa, preciocompra, nventas, totventas, detsfact

        # Agrupar datos por codprov
        datos_agrupados = {}
        for item in lista_data:
            codprov = item['codprov']
            if codprov not in datos_agrupados:
                datos_agrupados[codprov] = []
            datos_agrupados[codprov].append(item)

        asicred_provs_dao = TAsicreditoProvsDao(self.dbsession)
        crpr_sales_from = fechas.format_cadena_db(sales_from)
        crpr_sales_to = fechas.format_cadena_db(sales_to)
        for provider_id, ventas in datos_agrupados.items():
            trn_codigo_gen, cre_codigo = self.crear_asiento_cuenta_por_pagar_proveedor(cod_prov=provider_id,
                                                                                       ventas=ventas,
                                                                                       cta_contable_debe=cta_contable_debe,
                                                                                       cta_contable_haber=cta_contable_haber,
                                                                                       user_crea=user_crea,
                                                                                       sec_id=sec_id,
                                                                                       sales_from=sales_from,
                                                                                       sales_to=sales_to)
            asicred_provs_dao.create(crpr_sales_from=crpr_sales_from,
                                     crpr_sales_to=crpr_sales_to,
                                     crpr_user_create=user_crea,
                                     cre_codigo=cre_codigo,
                                     details=[int(det) for venta in ventas for det in venta['detsfact'].split(',')])

        return True

    def crear_asiento_cuenta_por_pagar_proveedor(self, cod_prov, ventas, cta_contable_debe, cta_contable_haber,
                                                 user_crea, sec_id, sales_from, sales_to):
        """Crea un asiento de cuenta por pagar para un proveedor específico y un conjunto de ventas asociadas """

        nombre_prov = ventas[0]['prov'] if ventas else 'Proveedor Desconocido'

        # Calculo del monto del asiento contable
        monto_asiento = sum(venta['nventas'] * venta['preciocompra'] for venta in ventas)
        monto_asiento_round = roundm2(monto_asiento)
        observacion = (f"Cuenta por pagar al proveedor {nombre_prov} por venta de los siguientes productos: " +
                       ", ".join([f"{venta['articulo']}:{venta['nventas']}" for venta in ventas]) +
                       f" en le periodo {sales_from}- {sales_to}")

        tasientodao = TasientoDao(self.dbsession)
        formasiento = tasientodao.get_form_asiento(sec_codigo=sec_id)

        formasiento['formasiento']['trn_docpen'] = 'F'
        formasiento['formasiento']['trn_observ'] = observacion
        formasiento['formref']['per_id'] = cod_prov

        formdet = formasiento['formdet']
        detalles = []

        debedet = clone_formdet(formdet)
        debedet['dt_debito'] = 1
        debedet['dt_valor'] = monto_asiento_round
        debedet['cta_codigo'] = cta_contable_debe['cta_codigo']
        debedet['ic_clasecc'] = ''
        detalles.append(debedet)

        debedet = clone_formdet(formdet)
        debedet['dt_debito'] = -1
        debedet['dt_valor'] = monto_asiento_round
        debedet['cta_codigo'] = cta_contable_haber['cta_codigo']
        debedet['ic_clasecc'] = cta_contable_haber['ic_clasecc']
        detalles.append(debedet)

        formasiento['detalles'] = detalles

        trn_codigo_gen, cre_codigo = tasientodao.crear_asiento_cxcp_fromref(formcab=formasiento['formasiento'],
                                                                            formref=formasiento['formref'],
                                                                            usercrea=user_crea,
                                                                            detalles=formasiento['detalles'])

        return trn_codigo_gen, cre_codigo
