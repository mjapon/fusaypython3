# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging
from datetime import datetime
from functools import reduce

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasidetimp.tasidetimp_model import TAsidetimp
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento, TAsientoAud
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.timpuesto.timpuesto_dao import TImpuestoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransaccimp.ttransaccimp_dao import TTransaccImpDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.utils import fechas, numeros, ctes, cadenas

log = logging.getLogger(__name__)


class TasientoDao(BaseDao):

    def find_entity_byid(self, trn_codigo):
        return self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()

    def get_form_asiento(self):
        formasiento = self.get_form_cabecera(tra_codigo=ctes.TRA_CODIGO_ASIENTO_CONTABLE,
                                             alm_codigo=0, sec_codigo=0, tdv_codigo=0)
        formdet = self.get_form_detalle_asiento()
        persondao = TPersonaDao(self.dbsession)
        formref = persondao.getform()

        # Por defecto se lo pone en consumidor final
        formref['per_id'] = -1

        return {
            'formasiento': formasiento,
            'formref': formref,
            'formdet': formdet
        }

    def get_form_libromayor(self):

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

    def listar_asientos(self):
        sql = """
        select a.trn_codigo, a.dia_codigo, a.trn_fecreg, extract(day from a.trn_fecreg) ||'-'|| m.mes_corto as fecdesc,  a.trn_compro::int, a.trn_fecha, a.trn_valido, a.trn_docpen,
               a.per_codigo, a.us_id, a.trn_observ,
               b.dt_debito, b.dt_codigo, b.cta_codigo, c.ic_code, c.ic_nombre, b.dt_valor
               from tasiento a
                join tasidetalle b on b.trn_codigo = a.trn_codigo
                join titemconfig c on b.cta_codigo = c.ic_id
                join public.tmes m on  m.mes_id =  extract(month from a.trn_fecreg)
        where tra_codigo = {0} and trn_valido = 0 order by a.trn_fecreg desc, a.trn_compro::int desc, b.dt_debito desc, b.dt_codigo
        """.format(ctes.TRA_CODIGO_ASIENTO_CONTABLE)
        tupla_desc = (
            'trn_codigo', 'dia_codigo', 'trn_fecreg', 'fecdesc', 'trn_compro', 'trn_fecha', 'trn_valido', 'trn_docpen',
            'per_codigo', 'us_id', 'trn_observ', 'dt_debito',
            'dt_codigo', 'cta_codigo', 'ic_code', 'ic_nombre', 'dt_valor')
        items = self.all(sql, tupla_desc)
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
            if trn_codigo != lasttrncod:
                cab = True
                if lasttrncod != 0:
                    resultlist.append({
                        'trn_codigo': asiprevius['trn_codigo'],
                        'dt_codigo': '',
                        'cta_codigo': '',
                        'ic_code': '',
                        'trn_fecreg': '',
                        'ic_nombre': asiprevius['trn_observ'],
                        'dt_debito': 0,
                        'debe': '',
                        'haber': '',
                        'tr': 2
                    })
                lasttrncod = trn_codigo
                asiprevius = item
            if cab:
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'dt_codigo': '',
                    'cta_codigo': '',
                    'ic_code': '',
                    'trn_fecreg': item['fecdesc'],
                    'ic_nombre': '--------------------- {0} ---------------------'.format(
                        item['trn_compro']),
                    'dt_debito': 0,
                    'debe': '',
                    'haber': '',
                    'tr': 0
                })
            if item['dt_debito'] == 1:
                totales['debe'] += item['dt_valor']
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'dt_codigo': item['dt_codigo'],
                    'cta_codigo': item['cta_codigo'],
                    'ic_code': item['ic_code'],
                    'trn_fecreg': '',
                    'ic_nombre': item['ic_nombre'],
                    'dt_debito': item['dt_debito'],
                    'debe': item['dt_valor'],
                    'haber': '',
                    'tr': 1
                })
            elif item['dt_debito'] == -1:
                totales['haber'] += item['dt_valor']
                resultlist.append({
                    'trn_codigo': item['trn_codigo'],
                    'dt_codigo': item['dt_codigo'],
                    'cta_codigo': item['cta_codigo'],
                    'ic_code': item['ic_code'],
                    'trn_fecreg': '',
                    'ic_nombre': item['ic_nombre'],
                    'dt_debito': item['dt_debito'],
                    'debe': '',
                    'haber': item['dt_valor'],
                    'tr': 1
                })

            if item == items[len(items) - 1]:
                resultlist.append({
                    'trn_codigo': asiprevius['trn_codigo'],
                    'dt_codigo': '',
                    'cta_codigo': '',
                    'ic_code': '',
                    'trn_fecreg': '',
                    'ic_nombre': asiprevius['trn_observ'],
                    'dt_debito': 0,
                    'debe': '',
                    'haber': '',
                    'tr': 2
                })

        totales = {
            'debe': numeros.roundm2(totales['debe']),
            'haber': numeros.roundm2(totales['haber'])
        }

        return resultlist, totales

    def get_form_cabecera(self, tra_codigo, alm_codigo, sec_codigo, tdv_codigo):
        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
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
            'impuestos': impuestos
        }

        return form_asiento

    def listar_grid_ventas(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='ventas')
        return data

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

    def buid_rep_conta(self, desde, hasta, wherecodparents, isestadores=False):

        sqlbalgen = """
        select ic_id, ic_code, ic_nombre, ic_padre, ic_haschild, 0.0 as total from titemconfig
        where tipic_id = 3 and ic_estado = 1 and ({0})
        order by ic_code asc
        """.format(wherecodparents)

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
        """.format(ctes.TRA_CODIGO_ASIENTO_CONTABLE,
                   fechas.format_cadena_db(desde),
                   fechas.format_cadena_db(hasta))

        tupla_desc = ('cta_codigo', 'total')
        result = self.all(sql, tupla_desc)
        for item in result:
            if item['cta_codigo'] in planctasdict:
                planctasdict[item['cta_codigo']]['total'] = item['total']

        itemconfigdao = TItemConfigDao(self.dbsession)
        if isestadores:
            treebg = itemconfigdao.build_tree_estado_resultados()
        else:
            treebg = itemconfigdao.build_tree_balance_general()

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
            resultestres, parentestres, auxparentestres, auxrestree = self.buid_rep_conta(desde, hasta,
                                                                                          wherecodparents="ic_code like '4%' or ic_code like '5%'",
                                                                                          isestadores=True)
        return resultlist, parentsdict, parentestres, restulttree

    def get_datos_asientocontable(self, trn_codigo):
        formasiento = self.get_cabecera_asiento(trn_codigo=trn_codigo)
        formasiento['secuencia'] = int(formasiento['trn_compro'][6:])
        formasiento['tps_codigo'] = 0

        sqldet = """
        select det.dt_codigo, det.cta_codigo, det.dt_cant, det.dt_debito, det.dt_tipoitem, det.dt_valor,
               det.dt_valor as dt_valor_in, ic.ic_clasecc, ic.ic_code, ic.ic_nombre, det.per_codigo, det.pry_codigo,
               det.dt_codsec
            from tasidetalle det
            join titemconfig ic on det.cta_codigo = ic.ic_id
            where det.trn_codigo = {0} order by det.dt_codigo        
        """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'cta_codigo', 'dt_cant', 'dt_debito', 'dt_tipoitem', 'dt_valor',
                      'dt_valor_in', 'ic_clasecc', 'ic_code', 'ic_nombre', 'per_codigo', 'pry_codigo', 'dt_codsec')

        detalles = self.all(sqldet, tupla_desc)

        return {
            'cabecera': formasiento,
            'detalles': detalles
        }

    def get_form_detalle_asiento(self):
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

    def get_form_detalle(self):
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
            'dt_codsec': 1,
            'dai_imp0': None,
            'dai_impg': None,
            'dai_ise': None,
            'dai_ice': None,
            'icdp_grabaiva': False,
            'subtotal': 0.0,
            'ivaval': 0.0,
            'total': 0.0
        }

        return form

    def existe_doc_valido(self, trn_compro, tra_codigo):
        sql = """
        select count(*) as cuenta from tasiento where trn_compro = '{0}' and tra_codigo = {1} 
        and trn_docpen = 'F' and trn_valido = 0
        """.format(cadenas.strip(trn_compro), tra_codigo)
        return self.first_col(sql, 'cuenta') > 0

    def get_pagos(self, trn_codigo):
        sql = """
        select a.dt_codigo, a.cta_codigo, ic.ic_nombre, ic.ic_clasecc, a.dt_valor from tasidetalle a
            join titemconfig ic on ic.ic_id = cta_codigo
            where a.dt_tipoitem = 2
            and a.trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('dt_codigo', 'cta_codigo', 'ic_nombre', 'ic_clasecc', 'dt_valor')
        return self.all(sql, tupla_desc)

    def listar_documentos(self, per_codigo, tra_codigo, find_pagos=False):
        """
        Listar facturas validas de un referente especificaco
        :param per_codigo:
        :return: [trn_codigo, trn_fecreg, trn_fecha, trn_compro, trn_observ, pagos:{'dt_codigo', 'cta_codigo', 'ic_nombre', 'ic_clasecc', 'dt_valor'}]
        """
        sql = """
        select trn_codigo, trn_fecreg, trn_fecha, trn_compro, trn_observ from tasiento where per_codigo = {0}
        and tra_codigo = {1} and trn_valido = 0 and trn_docpen = 'F' order by trn_fecha desc 
        """.format(per_codigo, tra_codigo)
        tupla_desc = ('trn_codigo', 'trn_fecreg', 'trn_fecha', 'trn_compro', 'trn_observ')

        facturas = self.all(sql, tupla_desc)
        if find_pagos:
            for factura in facturas:
                factura['pagos'] = self.get_pagos(trn_codigo=factura['trn_codigo'])

        return facturas

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
        trn_fecha,
        trn_valido,
        trn_docpen,
        trn_pagpen,
        sec_codigo,
        a.per_codigo,
        tra_codigo,
        us_id,
        trn_observ,
        tdv_codigo,
        fol_codigo,
        trn_tipcom,
        trn_suscom,
        per_codres,
        trn_impref,
        coalesce(per.per_nombres,'')||' '||coalesce(per.per_apellidos,'') as referente,
        per.per_ciruc,
        per.per_telf,
        per.per_direccion
         from tasiento a join tpersona per on a.per_codigo = per.per_id  where trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('trn_codigo',
                      'dia_codigo',
                      'trn_fecreg',
                      'trn_compro',
                      'trn_fecha',
                      'trn_valido',
                      'trn_docpen',
                      'trn_pagpen',
                      'sec_codigo',
                      'per_codigo',
                      'tra_codigo',
                      'us_id',
                      'trn_observ',
                      'tdv_codigo',
                      'fol_codigo',
                      'trn_tipcom',
                      'trn_suscom',
                      'per_codres',
                      'trn_impref',
                      'referente',
                      'per_ciruc',
                      'per_telf',
                      'per_direccion')

        tasiento = self.first(sql, tupla_desc)
        return tasiento

    def get_documento(self, trn_codigo):
        tasiento = self.get_cabecera_asiento(trn_codigo=trn_codigo)
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
            if pago['ic_clasecc'] == 'C':
                pagosobj['credito'] = numeros.roundm2(pago['dt_valor'])
            else:
                pagosobj['efectivo'] = numeros.roundm2(pago['dt_valor'])

        pagosobj['total'] = numeros.roundm2(totalpagos)

        return {
            'tasiento': tasiento,
            'detalles': detalles,
            'pagos': pagos,
            'pagosobj': pagosobj,
            'impuestos': impuestos,
            'totales': totales
        }

    def calcular_totales(self, detalles):
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
            det['icdp_grabaiva'] = 'N'
            ivaval = 0.0
            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                det['icdp_grabaiva'] = 'S'
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

    def get_form_pago(self):
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
        tasiento.trn_valido = 1
        self.dbsession.add(tasiento)

        tasientoaud = TAsientoAud()
        tasientoaud.trn_codigo = trn_codigo
        tasientoaud.aud_accion = ctes.AUD_ASIENTO_ANULAR
        tasientoaud.aud_obs = obs
        tasientoaud.aud_user = useredita
        self.dbsession.add(tasientoaud)

        new_trn_codigo = self.crear_asiento(formcab=formcab, formref=formref, usercrea=useredita, detalles=detalles)

        return new_trn_codigo

    def crear_asiento(self, formcab, formref, usercrea, detalles):
        secuencia = formcab['secuencia']
        trn_compro = "{0}{1}".format(formcab['estabptoemi'], str(secuencia).zfill(ctes.LEN_DOC_SECUENCIA))

        # Verificar que el comprobante no este siendo utilizado
        tra_codigo = formcab['tra_codigo']
        if formcab['trn_docpen'] == 'F':
            if self.existe_doc_valido(trn_compro, tra_codigo=tra_codigo):
                raise ErrorValidacionExc('Ya existe un comprobante registrado con el número: {0}'.format(trn_compro))

        trn_compro = trn_compro
        trn_fecha = datetime.now()
        trn_valido = 0
        trn_docpen = formcab['trn_docpen']
        trn_pagpen = formcab['trn_pagpen']
        sec_codigo = formcab['sec_codigo']
        us_id = usercrea
        trn_observ = formcab['trn_observ']
        tdv_codigo = formcab['tdv_codigo']
        fol_codigo = int(formcab['fol_codigo'])
        trn_tipcom = formcab['trn_tipcom']
        trn_suscom = formcab['trn_suscom']
        per_codres = None

        persodao = TPersonaDao(self.dbsession)

        per_codigo = int(formref['per_id'])
        if per_codigo == 0:
            per_codigo = persodao.crear(form=formref)
        elif per_codigo > 0:
            per_codigo = persodao.actualizar(form=formref)

        tasiento = TAsiento()
        tasiento.dia_codigo = formcab['dia_codigo']
        tasiento.trn_fecreg = fechas.parse_cadena(formcab['trn_fecreg'])
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = trn_fecha
        tasiento.trn_valido = trn_valido
        tasiento.trn_docpen = trn_docpen
        tasiento.trn_pagpen = trn_pagpen
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = per_codigo
        tasiento.tra_codigo = tra_codigo
        tasiento.us_id = us_id
        tasiento.trn_observ = trn_observ
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = fol_codigo
        tasiento.trn_tipcom = trn_tipcom
        tasiento.trn_suscom = trn_suscom
        tasiento.per_codres = per_codres
        tasiento.trn_impref = 0

        tps_codigo = formcab['tps_codigo']
        if tps_codigo is not None and tps_codigo > 0:
            transaccpdv_dao = TTransaccPdvDao(self.dbsession)
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        trn_codigo = tasiento.trn_codigo

        # Verificar la suma del debe con el haber
        sumadebe = 0.0
        sumahaber = 0.0
        for det in detalles:
            if det['dt_debito'] == 1:
                sumadebe += float(det['dt_valor'])
            else:
                sumahaber += float(det['dt_valor'])

        sumadeberound = numeros.roundm2(sumadebe)
        sumahaberound = numeros.roundm2(sumahaber)
        if sumadeberound != sumahaberound:
            raise ErrorValidacionExc(
                'La suma del debe ({0}) y del haber({1}) no coinciden, favor verificar'.format(sumadeberound,
                                                                                               sumahaberound))
        for detalle in detalles:
            detasiento = TAsidetalle()
            if float(detalle['dt_valor']) > 0.0:
                detasiento.trn_codigo = trn_codigo
                detasiento.per_codigo = per_codigo
                detasiento.cta_codigo = detalle['cta_codigo']
                detasiento.art_codigo = 0
                detasiento.dt_debito = detalle['dt_debito']
                detasiento.dt_valor = numeros.roundm2(float(detalle['dt_valor']))
                detasiento.dt_tipoitem = ctes.DT_TIPO_ITEM_DETASIENTO
                detasiento.dt_codsec = detalle['dt_codsec']
                self.dbsession.add(detasiento)

        return trn_codigo

    def crear_asiento_cxcp(self, formcab, per_codigo, user_crea, detalles):
        len_compro = ctes.LEN_DOC_SECUENCIA
        secuencia = formcab['secuencia']
        trn_compro = "{0}{1}".format(formcab['estabptoemi'], str(secuencia).zfill(len_compro))

        # Verificar que el comprobante no este siendo utilizado
        tra_codigo = formcab['tra_codigo']
        if formcab['trn_docpen'] == 'F':
            if self.existe_doc_valido(trn_compro, tra_codigo=tra_codigo):
                raise ErrorValidacionExc('Ya existe un comprobante registrado con el número: {0}'.format(trn_compro))

        trn_compro = trn_compro
        trn_fecha = datetime.now()
        trn_valido = 0
        trn_docpen = formcab['trn_docpen']
        trn_pagpen = formcab['trn_pagpen']
        sec_codigo = formcab['sec_codigo']
        us_id = user_crea
        trn_observ = formcab['trn_observ']
        tdv_codigo = formcab['tdv_codigo']
        fol_codigo = int(formcab['fol_codigo'])
        trn_tipcom = formcab['trn_tipcom']
        trn_suscom = formcab['trn_suscom']
        per_codres = None

        tasiento = TAsiento()
        tasiento.dia_codigo = formcab['dia_codigo']
        tasiento.trn_fecreg = fechas.parse_cadena(formcab['trn_fecreg'])
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = trn_fecha
        tasiento.trn_valido = trn_valido
        tasiento.trn_docpen = trn_docpen
        tasiento.trn_pagpen = trn_pagpen
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = per_codigo
        tasiento.tra_codigo = tra_codigo
        tasiento.us_id = us_id
        tasiento.trn_observ = trn_observ
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = fol_codigo
        tasiento.trn_tipcom = trn_tipcom
        tasiento.trn_suscom = trn_suscom
        tasiento.per_codres = per_codres
        tasiento.trn_impref = 0

        tps_codigo = formcab['tps_codigo']
        if tps_codigo is not None:
            transaccpdv_dao = TTransaccPdvDao(self.dbsession)
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        trn_codigo = tasiento.trn_codigo

        creditodao = TAsicreditoDao(self.dbsession)
        for detalle in detalles:
            detasiento = TAsidetalle()
            if float(detalle['dt_valor']) > 0.0:
                detasiento.trn_codigo = trn_codigo
                detasiento.per_codigo = per_codigo
                detasiento.cta_codigo = detalle['cta_codigo']
                detasiento.art_codigo = 0
                detasiento.dt_debito = detalle['dt_debito']
                detasiento.dt_valor = numeros.roundm2(float(detalle['dt_valor']))
                detasiento.dt_tipoitem = ctes.DT_TIPO_ITEM_DETASIENTO
                detasiento.dt_codsec = detalle['dt_codsec']

                ic_clasecc = detalle['ic_clasecc']

                self.dbsession.add(detasiento)
                self.dbsession.flush()
                dt_codigo = detasiento.dt_codigo
                if ic_clasecc == 'C':
                    tra_codigo_int = int(tra_codigo)
                    if (tra_codigo_int == ctes.TRA_CODIGO_ABONO_COMPRA) or (
                            tra_codigo_int == ctes.TRA_CODIGO_ABONO_VENTA):
                        # Se debe registrar abono
                        abonodao = TAsiAbonoDao(self.dbsession)
                        abonodao.crear(dt_codigo, detalle['dt_codcred'], detasiento.dt_valor)
                    else:
                        tra_codigo_cred = ctes.TRA_CODIGO_CREDITO_VENTA
                        if int(tra_codigo) == ctes.TRA_CODIGO_FACTURA_COMPRA:
                            tra_codigo_cred = ctes.TRA_CODIGO_CREDITO_COMPRA

                        formcre = {
                            'dt_codigo': dt_codigo,
                            'cre_fecini': formcab['trn_fecreg'],
                            'cre_fecven': None,
                            'cre_intere': 0.0,
                            'cre_intmor': 0.0,
                            'cre_codban': None,
                            'cre_saldopen': detasiento.dt_valor
                        }
                        creditodao.crear(form=formcre, tra_codigo_cred=tra_codigo_cred)

        return trn_codigo

    def aux_cambia_estado(self, trn_codigo, user_do, obs, new_state):
        tasiento = self.find_entity_byid(trn_codigo=trn_codigo)
        if tasiento is not None:
            if tasiento.trn_valido != new_state:
                tasiento.trn_valido = new_state
                self.dbsession.add(tasiento)
                # TODO: Agregar informacion de auditoria en tabla tasientoaud (usuario, motivo)

    def anular(self, trn_codigo, user_anula, obs_anula):
        self.aux_cambia_estado(trn_codigo, user_do=user_anula, obs=obs_anula, new_state=1)

    def marcar_errado(self, trn_codigo, user_do):
        self.aux_cambia_estado(trn_codigo, user_do=user_do, obs='', new_state=2)

    def duplicar_comprobante(self, trn_codigo, user_crea, tra_codigo):
        tasiento = self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()
        if tasiento is not None:
            detalles = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=ctes.DT_TIPO_ITEM_DETALLE)

            for detalle in detalles:
                for key in detalle.keys():
                    if not cadenas.es_nonulo_novacio(detalle[key]):
                        detalle[key] = None

            # impuestos = self.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=ctes.DT_TIPO_ITEM_IMPUESTO)
            pagos = self.get_detalles_doc(trn_codigo=trn_codigo, joinarts=False, dt_tipoitem=ctes.DT_TIPO_ITEM_PAGO)

            totales = self.calcular_totales(detalles)

            ttpdvdao = TtpdvDao(self.dbsession)
            alm_codigo = ttpdvdao.get_alm_codigo_from_tdv_codigo(tasiento.tdv_codigo)
            formcab = self.get_form_cabecera(tra_codigo=tra_codigo, alm_codigo=alm_codigo,
                                             sec_codigo=tasiento.sec_codigo, tdv_codigo=tasiento.tdv_codigo)
            formcab['trn_docpen'] = 'F'
            formcab['tra_codigo'] = tra_codigo

            formpersona = {'per_id': tasiento.per_codigo}
            return self.crear(form=formcab, form_persona=formpersona, user_crea=user_crea, detalles=detalles,
                              pagos=pagos, totales=totales)

    def crear(self, form, form_persona, user_crea, detalles, pagos, totales, creaupdpac=True):
        dia_codigo = form['dia_codigo']
        trn_fecreg = fechas.parse_cadena(form['trn_fecreg'])
        len_compro = ctes.LEN_DOC_SECUENCIA
        secuencia = form['secuencia']
        trn_compro = "{0}{1}".format(form['estabptoemi'], str(secuencia).zfill(len_compro))

        # Verificar que el comprobante no este siendo utilizado
        tra_codigo = form['tra_codigo']
        if form['trn_docpen'] == 'F':
            if self.existe_doc_valido(trn_compro, tra_codigo=tra_codigo):
                raise ErrorValidacionExc('Ya existe un comprobante registrado con el número: {0}'.format(trn_compro))

        trn_compro = trn_compro
        trn_fecha = datetime.now()
        trn_valido = 0
        trn_docpen = form['trn_docpen']
        trn_pagpen = form['trn_pagpen']
        sec_codigo = form['sec_codigo']
        us_id = user_crea
        trn_observ = form['trn_observ']
        tdv_codigo = form['tdv_codigo']
        fol_codigo = int(form['fol_codigo'])
        trn_tipcom = form['trn_tipcom']
        trn_suscom = form['trn_suscom']
        per_codres = None

        personadao = TPersonaDao(self.dbsession)
        ttransaccimpdao = TTransaccImpDao(self.dbsession)

        configtransaccimp = ttransaccimpdao.get_config(tra_codigo=tra_codigo)
        impuestos = []
        if configtransaccimp is not None and totales is not None:
            ivaval = totales['iva']
            if ivaval is not None and ivaval > 0:
                impuestos.append({
                    'cta_codigo': configtransaccimp['tra_impg'],
                    'dt_debito': configtransaccimp['tra_signo'],
                    'dt_valor': ivaval
                })

        per_codigo = int(form_persona['per_id'])
        if creaupdpac and per_codigo >= 0:
            if per_codigo is not None and per_codigo > 0:
                personadao.actualizar(per_id=per_codigo, form=form_persona)
            else:
                persona = personadao.buscar_porciruc(per_ciruc=form_persona['per_ciruc'])
                if persona is not None:
                    per_codigo = persona[0]['per_id']
                    personadao.actualizar(per_id=per_codigo, form=form_persona)
                else:
                    per_codigo = personadao.crear(form=form_persona)

        tasiento = TAsiento()
        tasiento.dia_codigo = dia_codigo
        tasiento.trn_fecreg = trn_fecreg
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = trn_fecha
        tasiento.trn_valido = trn_valido
        tasiento.trn_docpen = trn_docpen
        tasiento.trn_pagpen = trn_pagpen
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = per_codigo
        tasiento.tra_codigo = tra_codigo
        tasiento.us_id = us_id
        tasiento.trn_observ = trn_observ
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = fol_codigo
        tasiento.trn_tipcom = trn_tipcom
        tasiento.trn_suscom = trn_suscom
        tasiento.per_codres = per_codres
        tasiento.trn_impref = form['trn_impref']

        tps_codigo = form['tps_codigo']
        if tps_codigo is not None:
            transaccpdv_dao = TTransaccPdvDao(self.dbsession)
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        trn_codigo = tasiento.trn_codigo

        for detalle in detalles:
            tasidetalle = TAsidetalle()

            per_cod_det = int(detalle['per_codigo'])
            if per_cod_det == 0:
                per_cod_det = per_codigo

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
            tasidetimp.dai_imp0 = detalle['dai_imp0']
            tasidetimp.dai_impg = detalle['dai_impg']
            tasidetimp.dai_ise = detalle['dai_ise']
            tasidetimp.dai_ice = detalle['dai_ice']

            self.dbsession.add(tasidetimp)

        for impuesto in impuestos:
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

        sumapagos = 0.0
        for pago in pagos:
            detpago = TAsidetalle()
            if float(pago['dt_valor']) > 0.0:
                detpago.trn_codigo = trn_codigo
                detpago.per_codigo = per_codigo
                detpago.cta_codigo = pago['cta_codigo']
                detpago.art_codigo = 0
                detpago.dt_debito = pago['dt_debito']
                detpago.dt_valor = float(pago['dt_valor'])
                detpago.dt_tipoitem = ctes.DT_TIPO_ITEM_PAGO
                detpago.dt_codsec = pago['dt_codsec']
                sumapagos += detpago.dt_valor

                ic_clasecc = pago['ic_clasecc']

                self.dbsession.add(detpago)
                self.dbsession.flush()
                dt_codigo = detpago.dt_codigo
                if ic_clasecc == 'C' and float(pago['dt_valor']) > 0.0:
                    creditodao = TAsicreditoDao(self.dbsession)
                    tra_codigo_cred = ctes.TRA_CODIGO_CREDITO_VENTA
                    if int(tra_codigo) == ctes.TRA_CODIGO_FACTURA_COMPRA:
                        tra_codigo_cred = ctes.TRA_CODIGO_CREDITO_COMPRA

                    formcre = {
                        'dt_codigo': dt_codigo,
                        'cre_fecini': form['trn_fecreg'],
                        'cre_fecven': None,
                        'cre_intere': 0.0,
                        'cre_intmor': 0.0,
                        'cre_codban': None,
                        'cre_saldopen': detpago.dt_valor
                    }
                    creditodao.crear(form=formcre, tra_codigo_cred=tra_codigo_cred)

        totalform = numeros.roundm(float(totales['total']), 2)
        totalsuma = numeros.roundm(sumapagos, 2)

        if totalform != totalsuma:
            raise ErrorValidacionExc(
                'El total de la factura ({0}) no coincide con la suma de los pagos ({1})'.format(totalform, totalsuma))

        return trn_codigo
