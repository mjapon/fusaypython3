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

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasiento.auxlogicasi_dao import AuxLogicAsiDao
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento
from fusayrepo.logica.fusay.tasiento.tasientoaud_dao import TAsientoAudDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.timpuesto.timpuesto_dao import TImpuestoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
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

    def listar_movs_ctacontable(self, cta_codigo, desde, hasta):
        gridado = TGridDao(self.dbsession)
        resgrid = gridado.run_grid('libromayor', cta_codigo=cta_codigo,
                                   desde=fechas.format_cadena_db(desde),
                                   hasta=fechas.format_cadena_db(hasta))
        data = resgrid['data']
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

    def listar_grid_ventas(self, desde, hasta, filtro, tracod, tipo, sec_id):
        tgrid_dao = TGridDao(self.dbsession)
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
            if int(tipo) == 1:
                sqltra = "and a.tra_codigo in (1,2)"
            elif int(tipo) == 2:
                sqltra = "and a.tra_codigo in (7)"
        else:
            sqltra = "and a.tra_codigo in ({0})".format(tracod)

        swhere = ' {0} {1} and a.sec_codigo = {2}'.format(sqltra, sqladc, sec_id)

        data = tgrid_dao.run_grid(grid_nombre='ventas', swhere=swhere)

        # Totalizar
        totales = self.totalizar_facturas(listafact=data['data'])

        return data, totales

    def aux_get_cod_cuentas_repconta(self, cuentas, codcuentas):
        for cuenta in cuentas:
            dbdata_it = cuenta['dbdata']
            codcuentas.append('\'{0}\''.format(dbdata_it['ic_id']))
            if 'children' in cuenta:
                codcuentas = self.aux_get_cod_cuentas_repconta(cuentas=cuenta['children'], codcuentas=codcuentas)

        return codcuentas

    def aux_totalizar_nodo(self, nodo, planctasdict):
        totalnodo = 0.0
        if 'children' in nodo and len(nodo['children']) > 0:
            for hijonodo in nodo['children']:
                totalnodo += self.aux_totalizar_nodo(hijonodo, planctasdict)
            nodo['total'] = numeros.roundm2(totalnodo)
        else:
            itemdb = nodo['dbdata']
            item_codcta = itemdb['ic_id']
            if item_codcta in planctasdict:
                nodo['total'] = numeros.roundm2(planctasdict[item_codcta]['total'])

            totalnodo = numeros.roundm2(nodo['total'])

        return totalnodo

    def aux_tree_to_list(self, nodo, alllist, acpasress):
        codnodo = nodo['dbdata']['ic_code']
        acpasress[codnodo] = {'total': nodo['total']}
        nodo['expanded'] = True
        alllist.append(
            {'codigo': codnodo, 'nombre': nodo['dbdata']['ic_nombre'], 'total': numeros.roundm2(nodo['total'])}
        )
        if 'children' in nodo and len(nodo['children']) > 0:
            for hijonodo in nodo['children']:
                self.aux_tree_to_list(hijonodo, alllist, acpasress)

    def buid_rep_conta(self, desde, hasta, wherecodparents, sec_id, isestadores=False):

        sqlbalgen = """
        select ic.ic_id, ic_code, ic_nombre, ic_padre, ic_haschild, 0.0 as total 
        from titemconfig ic
        join titemconfig_sec ics on  ics.ic_id = ic.ic_id and ics.sec_id ={sec_id} 
        where ic.tipic_id = 3 and ic.ic_estado = 1 and ({andwhere})
        order by ic_code asc
        """.format(andwhere=wherecodparents, sec_id=sec_id)

        tdgb = ('ic_id', 'ic_code', 'ic_nombre', 'ic_padre', 'ic_haschild', 'total')
        planctabalg = self.all(sqlbalgen, tdgb)

        planctasdict = {}
        for item in planctabalg:
            planctasdict[item['ic_id']] = item

        sql = """
        select det.cta_codigo, round(sum(det.dt_debito*det.dt_valor),2) as total 
        from tasidetalle det
        join tasiento t on det.trn_codigo = t.trn_codigo 
        join titemconfig ic on det.cta_codigo = ic.ic_id
        where
        t.tra_codigo = {0} and t.trn_valido = 0 and  t.trn_fecreg between '{1}' and '{2}'
        group by det.cta_codigo order by det.cta_codigo
        """.format(ctes.TRA_COD_ASI_CONTABLE,
                   fechas.format_cadena_db(desde),
                   fechas.format_cadena_db(hasta))

        tupla_desc = ('cta_codigo', 'total')
        result = self.all(sql, tupla_desc)
        for item in result:
            if item['cta_codigo'] in planctasdict:
                planctasdict[item['cta_codigo']]['total'] = item['total']

        itemconfigdao = TItemConfigDao(self.dbsession)
        if isestadores:
            treebg = itemconfigdao.build_tree_estado_resultados(sec_id=sec_id)
        else:
            treebg = itemconfigdao.build_tree_balance_general(sec_id=sec_id)

        for item in treebg:
            item['total'] = self.aux_totalizar_nodo(item, planctasdict)

        resultlist = []
        parentsdict = {}
        for item in treebg:
            self.aux_tree_to_list(item, resultlist, parentsdict)

        parentestres = {}
        restulttree = treebg
        if not isestadores:
            # Debe generar el resultado del ejercicio:
            wherecodparents = "ic_code like '4%' or ic_code like '5%'"
            resultestres, parentestres, auxparentestres, auxrestree = self.buid_rep_conta(desde, hasta,
                                                                                          wherecodparents,
                                                                                          sec_id=sec_id,
                                                                                          isestadores=True)
        return resultlist, parentsdict, parentestres, restulttree

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

        return {
            'cabecera': formasiento,
            'detalles': detalles,
            'totales': totales
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
            'dt_dectoin': 0.0,
            'dt_valor': 0.0,
            'dt_dectogen': 0.0,
            'dt_tipoitem': 1,
            'dt_valdto': 0.0,
            'dt_valdtogen': 0.0,
            'dt_codsec': sec_codigo,
            'dai_imp0': None,
            'dai_impg': None,
            'dai_ise': None,
            'dai_ice': None,
            'icdp_grabaiva': False,
            'icdp_modcontab': 0,
            'tipic_id': 0,
            'ice_stock': 0,
            'subtotal': 0.0,
            'ivaval': 0.0,
            'total': 0.0
        }

        return form

    def listar_documentos(self, per_codigo, clase=1):
        """
        Listar facturas validas de un referente especificaco
        :param per_codigo:
        :param clase:
        :return:
        """
        tracodin = "1,2"
        if int(clase) == 2:
            tracodin = "7"

        sql = """
        select a.trn_codigo, a.trn_fecreg, a.trn_fecha, a.trn_compro, a.trn_observ,
        pagos.efectivo, pagos.credito, pagos.saldopend, pagos.total
         from tasiento a
         join get_pagos_factura(a.trn_codigo) as pagos(efectivo numeric, credito numeric, total numeric, saldopend numeric, trncodigo integer)
         on a.trn_codigo = pagos.trncodigo 
         where per_codigo = {percodigo}
        and tra_codigo in ({tracodin}) and trn_valido = 0 and trn_docpen = 'F' order by trn_fecha desc 
        """.format(percodigo=per_codigo, tracodin=tracodin)

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
            der.dtpreiva as dt_precioiva, der.icdpgrabaiva as icdp_grabaiva, der.subt as subtotal, der.total, der.dtdecto as dt_dectoin
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

    def get_detalles_doc(self, trn_codigo, dt_tipoitem, joinarts=True):

        joinartsql = 'a.art_codigo'
        if not joinarts:
            joinartsql = 'a.cta_codigo'

        sqlic_nombre = 'b.ic_nombre'
        if dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
            sqlic_nombre = 'b.ic_alias as ic_nombre'

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
        per.per_direccion
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
                      'per_direccion')

        tasiento = self.first(sql, tupla_desc)
        return tasiento

    def get_documento(self, trn_codigo, foredit=False):
        tasiento = self.get_cabecera_asiento(trn_codigo=trn_codigo)
        if foredit:
            detalles = self.get_detdoc_foredit(trn_codigo=trn_codigo, dt_tipoitem=1)
        else:
            detalles = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=1)
        pagos = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=2, joinarts=False)
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

        return {
            'tasiento': tasiento,
            'detalles': detalles,
            'datosref': datosref,
            'pagos': pagos,
            'pagosobj': pagosobj,
            'impuestos': impuestos,
            'totales': totales
        }

    @staticmethod
    def calcular_totales(detalles):
        gsubtotal = 0.0
        gsubtotal12 = 0.0
        gsubtotal0 = 0.0
        giva = 0.0
        gdescuentos = 0.0
        gtotal = 0.0

        for det in detalles:
            dt_cant = det['dt_cant']
            dai_impg = det['dai_impg']
            dt_decto = det['dt_decto']
            dt_precio = det['dt_precio']
            subtotal = dt_cant * dt_precio
            subtforiva = (dt_cant * dt_precio) - dt_decto
            ivaval = 0.0
            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                gsubtotal12 += subtforiva
            else:
                gsubtotal0 += subtotal

            ftotal = subtotal - dt_decto + ivaval
            giva += ivaval
            gdescuentos += dt_decto
            gtotal += ftotal
            gsubtotal += subtotal

        return {
            'subtotal': numeros.roundm2(gsubtotal),
            'subtotal12': numeros.roundm2(gsubtotal12),
            'subtotal0': numeros.roundm2(gsubtotal0),
            'iva': numeros.roundm2(giva),
            'descuentos': numeros.roundm2(gdescuentos),
            'total': numeros.roundm2(gtotal)
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

    def crear_asiento(self, formcab, formref, usercrea, detalles, roundvalor=True):
        persodao = TPersonaDao(self.dbsession)

        per_codigo = int(formref['per_id'])
        if per_codigo == 0:
            per_codigo = persodao.crear(form=formref)
        elif per_codigo > 0:
            per_codigo = persodao.actualizar(per_id=per_codigo, form=formref)

        tasiento = self.aux_set_datos_tasiento(usercrea=usercrea, per_codigo=per_codigo, formcab=formcab)
        trn_codigo = tasiento.trn_codigo

        self.chk_sum_debe_haber(detalles)

        for detalle in detalles:
            if float(detalle['dt_valor']) > 0.0:
                self.save_tasidet_asiento(trn_codigo=trn_codigo, per_codigo=per_codigo, detalle=detalle,
                                          roundvalor=roundvalor)

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

    def anular(self, trn_codigo, user_anula, obs_anula):
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

    def editar(self, trn_codigo, user_edita, sec_codigo, detalles, pagos, totales, formcab=None, formref=None,
               creaupdref=False):
        tasiauddao = TAsientoAudDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)
        tasicredao = TAsicreditoDao(self.dbsession)
        tasiabodao = TAsiAbonoDao(self.dbsession)
        auxlogicasi = AuxLogicAsiDao(self.dbsession)

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

        # Se debe anular la factura anterior
        tasiauddao.save_anula_transacc(tasiento=self.find_entity_byid(trn_codorig), user_anula=user_edita)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        new_trn_codigo = tasiento.trn_codigo

        valdebehaber = []
        auxlogicasi.save_dets_imps_fact(detalles=detalles, tasiento=tasiento, totales=totales,
                                        valdebehaber=valdebehaber)
        datoscred = tasicredao.find_datoscred_intransacc(trn_codigo=trn_codigo)
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

    def crear(self, form, form_persona, user_crea, detalles, pagos, totales, creaupdpac=True):

        per_codigo, per_ciruc = self.aux_save_datos_ref(formref=form_persona, creaupdref=creaupdpac)

        tasiento = self.aux_set_datos_tasiento(usercrea=user_crea, per_codigo=per_codigo,
                                               formcab=form, per_ciruc=per_ciruc)
        trn_codigo = tasiento.trn_codigo
        valdebehaber = []
        self.save_dets_imps_fact(detalles=detalles, tasiento=tasiento, totales=totales,
                                 valdebehaber=valdebehaber)

        sumapagos = 0.0
        creditodao = TAsicreditoDao(self.dbsession)
        for pago in pagos:
            valorpago = float(pago['dt_valor'])
            if valorpago > 0.0:
                dt_codigo = self.save_tasidet_pago(trn_codigo=trn_codigo, per_codigo=per_codigo, pago=pago)
                sumapagos += valorpago
                valdebehaber.append({'dt_debito': pago['dt_debito'], 'dt_valor': valorpago})
                ic_clasecc = pago['ic_clasecc']
                if creditodao.is_clasecc_cred(ic_clasecc):
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
        return trn_codigo
