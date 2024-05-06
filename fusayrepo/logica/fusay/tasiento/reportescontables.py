# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tperiodocontable.tperiodo_dao import TPeriodoContableDao
from fusayrepo.utils import numeros, fechas, ctes
from fusayrepo.utils.numeros import roundm2

log = logging.getLogger(__name__)


class ReportesContablesDao(BaseDao):

    def aux_totalizar_nodo(self, nodo, planctasdict):
        totalnodo = 0.0
        if 'children' in nodo and len(nodo['children']) > 0:
            for hijonodo in nodo['children']:
                totalnodo += self.aux_totalizar_nodo(hijonodo, planctasdict)
            nodo['total'] = abs(numeros.roundm2(totalnodo))
        else:
            itemdb = nodo['dbdata']
            item_codcta = itemdb['ic_id']
            if item_codcta in planctasdict:
                nodo['total'] = abs(numeros.roundm2(planctasdict[item_codcta]['total']))

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

    def add_total_to_list(self, the_tree, the_list):
        ctas_dict = {}
        for item in the_tree:
            ctas_dict[item['dbdata']['ic_id']] = item['total']

        for item in the_list:
            if item['ic_id'] in ctas_dict:
                item['total'] = ctas_dict[item['ic_id']]

    def aux_build_tree_from_list(self, the_list, the_tree):
        planctasdict = {item['ic_id']: item for item in the_list}
        """
        for item in the_list:
            planctasdict[item['ic_id']] = item
        """

        for item in the_tree:
            item['total'] = roundm2(abs(self.aux_totalizar_nodo(item, planctasdict)))

        return the_tree

    def get_total_grupos_dict(self, desde, hasta, sec_id):
        sql = """
        with data as (
            select mcd.cta_id, round(mcd.mcd_saldo,2) as total 
                from tsum_ctas_diario mcd
                where date(mcd_dia) = '{hasta}' order by mcd.cta_id
        )

        select SUBSTRING(ic_code,1,1) grupo, sum(coalesce(data.total,0.0)) as total 
                from titemconfig ic
                join titemconfig_sec ics on ics.ic_id = ic.ic_id 
                left join data on ic.ic_id = data.cta_id
                where ic.tipic_id = 3 and ic.ic_estado = 1 and ics.sec_id = {sec_id} and 
                (ic_code like '1%' or ic_code like '2%' or ic_code like '3%' or ic_code like '4%' or ic_code like '5%')
                group by SUBSTRING(ic_code,1,1) order by 1 asc
        """.format(desde=desde, hasta=hasta, sec_id=sec_id)

        tupla_desc = ('grupo', 'total')
        totales = self.all(sql, tupla_desc)
        result_dict = {}
        for item in totales:
            result_dict[int(item['grupo'])] = roundm2(item['total'])

        for i in range(5):
            if i + 1 not in result_dict:
                result_dict[i + 1] = 0.0

        return result_dict

    def build_balance_gen_mayorizado(self, desde, hasta, sec_id, chk_per=True):
        periododao = TPeriodoContableDao(self.dbsession)
        periodo_contable = periododao.get_datos_periodo_contable()
        if periodo_contable is None and chk_per:
            raise ErrorValidacionExc('No existe un periodo contable activo registrado, favor verificar')

        # pc_desde = periodo_contable['pc_desde']

        total_grupos_dict = self.get_total_grupos_dict(desde=fechas.format_cadena_db(desde),
                                                       hasta=fechas.format_cadena_db(hasta),
                                                       sec_id=sec_id)
        resultado_ejercicio = numeros.roundm2(abs(total_grupos_dict[5]) - abs(total_grupos_dict[4]))
        total_grupos_dict[3] += (resultado_ejercicio * -1)

        paramsdao = TParamsDao(self.dbsession)
        cta_contab_result = paramsdao.get_param_value('cta_contab_resultado')

        sql_union_cta_result = ""
        if cta_contab_result is not None:
            sql_union_cta_result = """
            union all select ic.ic_id, {0} total from titemconfig ic where
            ic.ic_code = '{1}'
            """.format(resultado_ejercicio * -1, cta_contab_result)

        sql = """
            with data as (
                select mcd.cta_id, round(mcd.mcd_saldo,2) as total 
                    from tsum_ctas_diario mcd
                    where date(mcd_dia) = '{hasta}'                     
                {sql_cta_result}
            )            
            select ic.ic_id, ic_code, ic_nombre, ic_code||' '||ic_nombre as codenombre, ic_padre, ic_haschild, 
                    coalesce(data.total,0.0) as total 
                    from titemconfig ic
                    join titemconfig_sec ics on ics.ic_id = ic.ic_id 
                    left join data on ic.ic_id = data.cta_id
                    where ic.tipic_id = 3 and ic.ic_estado = 1 and ics.sec_id = {sec_id} and 
                    (ic_code like '1%' or ic_code like '2%' or ic_code like '3%')
                    order by ic_code asc  
        """.format(sql_cta_result=sql_union_cta_result,
                   desde=fechas.format_cadena_db(desde),
                   hasta=fechas.format_cadena_db(hasta),
                   sec_id=sec_id)
        tupla_desc = ('ic_id', 'ic_code', 'ic_nombre', 'codenombre', 'ic_padre', 'ic_haschild', 'total')

        result = self.all(sql, tupla_desc)

        itemconfigdao = TItemConfigDao(self.dbsession)
        treebg = self.aux_build_tree_from_list(the_list=result,
                                               the_tree=itemconfigdao.build_tree_balance_general(sec_id=sec_id))

        return {
            'balance_list': result,
            'balance_tree': treebg,
            'total_grupos': total_grupos_dict,
            'resultado_ejercicio': resultado_ejercicio,
            'cta_contab_result':cta_contab_result
        }

    def get_resultado_ejercicio_mayorizado(self, desde, hasta, sec_id):
        periododao = TPeriodoContableDao(self.dbsession)
        periodo_contable = periododao.get_datos_periodo_contable()
        if periodo_contable is None:
            raise ErrorValidacionExc('No existe un periodo contable activo registrado, favor verificar')

        #pc_desde = periodo_contable['pc_desde']
        sql = """
                    with data as (
                        select mcd.cta_id, round(mcd.mcd_saldo,2) as total 
                            from tsum_ctas_diario mcd
                            where date(mcd_dia) = '{hasta}' order by mcd.cta_id
                    )            
                    select ic.ic_id, ic_code, ic_nombre, ic_padre, ic_haschild, coalesce(data.total,0.0) as total 
                            from titemconfig ic
                            join titemconfig_sec ics on ics.ic_id = ic.ic_id 
                            left join data on ic.ic_id = data.cta_id
                            where ic.tipic_id = 3 and ic.ic_estado = 1 and ics.sec_id = {sec_id} and 
                            (ic_code like '4%' or ic_code like '5%')
                            order by ic_code asc  
                """.format(desde=fechas.format_cadena_db(desde),
                           hasta=fechas.format_cadena_db(hasta),
                           sec_id=sec_id)
        tupla_desc = ('ic_id', 'ic_code', 'ic_nombre', 'ic_padre', 'ic_haschild', 'total')

        result = self.all(sql, tupla_desc)

        itemconfigdao = TItemConfigDao(self.dbsession)
        treebg = self.aux_build_tree_from_list(the_list=result,
                                               the_tree=itemconfigdao.build_tree_estado_resultados(sec_id=sec_id))

        total_grupos_dict = self.get_total_grupos_dict(desde=fechas.format_cadena_db(desde),
                                                       hasta=fechas.format_cadena_db(hasta),
                                                       sec_id=sec_id)

        return {
            'reporte_list': result,
            'reporte_tree': treebg,
            'total_grupos': total_grupos_dict
        }

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

        tparamsdao = TParamsDao(self.dbsession)
        fecha_ini_contab = tparamsdao.get_param_value('fecha_ini_contab', sec_id=sec_id)
        sqlfechainicontab = ''
        if fecha_ini_contab is not None and len(fecha_ini_contab) > 0:
            sqlfechainicontab = " and date(t.trn_fecha)>='{0}' ".format(fechas.format_cadena_db(fecha_ini_contab))

        sql = """
        select det.cta_codigo, round(sum(det.dt_debito*det.dt_valor),2) as total 
        from tasidetalle det
        join tasiento t on det.trn_codigo = t.trn_codigo and t.tra_codigo = ANY (ARRAY [1, 2, 7, 8, 9]) and t.trn_valido = 0 and t.trn_docpen = 'F' 
        join titemconfig ic on det.cta_codigo = ic.ic_id
        where t.trn_fecreg between '{0}' and '{1}' {2}
        group by det.cta_codigo order by det.cta_codigo
        """.format(fechas.format_cadena_db(desde),
                   fechas.format_cadena_db(hasta),
                   sqlfechainicontab)

        if not isestadores:
            sql = """
                   select det.cta_codigo, round(sum(det.dt_debito*det.dt_valor),2) as total 
                   from tasidetalle det
                   join tasiento t on det.trn_codigo = t.trn_codigo and t.tra_codigo = {0} and t.trn_valido = 0 
                   join titemconfig ic on det.cta_codigo = ic.ic_id
                   where t.trn_fecreg between '{1}' and '{2}' {3}
                   group by det.cta_codigo order by det.cta_codigo
                   """.format(ctes.TRA_COD_ASI_CONTABLE,
                              fechas.format_cadena_db(desde),
                              fechas.format_cadena_db(hasta), sqlfechainicontab)

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
