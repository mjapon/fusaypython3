# coding: utf-8
"""
Fecha de creacion 5/23/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tconsultamedica.tconsultamedica_model import TConsultaMedicaValores, TConsultaMedica
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.utils import fechas, cadenas, ctes

log = logging.getLogger(__name__)


class TConsultaMedicaDao(BaseDao):

    def get_form(self):
        form_antecedentes = self.get_form_valores(1)
        form_revxsistemas = self.get_form_valores(2)
        form_examsfisicos = self.get_form_valores(3)
        form_paciente = {
            'per_id': 0,
            'per_ciruc': '',
            'per_nombres': '',
            'per_apellidos': '',
            'per_direccion': '',
            'per_telf': '',
            'per_movil': '',
            'per_email': '',
            'per_fecreg': '',
            'per_tipo': 1,
            'per_lugnac': None,
            'per_nota': '',
            'per_fechanac': '',
            'per_genero': None,
            'per_estadocivil': 1,
            'per_lugresidencia': None,
            'per_ocupacion': None,
            'per_edad': {'years': 0, 'months': 0, 'days': 0}
        }

        form_datosconsulta = {
            'cosm_id': 0,
            'pac_id': 0,
            'med_id': 0,
            'cosm_fechacita': fechas.get_str_fecha_actual(),
            'cosm_fechacrea': '',
            'cosm_motivo': '',
            'cosm_enfermactual': '',
            'cosm_hallazgoexamfis': '',
            'cosm_exmscompl': '',
            'cosm_tratamiento': '',
            'cosm_receta': '',
            'cosm_indicsreceta': '',
            'cosm_recomendaciones': '',
            'user_crea': '',
            'cosm_diagnostico': None,
            'cosm_diagnosticoal': '',
            'cosm_fechaproxcita': '',
            'cosm_tipo': 1,
            'cosm_odontograma': ''
        }

        return {
            'paciente': form_paciente,
            'datosconsulta': form_datosconsulta,
            'antecedentes': form_antecedentes,
            'examsfisicos': form_examsfisicos,
            'revxsistemas': form_revxsistemas
        }

    def get_form_odonto(self):
        form_antecedentes = self.get_form_valores(5)
        form_examsfisicos = self.get_form_valores(3)
        # form_examdiagnostico = self.get_form_valores(4)
        form_paciente = {
            'per_id': 0,
            'per_ciruc': '',
            'per_nombres': '',
            'per_apellidos': '',
            'per_direccion': '',
            'per_telf': '',
            'per_movil': '',
            'per_email': '',
            'per_fecreg': '',
            'per_tipo': 1,
            'per_lugnac': None,
            'per_nota': '',
            'per_fechanac': '',
            'per_genero': None,
            'per_estadocivil': 1,
            'per_lugresidencia': None,
            'per_ocupacion': None,
            'per_edad': {'years': 0, 'months': 0, 'days': 0}
        }

        form_datosconsulta = {
            'cosm_id': 0,
            'pac_id': 0,
            'med_id': 0,
            'cosm_fechacita': fechas.get_str_fecha_actual(),
            'cosm_fechacrea': '',
            'cosm_motivo': '',
            'cosm_enfermactual': '',
            'cosm_hallazgoexamfis': '',
            'cosm_exmscompl': '',
            'cosm_tratamiento': '',
            'cosm_receta': '',
            'cosm_indicsreceta': '',
            'cosm_recomendaciones': '',
            'user_crea': '',
            'cosm_diagnostico': None,
            'cosm_diagnosticoal': '',
            'cosm_fechaproxcita': '',
            'cosm_tipo': 2
        }

        return {
            'paciente': form_paciente,
            'datosconsulta': form_datosconsulta,
            'antecedentes': form_antecedentes,
            'examsfisicos': form_examsfisicos,
            'odontograma': {}
        }

    def get_antecedentes_personales(self, per_ciruc):

        ult_atencion_cod = self.get_ultima_atencion_paciente(per_ciruc)
        form_antecedentes = []
        if ult_atencion_cod is not None:
            form_antecedentes = self.get_valores_adc_citamedica(1, ult_atencion_cod)

        return form_antecedentes

    def get_historia_porpaciente(self, per_ciruc):
        """
        Buscar todas las veces que se ha registrado una atencion para el paciente especificado
        :param per_ciruc:
        :return: ['cosm_id', 'cosm_fechacrea', 'per_ciruc', 'paciente', 'cosm_motivo']
        """

        sql = u"""select historia.cosm_id, historia.cosm_fechacrea, paciente.per_ciruc, 
                paciente.per_nombres||' '||paciente.per_apellidos as paciente, historia.cosm_motivo,
                historia.cosm_fechaproxcita 
                from tconsultamedica historia
                join tpersona paciente on historia.pac_id = paciente.per_id and 
                paciente.per_ciruc = '{0}' where historia.cosm_estado = 1 order by historia.cosm_fechacrea desc """.format(
            per_ciruc)
        tupla_desc = ('cosm_id', 'cosm_fechacrea', 'per_ciruc', 'paciente', 'cosm_motivo', 'cosm_fechaproxcita')

        historias = self.all(sql, tupla_desc)
        historias_fecha = []

        for item in historias:
            fecha_str = fechas.get_fecha_letras_largo(
                fechas.parse_cadena(item['cosm_fechacrea'], formato=ctes.APP_FMT_FECHA_HORA))
            item['fecha_crea_largo'] = fecha_str
            historias_fecha.append(item)

        return historias_fecha

    def get_entity_byid(self, cosm_id):
        return self.dbsession.query(TConsultaMedica).filter(TConsultaMedica.cosm_id == cosm_id).first()

    def anular(self, cosm_id, form, useranula):
        tconsultamedica = self.get_entity_byid(cosm_id)
        if tconsultamedica is not None:
            if tconsultamedica.cosm_estado == 1:
                tconsultamedica.cosm_estado = 2
                tconsultamedica.cosm_obsanula = form['cosm_obsanula']
                tconsultamedica.cosm_useranula = useranula
                tconsultamedica.cosm_fechaanula = datetime.now()
            else:
                raise ErrorValidacionExc('Esta historia ya ha sido anulada')
        else:
            raise ErrorValidacionExc('No existe ningún registro de historia clínica con el código:{0}'.format(cosm_id))

    def listarproxcitasod_grid(self, tipofecha):
        tgrid_dao = TGridDao(self.dbsession)

        desde = ''
        hasta = ''
        hoy = datetime.now()
        fechasstr = ''
        if tipofecha == 1:  # hoy
            desde = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
            fechasstr = fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA)
        elif tipofecha == 2:  # mañana
            maniana = fechas.sumar_dias(hoy, 1)
            desde = fechas.get_str_fecha(maniana, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(maniana, ctes.APP_FMT_FECHA_DB)
            fechasstr = fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA)
        elif tipofecha == 3:  # Esta semana
            desde = fechas.get_str_fecha(hoy, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(fechas.get_lastday_of_week(), ctes.APP_FMT_FECHA_DB)
            fechasstr = '{0}  -  {1}'.format(fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA),
                                             fechas.format_cadena(hasta, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA))
        elif tipofecha == 4:  # Este mesa
            desde = fechas.get_str_fecha(hoy, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(fechas.get_lastday_of_month(), ctes.APP_FMT_FECHA_DB)
            fechasstr = '{0}  -  {1}'.format(fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA),
                                             fechas.format_cadena(hasta, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA))
        swhere = " "
        if len(desde) > 0:
            swhere = " and date(cita.ct_fecha) between '{desde}' and '{hasta}' ".format(
                desde=desde,
                hasta=hasta)

        data = tgrid_dao.run_grid(grid_nombre='proxcitasod', swhere=swhere)
        return data, fechasstr

    def listarproxcita_grid(self, tipofecha, tipocita):
        tgrid_dao = TGridDao(self.dbsession)

        desde = ''
        hasta = ''
        hoy = datetime.now()
        fechasstr = ''
        if tipofecha == 1:  # hoy
            desde = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
            fechasstr = fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA)
        elif tipofecha == 2:  # mañana
            maniana = fechas.sumar_dias(hoy, 1)
            desde = fechas.get_str_fecha(maniana, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(maniana, ctes.APP_FMT_FECHA_DB)
            fechasstr = fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA)
        elif tipofecha == 3:  # Esta semana
            desde = fechas.get_str_fecha(hoy, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(fechas.get_lastday_of_week(), ctes.APP_FMT_FECHA_DB)
            fechasstr = '{0}  -  {1}'.format(fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA),
                                             fechas.format_cadena(hasta, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA))
        elif tipofecha == 4:  # Este mesa
            desde = fechas.get_str_fecha(hoy, ctes.APP_FMT_FECHA_DB)
            hasta = fechas.get_str_fecha(fechas.get_lastday_of_month(), ctes.APP_FMT_FECHA_DB)
            fechasstr = '{0}  -  {1}'.format(fechas.format_cadena(desde, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA),
                                             fechas.format_cadena(hasta, ctes.APP_FMT_FECHA_DB, ctes.APP_FMT_FECHA))

        tipocitawhere = " and historia.cosm_tipo = {tipo}".format(tipo=tipocita)
        swhere = "{0}".format(tipocitawhere)
        if len(desde) > 0:
            swhere = " {tipo} and date(historia.cosm_fechaproxcita) between '{desde}' and '{hasta}' ".format(
                tipo=tipocitawhere,
                desde=desde,
                hasta=hasta)

        data = tgrid_dao.run_grid(grid_nombre='proxcitas', swhere=swhere)
        return data, fechasstr

    def listar_odonto(self, filtro, desde, hasta, limit=30, offset=0):
        tupla_desc = ('ate_id',
                      'ate_fechacrea',
                      'mescrea',
                      'mescreastr',
                      'horacreastr',
                      'diacrea',
                      'genero',
                      'per_ciruc',
                      'paciente',
                      'cosm_motivo',
                      'ate_estado',
                      'ate_odontograma',
                      'ate_odontograma_sm',
                      'per_lugresidencia',
                      'lugresidencia')

        basesql = """
                    select  aten.ate_id,
                            aten.ate_fechacrea,
                            extract(month from aten.ate_fechacrea)  as mescrea,
                            to_char(aten.ate_fechacrea, 'TMMonth') as mescreastr,
                            to_char(aten.ate_fechacrea, 'HH24:MI') as horacreastr,
                            extract(day from aten.ate_fechacrea)   as diacrea,
                            coalesce(paciente.per_genero, 1)        as genero,
                            paciente.per_ciruc,
                            paciente.per_nombres || ' ' || paciente.per_apellidos as paciente,
                            aten.ate_diagnostico as cosm_motivo,
                            aten.ate_estado,
                            aten.ate_odontograma,
                            aten.ate_odontograma_sm,
                            paciente.per_lugresidencia,
                            coalesce(tlugar.lug_nombre,'') as lugresidencia
                    from todatenciones aten
                            join tpersona paciente on aten.pac_id = paciente.per_id
                            left join tlugar on paciente.per_lugresidencia = tlugar.lug_id"""

        solo_cedulas = True
        concedula = u" aten.ate_estado = 1 and coalesce(per_ciruc,'')!='' and per_id>0 " if solo_cedulas else ''
        tipocita = " 1=1 "

        filtrofechas = ""
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(ate_fechacrea) between '{desde}' and '{hasta}' ".format(
                desde=fechas.format_cadena_db(desde),
                hasta=fechas.format_cadena_db(hasta))
        elif cadenas.es_nonulo_novacio(desde) and not cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(ate_fechacrea) >= '{desde}' ".format(
                desde=fechas.format_cadena_db(desde))
        elif not cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(ate_fechacrea) <= '{hasta}' ".format(
                hasta=fechas.format_cadena_db(hasta))

        if cadenas.es_nonulo_novacio(filtro):
            palabras = cadenas.strip_upper(filtro).split()
            filtromod = []
            for cad in palabras:
                filtromod.append(u"%{0}%".format(cad))

            nombreslike = u' '.join(filtromod)
            filtrocedulas = u" per_ciruc like '{0}%'".format(cadenas.strip(filtro))

            sql = u"""{basesql}
                        where ((per_nombres||' '||per_apellidos like '{nombreslike}') or ({filtrocedulas})) and {concedula} and {tipo} {filtrofechas} order by aten.ate_fechacrea desc limit {limit} offset {offset}
                    """.format(nombreslike=nombreslike,
                               concedula=concedula,
                               tipo=tipocita,
                               limit=limit,
                               offset=offset,
                               filtrocedulas=filtrocedulas,
                               filtrofechas=filtrofechas,
                               basesql=basesql)
        else:
            sql = u"""{basesql} where {concedula} and {tipo} {filtrofechas}
                             order by aten.ate_fechacrea desc limit {limit} offset {offset}
                            """.format(basesql=basesql, limit=limit, offset=offset, concedula=concedula, tipo=tipocita,
                                       filtrofechas=filtrofechas)

        items = self.all(sql, tupla_desc)
        lenitems = len(items)
        itemsres = []
        items_dict = {}

        for item in items:
            mescrea = item['mescrea']
            diacrea = item['diacrea']
            clave = "{0}_{1}".format(mescrea, diacrea)
            if clave not in items_dict:
                items_dict[clave] = []

            items_dict[clave].append(item)

        for key in items_dict:
            first = items_dict[key][0]
            month_item = {'tipo': 'd', 'mes': '{0} {1}'.format(first['mescreastr'], int(first['diacrea']))}
            itemsres.append(month_item)
            for item in items_dict[key]:
                itemsres.append(item)

        return itemsres, lenitems

    def listar(self, filtro, desde, hasta, tipo, limit=30, offset=0):
        tupla_desc = ('cosm_id',
                      'cosm_fechacrea',
                      'mescrea',
                      'mescreastr',
                      'horacreastr',
                      'diacrea',
                      'genero',
                      'per_ciruc',
                      'paciente',
                      'cosm_motivo',
                      'cosm_estado',
                      'cosm_fechaproxcita', 'per_lugresidencia', 'lugresidencia')

        basesql = """
                select  historia.cosm_id,
                        historia.cosm_fechacrea,
                        extract(month from historia.cosm_fechacrea)           as mescrea,
                        to_char(historia.cosm_fechacrea, 'TMMonth')           as mescreastr,
                        to_char(historia.cosm_fechacrea, 'HH24:MI')           as horacreastr,
                        extract(day from historia.cosm_fechacrea)             as diacrea,
                        coalesce(paciente.per_genero, 1)                      as genero,
                        paciente.per_ciruc,
                        paciente.per_nombres || ' ' || paciente.per_apellidos as paciente,
                        historia.cosm_motivo,
                        historia.cosm_estado,
                        historia.cosm_fechaproxcita,
                        paciente.per_lugresidencia,
                        coalesce(tlugar.lug_nombre,'') as lugresidencia
                from tconsultamedica historia
                        join tpersona paciente on historia.pac_id = paciente.per_id
                        left join tlugar on paciente.per_lugresidencia = tlugar.lug_id
                """

        solo_cedulas = True
        concedula = u" historia.cosm_estado = 1 and coalesce(per_ciruc,'')!='' and per_id>0 " if solo_cedulas else ''
        tipocita = "  historia.cosm_tipo = {0}".format(tipo)

        filtrofechas = ""
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(cosm_fechacrea) between '{desde}' and '{hasta}' ".format(
                desde=fechas.format_cadena_db(desde),
                hasta=fechas.format_cadena_db(hasta))
        elif cadenas.es_nonulo_novacio(desde) and not cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(cosm_fechacrea) >= '{desde}' ".format(
                desde=fechas.format_cadena_db(desde))
        elif not cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            filtrofechas = " and date(cosm_fechacrea) <= '{hasta}' ".format(
                hasta=fechas.format_cadena_db(hasta))

        if cadenas.es_nonulo_novacio(filtro):
            palabras = cadenas.strip_upper(filtro).split()
            filtromod = []
            for cad in palabras:
                filtromod.append(u"%{0}%".format(cad))

            nombreslike = u' '.join(filtromod)
            filtrocedulas = u" per_ciruc like '{0}%'".format(cadenas.strip(filtro))

            sql = u"""{basesql}
                                where ((per_nombres||' '||per_apellidos like '{nombreslike}') or ({filtrocedulas})) and {concedula} and {tipo} {filtrofechas} order by historia.cosm_fechacrea desc limit {limit} offset {offset}
                            """.format(nombreslike=nombreslike,
                                       concedula=concedula,
                                       tipo=tipocita,
                                       limit=limit,
                                       offset=offset,
                                       filtrocedulas=filtrocedulas,
                                       filtrofechas=filtrofechas,
                                       basesql=basesql)
        else:
            sql = u"""{basesql} where {concedula} and {tipo} {filtrofechas}
                     order by historia.cosm_fechacrea desc limit {limit} offset {offset}
                    """.format(basesql=basesql, limit=limit, offset=offset, concedula=concedula, tipo=tipocita,
                               filtrofechas=filtrofechas)

        items = self.all(sql, tupla_desc)
        lenitems = len(items)
        itemsres = []
        items_dict = {}

        for item in items:
            mescrea = item['mescrea']
            diacrea = item['diacrea']
            clave = "{0}_{1}".format(mescrea, diacrea)
            if clave not in items_dict:
                items_dict[clave] = []

            items_dict[clave].append(item)

        for key in items_dict:
            first = items_dict[key][0]
            month_item = {'tipo': 'd', 'mes': '{0} {1}'.format(first['mescreastr'], int(first['diacrea']))}
            itemsres.append(month_item)
            for item in items_dict[key]:
                itemsres.append(item)

        return itemsres, lenitems

    def get_datos_historia(self, cosm_id):
        """
        Retorna toda la informacion relacionada con una historia medica registrada
        :param cosm_id:
        :return:
        """

        sql = u"""
        select historia.cosm_id,
               historia.med_id,
               historia.cosm_fechacrea,
               historia.cosm_motivo,
               historia.cosm_enfermactual,
               historia.cosm_hallazgoexamfis,
               historia.cosm_exmscompl,
               historia.cosm_tratamiento,
               historia.cosm_receta,
               historia.cosm_indicsreceta,
               historia.cosm_recomendaciones,
               historia.cosm_diagnostico,
               historia.cosm_diagnosticos,
               historia.cosm_diagnosticoal,
               historia.user_crea,
               historia.cosm_fechaproxcita,
               paciente.per_id,
                    paciente.per_ciruc,
                    paciente.per_nombres,
                    paciente.per_apellidos,
                    paciente.per_nombres ||' '||paciente.per_apellidos as paciente, 
                    paciente.per_direccion,
                    paciente.per_telf,
                    paciente.per_movil,
                    paciente.per_email,
                    paciente.per_fecreg,
                    paciente.per_tipo,
                    paciente.per_lugnac,
                    paciente.per_nota,
                    paciente.per_fechanac,
                    paciente.per_genero,
                    paciente.per_estadocivil,
                    paciente.per_lugresidencia,
                    paciente.per_ocupacion,
                    coalesce(lv.lval_nombre, '') as ocupacion,
                    cie.cie_valor ciediagnostico, 
                    get_diagnosticos(historia.cosm_diagnosticos) as diagnosticos,
                    cie.cie_key ciekey,
                    historia.cosm_odontograma,
                    historia.cosm_fechaedita,
                    historia.cosm_useredita
                      from tconsultamedica historia
        join tpersona paciente on historia.pac_id = paciente.per_id
        left join tcie10 cie on  historia.cosm_diagnostico = cie.cie_id
        left join tlistavalores lv on paciente.per_ocupacion = lv.lval_id
        where historia.cosm_id = {0}
        """.format(cosm_id)

        tupla_desc = ('cosm_id',
                      'med_id',
                      'cosm_fechacrea',
                      'cosm_motivo',
                      'cosm_enfermactual',
                      'cosm_hallazgoexamfis',
                      'cosm_exmscompl',
                      'cosm_tratamiento',
                      'cosm_receta',
                      'cosm_indicsreceta',
                      'cosm_recomendaciones',
                      'cosm_diagnostico',
                      'cosm_diagnosticos',
                      'cosm_diagnosticoal',
                      'user_crea',
                      'cosm_fechaproxcita',
                      'per_id',
                      'per_ciruc',
                      'per_nombres',
                      'per_apellidos',
                      'per_direccion',
                      'paciente',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'per_fecreg',
                      'per_tipo',
                      'per_lugnac',
                      'per_nota',
                      'per_fechanac',
                      'per_genero',
                      'per_estadocivil',
                      'per_lugresidencia',
                      'per_ocupacion',
                      'ocupacion',
                      'ciediagnostico',
                      'diagnosticos',
                      'ciekey',
                      'cosm_odontograma', 'cosm_fechaedita', 'cosm_useredita')

        datos_cita_medica = self.first(sql, tupla_desc)

        form_paciente = {}
        form_datosconsulta = {}
        for key in datos_cita_medica:
            if key.startswith('per_'):
                form_paciente[key] = datos_cita_medica[key]
            else:
                form_datosconsulta[key] = datos_cita_medica[key]

        form_antecedentes = self.get_valores_adc_citamedica(1, cosm_id)
        form_examsfisicos = self.get_valores_adc_citamedica(3, cosm_id)
        form_revxsistemas = self.get_valores_adc_citamedica(2, cosm_id)

        return {
            'paciente': form_paciente,
            'datosconsulta': form_datosconsulta,
            'antecedentes': form_antecedentes,
            'examsfisicos': form_examsfisicos,
            'revxsistemas': form_revxsistemas
        }

    def get_form_valores(self, catc_id):
        """
        Retorna array de valores para las categorias
        :param catc_id:
        :return:
        """
        sql = u"""        
        select cmtv_id, cmtv_cat, cmtv_nombre, cmtv_valor, '' as valorreg, cmtv_tinput, cmtv_unidad from tconsultam_tiposval
            where cmtv_cat = {0} order by cmtv_orden
        """.format(catc_id)

        tupla_desc = ('cmtv_id', 'cmtv_cat', 'cmtv_nombre', 'cmtv_valor', 'valorreg', 'cmtv_tinput', 'cmtv_unidad')

        return self.all(sql, tupla_desc)

    def get_odontograma(self, per_ciruc):
        sql = u"""select historia.cosm_id, historia.cosm_fechacrea, paciente.per_ciruc, 
                                paciente.per_nombres||' '||paciente.per_apellidos as paciente, historia.cosm_odontograma                                 
                                from tconsultamedica historia
                                join tpersona paciente on historia.pac_id = paciente.per_id and 
                                paciente.per_ciruc = '{0}' order by historia.cosm_id desc""".format(per_ciruc)
        tupla_desc = ('cosm_id', 'cosm_fechacrea', 'per_ciruc', 'paciente', 'cosm_odontograma')

        respuesta = self.all(sql, tupla_desc)
        if respuesta is not None and len(respuesta) > 0:
            return respuesta[0]

    def get_ultima_atencion_paciente(self, per_ciruc):
        sql = u"""select historia.cosm_id, historia.cosm_fechacrea, paciente.per_ciruc, 
                        paciente.per_nombres||' '||paciente.per_apellidos as paciente, historia.cosm_motivo 
                        from tconsultamedica historia
                        join tpersona paciente on historia.pac_id = paciente.per_id and 
                        paciente.per_ciruc = '{0}' order by historia.cosm_id desc""".format(per_ciruc)
        tupla_desc = ('cosm_id', 'cosm_fechacrea', 'per_ciruc', 'paciente', 'cosm_motivo')

        respuesta = self.all(sql, tupla_desc)
        if respuesta is not None and len(respuesta) > 0:
            return respuesta[0]['cosm_id']
            # return respuesta[0]

        return None

    def get_valores_adc_citamedica(self, catc_id, cosm_id):
        sql = u"""
        select cmtval.cmtv_id, cmtval.cmtv_cat, cmtval.cmtv_nombre, cmtval.cmtv_valor, 
               cmtval.cmtv_tinput, coalesce(cval.valcm_valor,'') as valorreg 
            from tconsultam_tiposval cmtval
            left join tconsultam_valores cval on cmtval.cmtv_id = cval.valcm_tipo
                        where cmtv_cat = {0} and cval.cosm_id = {1} order by cmtval.cmtv_orden;
        """.format(catc_id, cosm_id)

        tupla_desc = ('cmtv_id', 'cmtv_cat', 'cmtv_nombre', 'cmtv_valor', 'cmtv_tinput', 'valorreg')
        return self.all(sql, tupla_desc)

    def get_valores_adc_odonto(self, catc_id, od_antid):
        sql = u"""
        select cmtval.cmtv_id, cmtval.cmtv_cat, cmtval.cmtv_nombre, cmtval.cmtv_valor, 
               cmtval.cmtv_tinput, coalesce(cval.valcm_valor,'') as valorreg 
            from tconsultam_tiposval cmtval
            left join tconsultam_valores cval on cmtval.cmtv_id = cval.valcm_tipo
                        where cmtv_cat = {0} and cval.od_antid = {1} order by cmtval.cmtv_orden;
        """.format(catc_id, od_antid)

        tupla_desc = ('cmtv_id', 'cmtv_cat', 'cmtv_nombre', 'cmtv_valor', 'cmtv_tinput', 'valorreg')
        return self.all(sql, tupla_desc)

    def get_cie10data(self):
        sql = u"select cie_id, cie_key, cie_valor, cie_key||'-'||cie_valor as ciekeyval  from tcie10 order by cie_key"
        tupla_desc = ('cie_id', 'cie_key', 'cie_valor', 'ciekeyval')

        return self.all(sql, tupla_desc)

    def registra_datosadc_consmedica(self, cosm_id, listadatosadc):
        for item in listadatosadc:
            codcat = item['cmtv_cat']
            valorpropiedad = item['valorreg']
            codtipo = item['cmtv_id']
            tconsultmvalores = TConsultaMedicaValores()
            tconsultmvalores.cosm_id = cosm_id
            tconsultmvalores.valcm_tipo = codtipo
            tconsultmvalores.valcm_valor = valorpropiedad
            tconsultmvalores.valcm_categ = codcat
            self.dbsession.add(tconsultmvalores)

    def procesar_array_diags(self, diagnosticos):
        diags_codes = []
        for diag in diagnosticos:
            if diag is not None:
                if type(diag) is dict:
                    diags_codes.append(str(diag['cie_id']))
                else:
                    diags_codes.append(str(diag))

        diags_codes_str = ",".join(diags_codes)
        return diags_codes_str

    def get_cod_diagnostico(self, diganostico):
        diag_code = None
        if diganostico is not None:
            if type(diganostico) is dict:
                diag_code = str(diganostico['cie_id'])
            else:
                diag_code = str(diganostico)

        return diag_code

    def clone_model(self, model):
        """Clone an arbitrary sqlalchemy model object without its primary key values."""
        # Ensure the model's data is loaded before copying.
        table = model.__table__
        non_pk_columns = [k for k in table.columns.keys() if k not in table.primary_key]
        data = {c: getattr(model, c) for c in non_pk_columns}
        # data.update(kwargs)
        clone = model.__class__(**data)

        return clone

    def actualizar(self, form, useredita):
        datosconsulta = form['datosconsulta']
        tconsultamedica = self.dbsession.query(TConsultaMedica).filter(
            TConsultaMedica.cosm_id == datosconsulta['cosm_id']).first()
        if tconsultamedica is not None:

            new_consultamedica = self.clone_model(tconsultamedica)

            tconsultamedica.cosm_estado = 2
            tconsultamedica.cosm_fechaanula = datetime.now()
            tconsultamedica.cosm_obsanula = 'anulado por edición'
            tconsultamedica.cosm_useranula = useredita

            if not cadenas.es_nonulo_novacio(datosconsulta['cosm_motivo']):
                raise ErrorValidacionExc('Debe especificar el motivo de la consulta')

            new_consultamedica.cosm_id = None
            new_consultamedica.cosm_motivo = datosconsulta['cosm_motivo']
            new_consultamedica.cosm_enfermactual = datosconsulta['cosm_enfermactual']
            new_consultamedica.cosm_hallazgoexamfis = datosconsulta['cosm_hallazgoexamfis']
            new_consultamedica.cosm_exmscompl = datosconsulta['cosm_exmscompl']
            new_consultamedica.cosm_tratamiento = datosconsulta['cosm_tratamiento']
            new_consultamedica.cosm_receta = datosconsulta['cosm_receta']
            new_consultamedica.cosm_indicsreceta = datosconsulta['cosm_indicsreceta']
            new_consultamedica.cosm_recomendaciones = datosconsulta['cosm_recomendaciones']
            new_consultamedica.cosm_fechaedita = datetime.now()
            new_consultamedica.cosm_useredita = useredita
            new_consultamedica.cosm_estado = 1
            new_consultamedica.cosm_fechaanula = None
            new_consultamedica.cosm_obsanula = None

            diagnosticos_array_aux = datosconsulta['diagnosticos']
            # filtrar diagnosticos null
            diagnosticos_array = []
            for item in diagnosticos_array_aux:
                if item is not None:
                    diagnosticos_array.append(item)

            diagnosticos = self.procesar_array_diags(diagnosticos_array)
            first_diagnostico = None
            if diagnosticos_array is not None and len(diagnosticos_array) > 0:
                first_diagnostico = self.get_cod_diagnostico(diagnosticos_array[0])

            if not cadenas.es_nonulo_novacio(diagnosticos):
                raise ErrorValidacionExc("Debe especificar el diagnóstico")

            new_consultamedica.cosm_diagnosticos = diagnosticos
            new_consultamedica.cosm_diagnostico = first_diagnostico
            new_consultamedica.cosm_diagnosticoal = datosconsulta['cosm_diagnosticoal']
            new_consultamedica.cosm_odontograma = datosconsulta['cosm_odontograma']

            cosm_fechaproxcita = datosconsulta['cosm_fechaproxcita']
            if cadenas.es_nonulo_novacio(cosm_fechaproxcita):
                cosm_fechaproxcita_parsed = fechas.parse_cadena(cosm_fechaproxcita)
                new_consultamedica.cosm_fechaproxcita = cosm_fechaproxcita_parsed

            self.dbsession.add(new_consultamedica)
            self.dbsession.flush()
            cosm_id = new_consultamedica.cosm_id
            print('Valor del nuevo id generado es:')
            print(cosm_id)

            # 3 Registro de antecendentes:
            # Esto se registra como lista de valores
            antecedentes = form['antecedentes']
            examsfisicos = form['examsfisicos']
            revxsistemas = form['revxsistemas']

            self.registra_datosadc_consmedica(cosm_id, antecedentes)
            self.registra_datosadc_consmedica(cosm_id, examsfisicos)
            self.registra_datosadc_consmedica(cosm_id, revxsistemas)

            return u"Actualizado exitósamente", cosm_id

    def registrar(self, form, usercrea):
        # 1 regstro de datos del paciente
        form_paciente = form['paciente']

        # Verificar si el paciente ya esta registrado:
        per_id = form_paciente['per_id']
        if per_id == 0 or per_id is None:
            raise ErrorValidacionExc('Debe registrar primero los datos del paciente')

        # 2 registro de la cita medica
        datosconsulta = form['datosconsulta']

        # Verificar que se ingrese el motivo de la consulta
        if not cadenas.es_nonulo_novacio(datosconsulta['cosm_motivo']):
            raise ErrorValidacionExc(u"Debe ingresar el motivo de la consulta")

        tconsultamedica = TConsultaMedica()
        tconsultamedica.pac_id = per_id
        tconsultamedica.med_id = usercrea
        tconsultamedica.cosm_fechacita = datetime.now()
        tconsultamedica.cosm_fechacrea = datetime.now()
        tconsultamedica.cosm_motivo = datosconsulta['cosm_motivo']
        tconsultamedica.cosm_enfermactual = datosconsulta['cosm_enfermactual']
        tconsultamedica.cosm_hallazgoexamfis = datosconsulta['cosm_hallazgoexamfis']
        tconsultamedica.cosm_exmscompl = datosconsulta['cosm_exmscompl']
        tconsultamedica.cosm_tratamiento = datosconsulta['cosm_tratamiento']
        tconsultamedica.cosm_receta = datosconsulta['cosm_receta']
        tconsultamedica.cosm_indicsreceta = datosconsulta['cosm_indicsreceta']
        tconsultamedica.cosm_recomendaciones = datosconsulta['cosm_recomendaciones']
        cosm_tipo = 1
        if 'cosm_tipo' in datosconsulta:
            cosm_tipo = datosconsulta['cosm_tipo']

        tconsultamedica.cosm_tipo = cosm_tipo

        # datosconsulta.diagnosticos se debe registrar un array de diagnosticos
        diagnosticos_array = datosconsulta['diagnosticos']
        diagnosticos = self.procesar_array_diags(diagnosticos_array)
        first_diagnostico = None
        if diagnosticos_array is not None and len(diagnosticos_array) > 0:
            first_diagnostico = self.get_cod_diagnostico(diagnosticos_array[0])

        if not cadenas.es_nonulo_novacio(diagnosticos):
            raise ErrorValidacionExc("Debe especificar el diagnóstico")

        tconsultamedica.cosm_diagnosticos = diagnosticos
        tconsultamedica.cosm_diagnostico = first_diagnostico
        tconsultamedica.cosm_diagnosticoal = datosconsulta['cosm_diagnosticoal']

        if 'cosm_fechaproxcita' in datosconsulta:
            cosm_fechaproxcita = datosconsulta['cosm_fechaproxcita']
            if cadenas.es_nonulo_novacio(cosm_fechaproxcita):
                cosm_fechaproxcita_parsed = fechas.parse_cadena(cosm_fechaproxcita)
                tconsultamedica.cosm_fechaproxcita = cosm_fechaproxcita_parsed

        tconsultamedica.user_crea = usercrea

        if 'cosm_odontograma' in datosconsulta:
            tconsultamedica.cosm_odontograma = datosconsulta['cosm_odontograma']

        self.dbsession.add(tconsultamedica)
        self.dbsession.flush()
        cosm_id = tconsultamedica.cosm_id

        # 3 Registro de antecendentes:
        # Esto se registra como lista de valores
        antecedentes = form['antecedentes']
        examsfisicos = form['examsfisicos']
        revxsistemas = form['revxsistemas']
        # diagnostico = form['diagnostico']

        self.registra_datosadc_consmedica(cosm_id, antecedentes)
        self.registra_datosadc_consmedica(cosm_id, examsfisicos)
        self.registra_datosadc_consmedica(cosm_id, revxsistemas)
        # self.registra_datosadc_consmedica(cosm_id, diagnostico)

        return u"Registrado exitósamente", cosm_id

    def buscar_categoria_valor(self, valor, categoria):
        """
        Busca la categoria de un valor
        :param valor:
        :param categoria:
        :return:
        """
        # CAtegoria 1,2: Presion (Presion Sistolica/Presion Diastóica)
        result = ""
        color = ""
        if categoria == 1:
            valorespresion = valor.split("/")
            if len(valorespresion) == 2:
                sistolica = float(valorespresion[0])
                diastolica = float(valorespresion[1])
                sql = u"""select cmcv_nombrecat, cmcv_color from tconsultam_clasificaval where 
                            cmcv_cat =1 and 
                            ( {0} between cmcv_min and cmcv_max ) and
                            ( {1} between cmcv_minb and cmcv_maxb ) """.format(sistolica, diastolica)
                tupla_desc = ('cmcv_nombrecat', 'cmcv_color')
                resa = self.all(sql, tupla_desc)

                if len(resa) > 0:
                    result = resa[0]['cmcv_nombrecat']
                    color = resa[0]['cmcv_color']

        if categoria == 3:
            if len(cadenas.strip(valor)) > 0:
                valimc = float(valor)
                sql = u"""select cmcv_nombrecat, cmcv_color from tconsultam_clasificaval where 
                                            cmcv_cat =3 and {0} between cmcv_min and cmcv_max """.format(valimc)
                tupla_desc = ('cmcv_nombrecat', 'cmcv_color')
                resa = self.all(sql, tupla_desc)
                if len(resa) > 0:
                    result = resa[0]['cmcv_nombrecat']
                    color = resa[0]['cmcv_color']

        return result, color
