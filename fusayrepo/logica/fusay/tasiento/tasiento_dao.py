# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import functools
import logging
from datetime import datetime
from functools import reduce

from sqlalchemy.orm import make_transient

from fusayrepo.logica.compele import ctes_facte
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasiento.auxlogicasi_dao import AuxLogicAsiDao
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento
from fusayrepo.logica.fusay.tasiento.tasientoaud_dao import TAsientoAudDao
from fusayrepo.logica.fusay.tasifacte.tasifacte_dao import TasiFacteDao
from fusayrepo.logica.fusay.tbilletera.tbilleterahist_dao import TBilleteraHistoDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.timpuesto.timpuesto_dao import TImpuestoDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.utils import fechas, numeros, ctes, cadenas

log = logging.getLogger(__name__)


class TasientoDao(AuxLogicAsiDao):

    def find_entity_byid(self, trn_codigo):
        return self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()

    def get_form_asiento(self, sec_codigo):
        formasiento = self.get_form_cabecera(tra_codigo=ctes.TRA_COD_ASI_CONTABLE,
                                             alm_codigo=0, sec_codigo=0, tdv_codigo=0, tra_emite=1)
        formdet = self.get_form_detalle_asiento()
        persondao = TPersonaDao(self.dbsession)
        formref = persondao.get_form()
        formref['per_id'] = -1
        formasiento['sec_codigo'] = sec_codigo
        return {
            'formasiento': formasiento,
            'formref': formref,
            'formdet': formdet
        }

    @staticmethod
    def get_form_libromayor():
        hoy = datetime.today().date()
        fdm = hoy.replace(day=1)
        return {
            'cta_codigo': 0,
            'desde': fechas.parse_fecha(fdm),
            'hasta': fechas.get_str_fecha_actual()
        }

    def listar_movs_ctacontable(self, cta_codigo, desde, hasta, sec_id=0):
        gridado = TGridDao(self.dbsession)

        tparamsdao = TParamsDao(self.dbsession)
        fecha_ini_contab = tparamsdao.get_param_value('fecha_ini_contab', sec_id=sec_id)
        sqlfechainicontab = ''
        if fecha_ini_contab is not None and len(fecha_ini_contab) > 0:
            sqlfechainicontab = " and date(asi.trn_fecha)>='{0}' ".format(fechas.format_cadena_db(fecha_ini_contab))

        resgrid = gridado.run_grid('libromayor', cta_codigo=cta_codigo,
                                   desde=fechas.format_cadena_db(desde),
                                   hasta=fechas.format_cadena_db(hasta),
                                   fecinicontab=sqlfechainicontab)

        previus_desde_db = fechas.sumar_dias(fechas.parse_cadena(desde), -1)
        sql_sum_previus = """
        select mcd_dia, 
               coalesce(mcd_debe,0) as mcd_debe, 
               coalesce(mcd_haber,0) as mcd_haber,
               coalesce(mcd_saldo,0) as mcd_saldo  
        from tsum_ctas_diario where cta_id = {0} and mcd_dia ='{1}' order by mcd_dia desc limit 1        
        """.format(cta_codigo, previus_desde_db)
        tupla_desc = ('mcd_dia', 'mcd_debe', 'mcd_haber', 'mcd_saldo')
        sum_previus = self.first(sql_sum_previus, tupla_desc)
        previus_debe = 0
        previus_haber = 0
        previus_saldo = 0
        if sum_previus:
            previus_debe = sum_previus['mcd_debe']
            previus_haber = sum_previus['mcd_haber']
            previus_saldo = sum_previus['mcd_saldo']

        data = resgrid['data']
        for it in data:
            it['saldo'] = float(it['saldo']) + previus_saldo
        debe = map(lambda x: x['debe'], filter((lambda x: x['dt_debito'] == 1), data))
        haber = map(lambda x: x['haber'], filter((lambda x: x['dt_debito'] == -1), data))

        totdebe = reduce((lambda x, y: x + y), debe, 0.0)
        tothaber = reduce((lambda x, y: x + y), haber, 0.0)

        resta = totdebe - tothaber
        totales = {
            'totdebe': numeros.roundm2(totdebe),
            'tothaber': numeros.roundm2(tothaber),
            'resta': numeros.roundm2(resta)
        }

        return {
            'grid': resgrid,
            'totales': totales
        }

    def get_form_cabecera(self, tra_codigo, alm_codigo, sec_codigo, tdv_codigo, tra_emite=1):
        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
        resestabsec = {'tps_codigo': 0, 'estabptoemi': '', 'secuencia': ''}
        if tra_emite == 1:  # Solo para documentos emitidos se debe generar la secuencia
            resestabsec = ttransacc_pdv.get_estabptoemi_secuencia(alm_codigo=alm_codigo, tra_codigo=tra_codigo,
                                                                  tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)
        timpuestodao = TImpuestoDao(self.dbsession)
        impuestos = timpuestodao.get_impuestos()
        trn_compro = ''
        form_asiento = {
            'dia_codigo': 0,
            'trn_fecreg': fechas.parse_fecha(fechas.get_now()),
            'trn_fecregobj': fechas.parse_fecha(fechas.get_now()),
            'trn_compro': trn_compro,
            'trn_docpen': 'F',
            'trn_pagpen': 'F',
            'sec_codigo': sec_codigo,
            'tra_codigo': tra_codigo,
            'trn_observ': '',
            'tdv_codigo': tdv_codigo,
            'fol_codigo': 0,
            'trn_tipcom': '',
            'trn_suscom': '',
            'tps_codigo': resestabsec['tps_codigo'],
            'estabptoemi': resestabsec['estabptoemi'],
            'secuencia': resestabsec['secuencia'],
            'trn_impref': impuestos['iva'],
            'impuestos': impuestos,
            'trn_codigo': 0
        }

        return form_asiento

    def contar_grid_ventas(self, swhere):
        sql = """ select  count(*) as cuenta from tasiento a
         join tpersona p on a.per_codigo = p.per_id where a.trn_valido = 0 {swhere} 
        """.format(swhere=swhere)
        result = self.first_raw(sql)
        return result[0] if result is not None else 0

    def totalizar_grid_ventas(self, swhere):

        sql = """select ic.ic_clasecc, sum(det.dt_valor), sum(coalesce(cred.cre_saldopen, 0.0)) as cre_saldopen
                    from tasidetalle det
                             join titemconfig ic on det.cta_codigo = ic.ic_id
                             left join tasicredito cred on det.dt_codigo = cred.dt_codigo
                             join tasiento a on det.trn_codigo = a.trn_codigo
                             join tpersona p on a.per_codigo = p.per_id
                    where a.trn_valido = 0
                      and det.dt_tipoitem = 2 {swhere}
                    group by ic.ic_clasecc
        """.format(swhere=swhere)
        result = self.all_raw(sql)

        totales = {'efectivo': 0.0, 'credito': 0.0, 'saldopend': 0.0, 'total': 0.0}
        for row in result:
            if row[0] == 'XC' or row[0] == 'XP':
                totales['credito'] = float(row[1])
                totales['saldopend'] = float(row[2])
            else:
                totales['efectivo'] = float(row[1])

            totales['total'] += float(row[1])

        for key in totales:
            totales[key] = numeros.roundm2(totales[key])

        return totales

    def build_grid_ventas_where(self, desde, hasta, filtro, tracod, tipo, sec_id):
        sqladc = ''
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sqladc = " and (a.trn_fecreg between '{0}' and '{1}' )".format(fechas.format_cadena_db(desde),
                                                                           fechas.format_cadena_db(hasta))

        if cadenas.es_nonulo_novacio(filtro):
            filtroupper = cadenas.strip_upper(filtro)
            auxfiltroupper = '%'.join(filtroupper.split(' '))
            filtrocedula = " ( ( (p.per_nombres || ' ' || coalesce(p.per_apellidos, '')) like '%{0}%' ) or (p.per_ciruc like '%{0}%') ) ".format(
                auxfiltroupper)
            filtronrocompro = " (a.trn_compro like '%{0}%') ".format(auxfiltroupper)
            sqladc += " and ({0} or {1})".format(filtrocedula, filtronrocompro)

        sqltra = ''
        if int(tracod) == 0:
            if int(tipo) == 1:  # Ventas
                sqltra = "and a.tra_codigo in (1,2)"
            elif int(tipo) == 2:  # Compras
                sqltra = "and a.tra_codigo in (7)"
            elif int(tipo) == 3:  # Noas de credito
                sqltra = "and a.tra_codigo in (4)"
            elif int(tipo) == 4:  # Proformas
                sqltra = "and a.tra_codigo in (14)"
        else:
            sqltra = "and a.tra_codigo in ({0})".format(tracod)

        return " {0} {1} and a.trn_docpen='F' and a.sec_codigo = {2}".format(sqltra, sqladc, sec_id)

    def listar_grid_ventas_for_export(self, desde, hasta, filtro, tracod, tipo, sec_id, limit=15):

        total = 0
        mxrexport = 0  # Numero maximo de filas para exportar
        continuar = True
        firstit = 0
        sumatorias = None
        cols = None
        alldata = []
        while continuar:
            it_grid_result = self.listar_grid_ventas(desde, hasta, filtro, tracod, tipo, sec_id, limit, firstit)
            if firstit == 0:
                total = it_grid_result['total']
                sumatorias = it_grid_result['sumatorias']
                cols = it_grid_result['cols']
                mxrexport = it_grid_result['mxrexport']
                if total > mxrexport:
                    raise ErrorValidacionExc('El total de resultados supera el límite máximo ')
            data = it_grid_result['data']
            for it in data:
                alldata.append(it)
            firstit = firstit + int(str(limit))
            continuar = len(data) == int(str(limit))

        return {
            'total': total,
            'sumatorias': sumatorias,
            'data': alldata,
            'cols': cols,
            'mxrexport': mxrexport
        }

    def listar_grid_ventas(self, desde, hasta, filtro, tracod, tipo, sec_id, limit=15, first=0):
        tgrid_dao = TGridDao(self.dbsession)

        swhere = self.build_grid_ventas_where(desde, hasta, filtro, tracod, tipo, sec_id)

        offset = first
        limit = "limit {0}".format(limit)
        offset = "offset {0}".format(offset)
        grid = tgrid_dao.run_grid(grid_nombre='ventas', swhere=swhere, limit=limit, offset=offset)

        trn_codigos = [str(row['trn_codigo']) for row in grid['data']]
        pagos_map = self.get_pagos_factura(','.join(trn_codigos))
        for row in grid['data']:
            trn_codigo = row['trn_codigo']
            if trn_codigo in pagos_map:
                pago_row = pagos_map[trn_codigo]
                row["efectivo"] = pago_row['efectivo']
                row["credito"] = pago_row['credito']
                row["saldopend"] = pago_row['saldopend']
                row["total"] = pago_row['total']

        if int(first) == 0:
            totales = self.totalizar_grid_ventas(swhere=swhere)
            total = self.contar_grid_ventas(swhere=swhere)
            grid['total'] = total
            grid['sumatorias'] = totales
        return grid

    def get_pagos_factura(self, trn_codigos):
        resultmap = {}
        if len(trn_codigos) > 0:
            sql = f"""select det.trn_codigo, ic.ic_clasecc, det.dt_valor, coalesce(cred.cre_saldopen, 0.0) as cre_saldopen
                    from tasidetalle det
                    join titemconfig ic on det.cta_codigo = ic.ic_id
                    left join tasicredito cred on det.dt_codigo = cred.dt_codigo
                where det.trn_codigo in ({trn_codigos})
                and det.dt_tipoitem = 2"""
            results = self.all_raw(sql)

            for row in results:
                if row[0] not in resultmap:
                    resultmap[row[0]] = {'credito': 0.0, 'efectivo': 0.0, 'saldopend': 0.0, 'total': 0.0}
                if row[1] == 'XC' or row[1] == 'XP':
                    resultmap[row[0]]['credito'] = float(row[2])
                    resultmap[row[0]]['saldopend'] = float(row[3])
                else:
                    resultmap[row[0]]['efectivo'] = float(row[2])

                resultmap[row[0]]['total'] += float(row[2])

        return resultmap

    def aux_get_cod_cuentas_repconta(self, cuentas, codcuentas):
        for cuenta in cuentas:
            dbdata_it = cuenta['dbdata']
            codcuentas.append('\'{0}\''.format(dbdata_it['ic_id']))
            if 'children' in cuenta:
                codcuentas = self.aux_get_cod_cuentas_repconta(cuentas=cuenta['children'], codcuentas=codcuentas)

        return codcuentas

    def get_datos_asientocontable(self, trn_codigo):
        formasiento = self.get_cabecera_asiento(trn_codigo=trn_codigo)
        try:
            formasiento['secuencia'] = int(formasiento['trn_compro'][6:])
        except Exception as ex:
            log.error('Error controlado al tratar de obtener valor de secuencia de un tasiento', ex)
            formasiento['secuencia'] = formasiento['trn_compro']

        formasiento['tps_codigo'] = 0

        sqldet = """
        select det.dt_codigo, det.cta_codigo, det.dt_cant, det.dt_debito, det.dt_tipoitem, det.dt_valor,
               det.dt_valor as dt_valor_in, ic.ic_clasecc, ic.ic_code, ic.ic_nombre, det.per_codigo, det.pry_codigo,
               det.dt_codsec
            from tasidetalle det
            join titemconfig ic on det.cta_codigo = ic.ic_id
            where det.trn_codigo = {0} order by det.dt_debito desc, ic.ic_nombre
        """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'cta_codigo', 'dt_cant', 'dt_debito', 'dt_tipoitem', 'dt_valor',
                      'dt_valor_in', 'ic_clasecc', 'ic_code', 'ic_nombre', 'per_codigo', 'pry_codigo', 'dt_codsec')

        detalles = self.all(sqldet, tupla_desc)
        debes = list(map(lambda it: it['dt_valor'], filter(lambda fila: fila['dt_debito'] == 1, detalles)))
        habers = list(map(lambda it: it['dt_valor'], filter(lambda fila: fila['dt_debito'] == -1, detalles)))

        sumadebe = 0.0
        if len(debes) > 0:
            sumadebe = functools.reduce(lambda a, b: a + b, debes)
        sumahaber = 0.0
        if len(habers) > 0:
            sumahaber = functools.reduce(lambda a, b: a + b, habers)

        totales = {
            'debe': numeros.roundm2(sumadebe['dt_valor'] if type(sumadebe) is dict else sumadebe),
            'haber': numeros.roundm2(sumahaber['dt_valor'] if type(sumahaber) is dict else sumahaber)
        }

        tra_codigo = formasiento['tra_codigo']
        datosfact_aborel = None
        if tra_codigo == ctes.TRA_COD_ABO_VENTA or tra_codigo == ctes.TRA_COD_ABO_COMPRA:
            tasiabodao = TAsiAbonoDao(self.dbsession)
            datosfact_aborel = tasiabodao.find_trn_codrel_abo(detalles)

        return {
            'cabecera': formasiento,
            'detalles': detalles,
            'totales': totales,
            'factrel': datosfact_aborel
        }

    @staticmethod
    def get_form_detalle_asiento():
        form = {
            'cta_codigo': 0,
            'per_codigo': 0,
            'pry_codigo': 0,
            'dt_debito': 0,
            'dt_valor': 0.0,
            'dt_valor_in': 0.0,
            'dt_tipoitem': 4,
            'dt_codsec': 1,
            'ic_clasecc': ''
        }

        return form

    @staticmethod
    def get_form_detalle(sec_codigo):
        form = {
            'cta_codigo': 0,
            'art_codigo': 0,
            'ic_nombre': '',
            'per_codigo': 0,
            'pry_codigo': 0,
            'dt_cant': 1,
            'dt_precio': 0.0,
            'dt_precioiva': 0.0,
            'dt_valoriva': 0.0,
            'dt_debito': 0,
            'dt_preref': 0.0,
            'dt_decto': 0.0,
            'dt_dectotipo': '1',  # 1-valor, 2-porcentaje
            'dt_dectoin': 0.0,
            'dt_dectoporcin': 0.0,
            'dt_valor': 0.0,
            'dt_dectogen': 0.0,
            'dt_tipoitem': 1,
            'dt_valdto': -1,
            'dt_valdtogen': 0.0,
            'dt_codsec': sec_codigo,
            'dai_imp0': None,
            'dai_impg': None,
            'dai_ise': None,
            'dai_ice': None,
            'icdp_grabaiva': False,
            'icdp_valoriva': 0,  # Se agrega este campo para registrar el monto del iva que debe registrar
            'icdp_modcontab': 0,
            'tipic_id': 0,
            'ice_stock': 0,
            'subtotal': 0.0,
            'subtforiva': 0.0,
            'subtforiva15': 0.0,
            'subtforiva5': 0.0,
            'ivaval': 0.0,
            'ivaval5': 0.0,
            'ivaval15': 0.0,
            'total': 0.0
        }

        return form

    def listar_documentos(self, per_codigo, clase=1, sec_codigo=0):
        """
        Listar facturas validas de un referente especificaco
        :param per_codigo:
        :param clase:
        :return:
        """
        tracodin = "1,2"
        if int(clase) == 2:
            tracodin = "7"

        sql_sec_codigo = ""
        if sec_codigo > 0:
            sql_sec_codigo = " and a.sec_codigo = {0}".format(sec_codigo)

        sql = """
        select a.trn_codigo, a.trn_fecreg, a.trn_fecha, a.trn_compro, a.trn_observ,
        pagos.efectivo, pagos.credito, pagos.saldopend, pagos.total
         from tasiento a
         join get_pagos_factura(a.trn_codigo) as pagos(efectivo numeric, credito numeric, total numeric, saldopend numeric, trncodigo integer)
         on a.trn_codigo = pagos.trncodigo 
         where per_codigo = {percodigo}
        and tra_codigo in ({tracodin}) and trn_valido = 0 and trn_docpen = 'F' {sql_sec} order by trn_fecha desc 
        """.format(percodigo=per_codigo, tracodin=tracodin, sql_sec=sql_sec_codigo)

        tupla_desc = (
            'trn_codigo', 'trn_fecreg', 'trn_fecha', 'trn_compro', 'trn_observ', 'efectivo', 'credito', 'saldopend',
            'total')

        facturas = self.all(sql, tupla_desc)

        totales = self.totalizar_facturas(listafact=facturas)

        return facturas, totales

    def get_detdoc_foredit(self, trn_codigo, dt_tipoitem, joinarts=True):
        joinartsql = 'a.art_codigo'
        if not joinarts:
            joinartsql = 'a.cta_codigo'

        sqlic_nombre = 'b.ic_nombre'
        if dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
            sqlic_nombre = 'b.ic_alias as ic_nombre'

        sql = """
            select a.dt_codigo, a.trn_codigo, a.cta_codigo, a.art_codigo, a.per_codigo, a.pry_codigo, a.dt_cant, a.dt_precio, a.dt_debito,
            a.dt_preref, a.dt_decto, a.dt_valor, a.dt_dectogen, a.dt_tipoitem, a.dt_valdto, a.dt_valdtogen, a.dt_codsec, {icnombre},
            b.ic_clasecc, b.ic_code, dimp.dai_imp0, dimp.dai_impg, dimp.dai_ise, dimp.dai_ice, 
            der.dtpreiva as dt_precioiva, der.icdpgrabaiva as icdp_grabaiva, der.subt as subtotal, der.total, der.dtdectoin as dt_dectoin
            from tasidetalle a
            left join tasidetimp dimp on a.dt_codigo = dimp.dt_codigo
            join get_dataforedit_rowfact(a.dt_codigo) as der(dtcod integer, 
            dtcant numeric, 
            dtprecio numeric,
            dtpreref numeric,
            dtdecto numeric,
            dtdectogen numeric,
            daiimpg numeric,
             dtpreiva numeric,
             dtdectoin numeric,
             icdpgrabaiva boolean,
             subt numeric,
             ivaval numeric,
             total numeric) on der.dtcod = a.dt_codigo
            join titemconfig b on {joinart} = b.ic_id where dt_tipoitem = {dttipo} and trn_codigo = {trncod}
            order by a.dt_codigo
            """.format(joinart=joinartsql,
                       icnombre=sqlic_nombre,
                       dttipo=dt_tipoitem,
                       trncod=trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre', 'ic_clasecc', 'ic_code', 'dai_imp0',
                      'dai_impg', 'dai_ise', 'dai_ice', 'dt_precioiva', 'icdp_grabaiva', 'subtotal', 'total',
                      'dt_dectoin')

        detalles = self.all(sql, tupla_desc)

        return detalles

    def get_pagos_doc(self, trn_codigo):
        sql = """
        select a.trn_codigo, 
        pagos.efectivo, pagos.credito, pagos.saldopend, pagos.total
         from tasiento a
         join get_pagos_factura(a.trn_codigo) as pagos(efectivo numeric, credito numeric, total numeric, saldopend numeric, trncodigo integer)
         on a.trn_codigo = pagos.trncodigo 
         where a.trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('trn_codigo', 'efectivo', 'credito', 'saldopend', 'total')
        return self.first(sql, tupla_desc)

    def get_detalles_doc(self, trn_codigo, dt_tipoitem, joinarts=True):

        joinartsql = 'a.art_codigo'
        if not joinarts:
            joinartsql = 'a.cta_codigo'

        sqlic_nombre = 'b.ic_nombre'
        if dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
            sqlic_nombre = """case when coalesce(b.ic_alias,'')='' then b.ic_nombre else b.ic_alias end as ic_nombre"""

        sql = """
                select a.dt_codigo, trn_codigo, cta_codigo, art_codigo, per_codigo, pry_codigo, dt_cant, dt_precio, dt_debito,
                dt_preref, dt_decto, dt_valor, dt_dectogen, dt_tipoitem, dt_valdto, dt_valdtogen, dt_codsec, {icnombre},
                b.ic_clasecc, b.ic_code, dimp.dai_imp0, dimp.dai_impg, dimp.dai_ise, dimp.dai_ice
                from tasidetalle a
                left join tasidetimp dimp on a.dt_codigo = dimp.dt_codigo
                join titemconfig b on {joinart} = b.ic_id where dt_tipoitem = {dttipo} and trn_codigo = {trncod}
                order by a.dt_codigo
                """.format(joinart=joinartsql,
                           icnombre=sqlic_nombre,
                           dttipo=dt_tipoitem,
                           trncod=trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre', 'ic_clasecc', 'ic_code', 'dai_imp0',
                      'dai_impg', 'dai_ise', 'dai_ice')

        detalles = self.all(sql, tupla_desc)

        return detalles

    def get_cabecera_asiento(self, trn_codigo):
        sql = """
        select trn_codigo,
        dia_codigo,
        trn_fecreg,
        trn_compro,
        get_small_trncompro(trn_compro) as secuencia,
        trn_fecha,
        trn_valido,
        case 
        when trn_valido = 0 then 'Valido'
        when trn_valido = 1 then 'Anulado'
        when trn_valido = 2 then 'Errado'
        else 'Desconocido' end as estado,
        trn_docpen,
        trn_pagpen,
        sec_codigo,
        a.per_codigo,
        a.tra_codigo,
        tra.tra_nombre,
        a.us_id,
        us.us_cuenta,
        trn_observ,
        tdv_codigo,
        fol_codigo,
        trn_tipcom,
        trn_suscom,
        per_codres,
        trn_impref,
        coalesce(per.per_nombres,'')||' '||coalesce(per.per_apellidos,'') as referente,
        coalesce(vu.referente, '') as refusercrea,
        per.per_ciruc,
        per.per_telf,
        per.per_direccion,
        per.per_email
         from tasiento a 
         join tpersona per on a.per_codigo = per.per_id
         join ttransacc tra on a.tra_codigo = tra.tra_codigo 
         join tfuser us on a.us_id = us.us_id  
         left join vusers vu on vu.us_id = a.us_id
         where trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('trn_codigo',
                      'dia_codigo',
                      'trn_fecreg',
                      'trn_compro',
                      'secuencia',
                      'trn_fecha',
                      'trn_valido',
                      'estado',
                      'trn_docpen',
                      'trn_pagpen',
                      'sec_codigo',
                      'per_codigo',
                      'tra_codigo',
                      'tra_nombre',
                      'us_id',
                      'us_cuenta',
                      'trn_observ',
                      'tdv_codigo',
                      'fol_codigo',
                      'trn_tipcom',
                      'trn_suscom',
                      'per_codres',
                      'trn_impref',
                      'referente',
                      'refusercrea',
                      'per_ciruc',
                      'per_telf',
                      'per_direccion',
                      'per_email')

        tasiento = self.first(sql, tupla_desc)
        return tasiento

    def get_documento(self, trn_codigo, foredit=False):
        tasiento = self.get_cabecera_asiento(trn_codigo=trn_codigo)
        if foredit:
            detalles = self.get_detdoc_foredit(trn_codigo=trn_codigo, dt_tipoitem=1)
        else:
            detalles = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=1)
        pagos = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=2, joinarts=False)
        pagosdoc = self.get_pagos_doc(trn_codigo=trn_codigo)
        impuestos = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=3, joinarts=False)
        totales = self.calcular_totales(detalles)

        # Sumar todos los items del articulo
        total = 0.0
        for item in detalles:
            total += item['dt_valor']

        total = round(total, 2)
        tasiento['totalfact'] = total

        totalpagos = 0.0
        pagosobj = {'efectivo': 0.0, 'credito': 0.0, 'total': 0.0}
        for pago in pagos:
            totalpagos += pago['dt_valor']
            if pago['ic_clasecc'] == 'XC' or pago['ic_clasecc'] == 'XP':
                pagosobj['credito'] = numeros.roundm2(pago['dt_valor'])
            else:
                pagosobj['efectivo'] = numeros.roundm2(pago['dt_valor'])

        pagosobj['total'] = numeros.roundm2(totalpagos)

        datosref = {}
        if tasiento is not None and 'per_codigo' in tasiento:
            per_codigo = tasiento['per_codigo']
            tpersondao = TPersonaDao(self.dbsession)
            datosref = tpersondao.buscar_porperid_full(per_id=per_codigo)

        asifacte = TasiFacteDao(self.dbsession)
        is_compele = asifacte.es_compro_elec(trn_codigo=trn_codigo)
        factele_info = asifacte.get_datos_facte(trn_codigo=trn_codigo)

        return {
            'tasiento': tasiento,
            'detalles': detalles,
            'datosref': datosref,
            'pagos': pagos,
            'pagosobj': pagosobj,
            'pagosdoc': pagosdoc,
            'impuestos': impuestos,
            'totales': totales,
            'isCompele': is_compele,
            'facteleinfo': factele_info
        }

    @staticmethod
    def calcular_totales(detalles):
        gsubtotal = 0.0
        gsubtotal12 = 0.0
        gsubtotal0 = 0.0
        giva = 0.0
        gdescuentos = 0.0
        gtotal = 0.0
        descglobal = 0.0
        subtiva15 = 0.0
        subtiva5 = 0.0
        giva15 = 0.0
        giva5 = 0.0

        for det in detalles:
            dt_cant = det['dt_cant']
            dai_impg = det['dai_impg']
            dt_decto = det['dt_decto']
            dt_decto_cant = dt_decto * dt_cant
            if det['dt_valdto'] >= 0.0:
                dt_decto_cant = dt_decto
            dt_dectogen = det['dt_dectogen']
            dt_precio = det['dt_precio']
            subtotal = dt_cant * dt_precio
            subtforiva = (dt_cant * dt_precio) - (dt_decto_cant + dt_dectogen)
            ivaval = 0.0
            dt_dectogeniva = dt_dectogen
            iva15 = 0.0
            iva5 = 0.0
            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                gsubtotal12 += subtforiva
                dt_dectogeniva = numeros.sumar_iva(dt_dectogen, dai_impg)

                if dai_impg == ctes_facte.VALOR_IVA_15:
                    subtiva15 += subtforiva
                    iva15 = ivaval
                elif dai_impg == ctes_facte.VALOR_IVA_5:
                    subtiva5 += subtforiva
                    iva5 = ivaval
            else:
                gsubtotal0 += subtotal

            ftotal = subtotal - (dt_decto_cant + dt_dectogen) + ivaval
            giva += ivaval
            giva15 += iva15
            giva5 += iva5
            gdescuentos += (dt_decto_cant + dt_dectogen)
            gtotal += ftotal
            gsubtotal += subtotal
            descglobal += dt_dectogeniva

        return {
            'subtotal': numeros.roundm4(gsubtotal),
            'subtotal12': numeros.roundm4(gsubtotal12),
            'subtotal15': numeros.roundm4(subtiva15),
            'subtotal5': numeros.roundm4(subtiva5),
            'subtotal0': numeros.roundm4(gsubtotal0),
            'iva': numeros.roundm4(giva),
            'iva15': numeros.roundm4(giva15),
            'iva5': numeros.roundm4(giva5),
            'descuentos': numeros.roundm4(gdescuentos),
            'total': numeros.roundm2(gtotal),
            'descglobalin': numeros.roundm4(descglobal),
            'descglobal': numeros.roundm4(descglobal),
            'descglobaltipo': '1'
        }

    @staticmethod
    def get_form_pago():
        form = {
            'cta_codigo': 0,
            'dt_debito': 1,
            'ic_nombre': '',
            'dt_valor': 0.0,
            'dt_codsec': 1
        }
        return form

    def editar_asiento(self, formcab, formref, useredita, detalles, obs):
        trn_codigo = formcab['trn_codigo']
        tasiento = self.find_entity_byid(trn_codigo=trn_codigo)
        tasiauddao = TAsientoAudDao(self.dbsession)

        if tasiento is not None:
            tasiauddao.save_anula_transacc(tasiento=tasiento, user_anula=useredita, obs_anula=obs)
            new_trn_codigo = self.crear_asiento(formcab=formcab, formref=formref, usercrea=useredita, detalles=detalles)
        else:
            raise ErrorValidacionExc('No pude recuperar datos del asiento contable (cod:{0})'.format(trn_codigo))

        return new_trn_codigo

    def crear_asiento_cxcp_fromref(self, formcab, formref, usercrea, detalles):
        persodao = TPersonaDao(self.dbsession)
        per_codigo = int(formref['per_id'])
        if per_codigo == 0:
            per_codigo = persodao.crear(form=formref)

        tasiento = self.aux_set_datos_tasiento(usercrea=usercrea, per_codigo=per_codigo, formcab=formcab)
        trn_codigo = tasiento.trn_codigo

        self.chk_sum_debe_haber(detalles)

        creditodao = TAsicreditoDao(self.dbsession)
        for detalle in detalles:
            dt_valor = float(detalle['dt_valor'])
            if dt_valor > 0.0:
                dt_codigo = self.save_tasidet_asiento(trn_codigo=trn_codigo, per_codigo=per_codigo, detalle=detalle,
                                                      roundvalor=True)
                ic_clasecc = detalle['ic_clasecc']
                if creditodao.is_clasecc_cred(ic_clasecc):
                    cre_tipo = creditodao.get_cre_tipo(ic_clasecc)
                    formcre = creditodao.get_form_asi(dt_codigo=dt_codigo, trn_fecreg=formcab['trn_fecreg'],
                                                      monto_cred=dt_valor, cre_tipo=cre_tipo)
                    creditodao.crear(form=formcre)

        return trn_codigo

    def crear_asiento(self, formcab, formref, usercrea, detalles, roundvalor=True, update_datosref=True):
        persodao = TPersonaDao(self.dbsession)

        per_codigo = int(formref['per_id'])
        if per_codigo == 0:
            per_codigo = persodao.crear(form=formref)
        elif per_codigo > 0 and update_datosref:
            per_codigo = persodao.actualizar(per_id=per_codigo, form=formref)

        tasiento = self.aux_set_datos_tasiento(usercrea=usercrea, per_codigo=per_codigo, formcab=formcab)
        trn_codigo = tasiento.trn_codigo

        self.chk_sum_debe_haber(detalles)

        for detalle in detalles:
            if float(detalle['dt_valor']) > 0.0:
                self.save_tasidet_asiento(trn_codigo=trn_codigo, per_codigo=per_codigo, detalle=detalle,
                                          roundvalor=roundvalor)

        tbillhist_dao = TBilleteraHistoDao(self.dbsession)
        tbillhist_dao.generate_history_mov(trn_codigo)

        return trn_codigo

    def crear_asiento_cxcp(self, formcab, per_codigo, user_crea, detalles):
        """
        Este metodo se usa para registrar un abono de una cuenta por cobrar o pagar
        :param formcab:
        :param per_codigo:
        :param user_crea:
        :param detalles:
        :return:
        """

        tasiento = self.aux_set_datos_tasiento(usercrea=user_crea, per_codigo=per_codigo, formcab=formcab)
        trn_codigo = tasiento.trn_codigo

        creditodao = TAsicreditoDao(self.dbsession)
        for detalle in detalles:
            dt_valor = float(detalle['dt_valor'])
            if dt_valor > 0.0:
                dt_codigo = self.save_tasidet_asiento(trn_codigo=trn_codigo, per_codigo=per_codigo, detalle=detalle,
                                                      roundvalor=True)
                ic_clasecc = detalle['ic_clasecc']

                if creditodao.is_clasecc_cred(ic_clasecc):
                    cre_tipo = creditodao.get_cre_tipo(ic_clasecc)
                    tra_codigo_int = int(formcab['tra_codigo'])
                    if (tra_codigo_int == ctes.TRA_COD_ABO_COMPRA) or (
                            tra_codigo_int == ctes.TRA_COD_ABO_VENTA):
                        abonodao = TAsiAbonoDao(self.dbsession)
                        abonodao.crear(dt_codigo, detalle['dt_codcred'], dt_valor)
                    else:
                        formcre = creditodao.get_form_asi(dt_codigo=dt_codigo, trn_fecreg=formcab['trn_fecreg'],
                                                          monto_cred=dt_valor, cre_tipo=cre_tipo)
                        creditodao.crear(form=formcre)
        billhisto_dao = TBilleteraHistoDao(self.dbsession)
        billhisto_dao.generate_history_mov(trn_codigo=trn_codigo)
        transaccpdv_dao = TTransaccPdvDao(self.dbsession)
        resestabsec = transaccpdv_dao.get_estabptoemi_secuencia(alm_codigo=0,
                                                                tra_codigo=ctes.TRA_COD_ASI_CONTABLE,
                                                                tdv_codigo=0, sec_codigo=0)
        if resestabsec is None:
            raise ErrorValidacionExc(
                'Error al tratar de generar secuencia para el registro contable asociado')

        trn_compro_rel = self._get_trn_compro("000000", resestabsec['secuencia'])

        transaccpdv_dao.gen_secuencia(tps_codigo=resestabsec['tps_codigo'], secuencia=resestabsec['secuencia'])
        tasiento.trn_compro_rel = trn_compro_rel

        return trn_codigo

    def aux_cambia_estado(self, trn_codigo, user_do, obs, new_state):
        tasiento = self.find_entity_byid(trn_codigo=trn_codigo)
        if tasiento is not None:
            current_trn_valido = tasiento.trn_valido
            current_trn_docpen = tasiento.trn_docpen
            if tasiento.trn_valido != new_state:
                tasiento.trn_valido = new_state
                self.dbsession.add(tasiento)

                tasientoauddao = TAsientoAudDao(self.dbsession)
                aud_accion = 0
                if int(new_state) == 1:
                    aud_accion = ctes.AUD_ASIENTO_ANULAR
                elif int(new_state) == 2:
                    aud_accion = ctes.AUD_ASIENTO_ERRAR

                tasientoauddao.craer(trn_codigo=trn_codigo, aud_accion=aud_accion, aud_user=user_do, aud_obs=obs)

                # Verificamos si se trata de aun asiento en el que interviene una cuenta tipo billetera, se debe totalizar nuevamente
                histobill_dao = TBilleteraHistoDao(self.dbsession)
                if current_trn_valido == 0 and current_trn_docpen == 'F':
                    histobill_dao.destroy_mov(trn_codigo=trn_codigo)

    def is_transacc_abono(self, trn_codigo):
        sql = "select tra_codigo from tasiento where trn_codigo = {0}".format(trn_codigo)
        tra_codigo = self.first_col(sql, 'tra_codigo')
        if tra_codigo is not None:
            return tra_codigo == ctes.TRA_COD_ABO_VENTA or tra_codigo == ctes.TRA_COD_ABO_COMPRA
        return False

    def is_transacc_in_state(self, trn_codigo, state):
        sql = "select trn_valido from tasiento where trn_codigo = {0}".format(trn_codigo)
        trn_valido = self.first_col(sql, 'trn_valido')
        if trn_valido is not None:
            return int(trn_valido) == int(state)
        return False

    def aux_anular_errar(self, trn_codigo, user_anula, obs_anula, new_state):
        if not self.is_transacc_in_state(trn_codigo=trn_codigo, state=new_state):
            if not self.is_transacc_abono(trn_codigo):
                tasicreddao = TAsicreditoDao(self.dbsession)
                tasiabodao = TAsiAbonoDao(self.dbsession)
                datoscred = tasicreddao.find_datoscred_intransacc(trn_codigo=trn_codigo)
                if datoscred is not None and datoscred['cre_codigo'] > 0:
                    if tasiabodao.is_transacc_with_abonos(dtcodcred=datoscred['dt_codigo']):
                        raise ErrorValidacionExc(
                            'No se puede anular esta transacción, existen abonos registrados, favor anular primero estos abonos')

            self.aux_cambia_estado(trn_codigo, user_do=user_anula, obs=obs_anula, new_state=new_state)
        else:
            raise ErrorValidacionExc('Esta transacción ya ha sido anulada, favor verificar')

    def is_asiento_mayorizado(self, trn_codigo):
        sql = "select trn_mayorizado from tasiento where trn_codigo = {0}".format(trn_codigo)
        trn_mayorizado = self.first_col(sql, 'trn_mayorizado')
        return trn_mayorizado is not None and trn_mayorizado

    def anular(self, trn_codigo, user_anula, obs_anula):
        if self.is_asiento_mayorizado(trn_codigo):
            raise ErrorValidacionExc('No es posible anular esta transacción ya ha sido mayorizada')
        self.aux_anular_errar(trn_codigo, user_anula, obs_anula, new_state=1)

    def marcar_errado(self, trn_codigo, user_do):
        self.aux_anular_errar(trn_codigo, user_anula=user_do, obs_anula='', new_state=2)

    def update_trn_docpen(self, trn_codigo, trn_docpen_value):
        tasiento = self.find_entity_byid(trn_codigo)
        if tasiento is not None:
            tasiento.trn_docpen = trn_docpen_value
            self.dbsession.add(tasiento)

    def listar_transacc_min(self, tipo):
        sql = "select tra_codigo, tra_nombre from ttransacc where tra_codigo in(7) "
        if int(tipo) == 1:
            sql = "select tra_codigo, tra_nombre from ttransacc where tra_codigo in(1,2) "
        elif int(tipo) == 3:
            sql = "select tra_codigo, tra_nombre from ttransacc where tra_codigo in(4) "

        tupla_desc = ('tra_codigo', 'tra_nombre')
        return self.all(sql, tupla_desc)

    def duplicar_comprobante(self, trn_codigo, user_crea, tra_codigo):
        tasiento = self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()
        if tasiento is not None:
            detalles = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=ctes.DT_TIPO_ITEM_DETALLE)

            for detalle in detalles:
                for key in detalle.keys():
                    if not cadenas.es_nonulo_novacio(detalle[key]):
                        detalle[key] = None

            pagos = self.get_detalles_doc(trn_codigo=trn_codigo, joinarts=False, dt_tipoitem=ctes.DT_TIPO_ITEM_PAGO)

            totales = self.calcular_totales(detalles)

            ttpdvdao = TtpdvDao(self.dbsession)
            alm_codigo = ttpdvdao.get_alm_codigo_from_sec_codigo(tasiento.sec_codigo)
            formcab = self.get_form_cabecera(tra_codigo=tra_codigo, alm_codigo=alm_codigo,
                                             sec_codigo=tasiento.sec_codigo, tdv_codigo=tasiento.tdv_codigo,
                                             tra_emite=1)
            formcab['trn_docpen'] = 'F'
            formcab['tra_codigo'] = tra_codigo

            formpersona = {'per_id': tasiento.per_codigo}
            return self.crear(form=formcab, form_persona=formpersona, user_crea=user_crea, detalles=detalles,
                              pagos=pagos, totales=totales)

    def generar_nota_credito(self, trn_codfactura, alm_codigo, sec_codigo, tdv_codigo, usercrea):
        return self.gen_nota_credito(trn_codfactura, alm_codigo, sec_codigo, tdv_codigo, usercrea)

    def editar(self, trn_codigo, user_edita, sec_codigo, detalles, pagos, totales, formcab=None, formref=None,
               creaupdref=False):
        tasiauddao = TAsientoAudDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)
        tasicredao = TAsicreditoDao(self.dbsession)
        tasiabodao = TAsiAbonoDao(self.dbsession)
        auxlogicasi = AuxLogicAsiDao(self.dbsession)

        datoscred = tasicredao.find_datoscred_intransacc(trn_codigo=trn_codigo)
        trn_codorig = trn_codigo
        tasiento = self.find_entity_byid(trn_codorig)
        iscontab = False

        if tasiento is not None:
            tra_codigo = tasiento.tra_codigo
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)

            if ttransacc is not None:
                iscontab = ttransacc['tra_contab'] == 1

            self.dbsession.expunge(tasiento)
            make_transient(tasiento)
        else:
            raise ErrorValidacionExc('No pude recupar información de la transacción (tr_cod:{0})'.format(trn_codigo))

        tasiento.trn_codigo = None
        tasiento.sec_codigo = sec_codigo
        tasiento.us_id = user_edita
        tasiento.trn_valido = 0

        if formref is not None:
            per_codigo, per_ciruc = self.aux_save_datos_ref(formref=formref, creaupdref=creaupdref)
            tasiento.per_codigo = per_codigo

        if formcab is not None:
            if 'trn_fecreg' in formcab:
                tasiento.trn_fecreg = fechas.parse_cadena(formcab['trn_fecreg'])
            if 'trn_observ' in formcab:
                tasiento.trn_observ = cadenas.strip_upper(formcab['trn_observ'])

        tbillhist_dao = TBilleteraHistoDao(self.dbsession)
        # Se debe anular la factura anterior
        tasiauddao.save_anula_transacc(tasiento=self.find_entity_byid(trn_codorig), user_anula=user_edita)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        tbillhist_dao.destroy_mov(trn_codigo=trn_codorig)

        new_trn_codigo = tasiento.trn_codigo

        tbillhist_dao.generate_history_mov(trn_codigo=new_trn_codigo)

        valdebehaber = []
        auxlogicasi.save_dets_imps_fact(detalles=detalles, tasiento=tasiento, totales=totales,
                                        valdebehaber=valdebehaber)

        abonos = None
        totalabonos = 0.0
        if datoscred is not None:
            abonos = tasiabodao.get_abonos_entity(datoscred['dt_codigo'])
            totalabonos = tasiabodao.get_total_abonos(dt_codcre=datoscred['dt_codigo'])

        per_codigo = tasiento.per_codigo
        sumapagos = 0.0
        for pago in pagos:
            valorpago = float(pago['dt_valor'])
            ic_clasecc = pago['ic_clasecc']
            if valorpago > 0.0:
                dt_codigo = auxlogicasi.save_tasidet_pago(trn_codigo=new_trn_codigo, per_codigo=per_codigo, pago=pago)
                sumapagos += valorpago
                valdebehaber.append({'dt_debito': pago['dt_debito'], 'dt_valor': valorpago})
                if tasicredao.is_clasecc_cred(ic_clasecc):
                    totalaboround = numeros.roundm2(totalabonos)
                    totalcredround = numeros.roundm2(pago['dt_valor'])
                    # Validar monto del credito no puede ser menos al total de abonos previos realizados
                    if totalcredround < totalaboround:
                        raise ErrorValidacionExc(
                            'No es posible editar este documento, existen abonos realizados por un total de ({0}) y el crédito actual es de ({1}), favor verificar'.format(
                                totalaboround, totalcredround))
                    else:
                        new_cre_saldopen = totalcredround - totalaboround

                    cre_tipo = tasicredao.get_cre_tipo(ic_clasecc)
                    formcre = tasicredao.get_form_asi(dt_codigo=dt_codigo,
                                                      trn_fecreg=fechas.parse_fecha(tasiento.trn_fecreg),
                                                      monto_cred=valorpago, cre_tipo=cre_tipo)
                    new_cre_codigo = tasicredao.crear(form=formcre)

                    # Si hay abonos asociados se debe pasar estos abonos a la nueva factdura
                    if abonos is not None:
                        for abono in abonos:
                            abono.dt_codcre = dt_codigo
                            self.dbsession.add(abono)

                    # Actualizar el saldo pendiente del credito en funcion de abonos anteriores registrados
                    tasicredao.upd_cre_saldopen(cre_codigo=new_cre_codigo, cre_saldopen=new_cre_saldopen)

        totalform = numeros.roundm(float(totales['total']), 2)
        totalsuma = numeros.roundm(sumapagos, 2)

        if totalform != totalsuma:
            raise ErrorValidacionExc(
                'El total de la factura ({0}) no coincide con la suma de los pagos ({1})'.format(totalform, totalsuma))

        if iscontab:  # Vericar que sumen debe y haber correctamente
            auxlogicasi.chk_sum_debe_haber(valdebehaber)

        return new_trn_codigo

    def aux_save_datos_ref(self, formref, creaupdref=True):
        personadao = TPersonaDao(self.dbsession)
        per_codigo = int(formref['per_id'])

        if 'per_ciruc' in formref:
            per_ciruc = formref['per_ciruc']
        else:
            per_ciruc = None

        if creaupdref and per_codigo >= 0:
            if per_codigo is not None and per_codigo > 0:
                personadao.actualizar(per_id=per_codigo, form=formref)
            else:
                persona = personadao.buscar_porciruc(per_ciruc=per_ciruc)
                if persona is not None:
                    per_codigo = persona[0]['per_id']
                    personadao.actualizar(per_id=per_codigo, form=formref)
                else:
                    per_codigo = personadao.crear(form=formref)

        return per_codigo, per_ciruc

    def crear(self, form, form_persona, user_crea, detalles, pagos, totales, creaupdpac=True, creabono=False,
              gen_secuencia=True):
        """
        creabono: True indica que se debe registrar un abono de una cuenta por pagar asociado
        """

        per_codigo, per_ciruc = self.aux_save_datos_ref(formref=form_persona, creaupdref=creaupdpac)

        tasiento = self.aux_set_datos_tasiento(usercrea=user_crea, per_codigo=per_codigo,
                                               formcab=form, per_ciruc=per_ciruc, gen_secuencia=gen_secuencia)
        trn_codigo = tasiento.trn_codigo
        valdebehaber = []
        self.save_dets_imps_fact(detalles=detalles, tasiento=tasiento, totales=totales,
                                 valdebehaber=valdebehaber)

        sumapagos = 0.0
        creditodao = TAsicreditoDao(self.dbsession)
        abonodao = TAsiAbonoDao(self.dbsession)

        pagos_validos = filter(lambda pago: cadenas.es_nonulo_novacio(pago['dt_valor']), pagos)

        for pago in pagos_validos:
            valorpago = float(pago['dt_valor'])
            if valorpago > 0.0:
                dt_codigo = self.save_tasidet_pago(trn_codigo=trn_codigo, per_codigo=per_codigo, pago=pago)
                sumapagos += valorpago
                valdebehaber.append({'dt_debito': pago['dt_debito'], 'dt_valor': valorpago})
                ic_clasecc = pago['ic_clasecc']
                if creditodao.is_clasecc_cred(ic_clasecc):
                    if creabono:
                        dt_codcre = pago['dt_codcre']
                        abonodao.crear(dt_codigo=dt_codigo, dt_codcre=dt_codcre, monto_abono=valorpago)
                    else:
                        cre_tipo = creditodao.get_cre_tipo(ic_clasecc)
                        formcre = creditodao.get_form_asi(dt_codigo=dt_codigo, trn_fecreg=form['trn_fecreg'],
                                                          monto_cred=valorpago, cre_tipo=cre_tipo)
                        creditodao.crear(form=formcre)

        totalform = numeros.roundm(float(totales['total']), 2)
        totalsuma = numeros.roundm(sumapagos, 2)

        if totalform != totalsuma:
            raise ErrorValidacionExc(
                'El total de la factura ({0}) no coincide con la suma de los pagos ({1})'.format(totalform, totalsuma))

        ttransaccdao = TTransaccDao(self.dbsession)
        ttransacc = ttransaccdao.get_ttransacc(tra_codigo=form['tra_codigo'])

        iscontab = None
        if ttransacc is not None:
            iscontab = ttransacc['tra_contab'] == 1

        if iscontab:
            self.chk_sum_debe_haber(valdebehaber)
            transaccpdv_dao = TTransaccPdvDao(self.dbsession)
            resestabsec = transaccpdv_dao.get_estabptoemi_secuencia(alm_codigo=0,
                                                                    tra_codigo=ctes.TRA_COD_ASI_CONTABLE,
                                                                    tdv_codigo=0, sec_codigo=0)
            if resestabsec is None:
                raise ErrorValidacionExc(
                    'Error al tratar de generar secuencia para el registro contable asociado')

            trn_compro_rel = self._get_trn_compro('000000', resestabsec['secuencia'])
            transaccpdv_dao.gen_secuencia(tps_codigo=resestabsec['tps_codigo'], secuencia=resestabsec['secuencia'])

            tasiento.trn_compro_rel = trn_compro_rel

        is_proforma = int(tasiento.tra_codigo) == ctes.TRA_COD_PROFORMA

        if not is_proforma:
            thistbill_dao = TBilleteraHistoDao(self.dbsession)
            thistbill_dao.generate_history_mov(trn_codigo)

        return trn_codigo
