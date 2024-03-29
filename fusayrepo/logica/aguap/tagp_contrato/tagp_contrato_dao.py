# coding: utf-8
"""
Fecha de creacion 4/29/21
@autor: mjapon
"""
import decimal
import logging
from datetime import datetime

from fusayrepo import utils
from fusayrepo.logica.aguap.tagp_contrato.comunidad_dao import ComunidadAguaDao
from fusayrepo.logica.aguap.tagp_contrato.tagp_medidor_dao import TagpMedidorAguaDao
from fusayrepo.logica.aguap.tagp_models import TAgpContrato
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.public.tmes_dao import PublicTMesDao
from fusayrepo.utils import cadenas, fechas, sqls

log = logging.getLogger(__name__)


class TAgpContratoDao(BaseDao):
    BASE_SQL_CONTRATOS = """
    select cn.cna_id,
               cn.per_id,
               cn.cna_fechacrea,
               cn.cna_usercrea,
               vu.referente as usercrea,
               cn.cna_estado,
               cn.cna_estadoserv,
               cn.cna_nmingas,
               com.cmn_nombre as comunidad,
               cn.cna_barrio,
               cn.cna_sector,
               cn.cna_direccion,
               cn.cna_referencia,
               cn.cna_teredad,
               cn.cna_discapacidad,
               tm.mdg_id,
               tm.mdg_num,
               per.per_nombres,
               per.per_apellidos,
               per.per_ciruc,
               per.per_nombres||' '||coalesce(per.per_apellidos,'') as nomapel,
               ic.ic_nombre as tarifa,
               ic.ic_id,
               trf.trf_id,
               case when cn.cna_estadoserv = 1 then 'Habilitado'
               when cn.cna_estadoserv = 2 then 'Suspendido'
               else 'Desconocido' end as estadoserv
        from tagp_contrato cn
        join tagp_medidor tm on cn.cna_id = tm.cna_id and tm.mdg_estado = 1
        join tpersona per on per.per_id = cn.per_id
        join vusers vu on vu.us_id = cn.cna_usercrea
        join tagp_tarifa trf on trf.trf_id = cn.cna_tarifa
        join titemconfig ic on trf.ic_id = ic.ic_id
        join public.tcomunidad com on cn.cna_barrio = com.cmn_id
    """

    BASE_TUPLA_DESC = ('cna_id',
                       'per_id',
                       'cna_fechacrea',
                       'cna_usercrea',
                       'usercrea',
                       'cna_estado',
                       'cna_estadoserv',
                       'cna_nmingas',
                       'comunidad',
                       'cna_barrio',
                       'cna_sector',
                       'cna_direccion',
                       'cna_referencia',
                       'cna_teredad',
                       'cna_discapacidad',
                       'mdg_id',
                       'mdg_num',
                       'per_nombres',
                       'per_apellidos',
                       'per_ciruc',
                       'nomapel',
                       'tarifa',
                       'ic_id',
                       'trf_id',
                       'estadoserv')

    def listar_tarifas(self):
        sql = """
        select ic.ic_id, ic.ic_nombre, ic.ic_code, trf.trf_id
        from tagp_tarifa trf join titemconfig ic on trf.ic_id = ic.ic_id
        order by ic.ic_nombre
        """

        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code', 'trf_id')
        return self.all(sql, tupla_desc)

    def get_datos_tarifa(self, trf_id):
        sql = """
        select trf_id, trf_base, ic_id from tagp_tarifa where trf_id = {0}
        """.format(trf_id)
        tupla_desc = ('trf_id', 'trf_base', 'ic_id')
        return self.first(sql, tupla_desc)

    def listar_tarifas_exceso(self, trf_id):
        sql = """
        select etr_id, trf_id, etr_desde, etr_hasta, etr_costo from tagp_tarifaexc where trf_id = {0}
        order by etr_desde asc
        """.format(trf_id)
        tupla_desc = ('etr_id', 'trf_id', 'etr_desde', 'etr_hasta', 'etr_costo')
        return self.all(sql, tupla_desc)

    def _buscar_tarifa_exceso(self, trf_id, consumo):
        sql = """
        select etr_id, trf_id, etr_desde, etr_hasta, etr_costo from tagp_tarifaexc where trf_id = {0}
        and ({1} between etr_desde and etr_hasta) limit 1
        """.format(trf_id, consumo)
        tupla_desc = ('etr_id', 'trf_id', 'etr_desde', 'etr_hasta', 'etr_costo')
        return self.first(sql, tupla_desc)

    def _get_first_tarifa_exceso(self, trf_id, consumo):
        sql = """
        select etr_id, trf_id, etr_desde, etr_hasta, etr_costo from tagp_tarifaexc 
        where abs({consumo} - etr_desde) = (select min(abs({consumo} - etr_desde)) from tagp_tarifaexc where trf_id = {trf_id})
        and trf_id = {trf_id} order by etr_desde asc limit 1
        """.format(consumo=consumo, trf_id=trf_id)

        tupla_desc = ('etr_id', 'trf_id', 'etr_desde', 'etr_hasta', 'etr_costo')
        return self.first(sql, tupla_desc)

    def get_tarifa_exceso(self, trf_id, consumo):
        tarifaexc = self._buscar_tarifa_exceso(trf_id, consumo)
        if tarifaexc is None:
            tarifaexc = self._get_first_tarifa_exceso(trf_id, consumo)

        return tarifaexc

    def get_form_anterior(self):
        refdao = TPersonaDao(self.dbsession)
        paramdao = TParamsDao(self.dbsession)
        meddao = TagpMedidorAguaDao(self.dbsession)
        form_per = refdao.get_form()
        form_contra = {
            'cna_id': 0,
            'per_id': 0,
            'cna_fechaini': '',
            'cna_fechafin': '',
            'cna_estado': 1,
            'cna_estadoserv': 1,
            'cna_nmingas': 0,
            'cna_barrio': 0,
            'cna_sector': '',
            'cna_direccion': '',
            'cna_costoinst': 0.0,
            'cna_referencia': '',
            'cna_adjunto': 0,
            'trn_codigo': 0,
            'cna_teredad': False,
            'cna_tarifa': 0,
            'cna_discapacidad': False
        }

        tarifas = self.listar_tarifas()
        comunidadao = ComunidadAguaDao(self.dbsession)
        comunidades = comunidadao.listar()

        teredad = paramdao.get_param_value('terceraEdad')
        if teredad is None:
            raise ErrorValidacionExc('No está registrado el parámetero terceraEdad, favor verificar')

        valid_fl = [
            {'name': 'cna_tarifa', 'msg': 'Debe seleccionar la tarifa', 'select': True},
            {'name': 'mdg_num', 'msg': 'Debe ingresar el número del medidor'},
            {'name': 'cna_barrio', 'msg': 'Debe seleccionar la comunidad', 'select': True},
            {'name': 'cna_direccion', 'msg': 'Debe ingresar la dirección del servicio'}
        ]

        return {
            'form': form_contra,
            'formper': form_per,
            'formmed': meddao.get_form(),
            'tarifas': tarifas,
            'comunidades': comunidades,
            'teredad': int(teredad),
            'validfl': valid_fl
        }

    def get_form(self, tipo):
        pass

    @staticmethod
    def _aux_valid_int(form, field, msg):
        field_value = form[field]
        raiseerror = False
        if cadenas.es_nonulo_novacio(field_value):
            field_value_int = int(field_value)
            if field_value_int == 0:
                raiseerror = True
        else:
            raiseerror = True
        if raiseerror:
            raise ErrorValidacionExc(msg)

    @staticmethod
    def _aux_valid_cna_tarifa(form):
        TAgpContratoDao._aux_valid_int(form, 'cna_tarifa', 'Debe ingresar la tarifa del contrato de agua')

    @staticmethod
    def _aux_valid_cna_barrio(form):
        TAgpContratoDao._aux_valid_int(form, 'cna_barrio', 'Debe ingresar la comunidad')

    @staticmethod
    def _aux_valid_cna_direccion(form):
        if not cadenas.es_nonulo_novacio(form['cna_direccion']):
            raise ErrorValidacionExc('Ingrese la dirección del servicio')

    def aux_valid_crea(self, form):
        self._aux_valid_cna_tarifa(form)
        self._aux_valid_cna_direccion(form)
        self._aux_valid_cna_barrio(form)

    def find_by_id(self, cna_id):
        return self.dbsession.query(TAgpContrato).filter(TAgpContrato.cna_id == cna_id).first()

    def get_form_edit(self, cna_id):

        sql = """
        select 
            cna_id,        
            per_id,
            cna_fechacrea,
            cna_fechaini,
            cna_fechafin,
            cna_usercrea,
            cna_estado,
            cna_estadoserv,
            cna_nmingas,
            cna_barrio,
            cna_sector,
            cna_direccion,
            cna_referencia,
            cna_adjunto,
            trn_codigo,
            cna_teredad,
            cna_costoinst,
            cna_tarifa, 
            cna_discapacidad from tagp_contrato where  cna_id = {0}
        """.format(cna_id)

        tupla_desc = ('cna_id',
                      'per_id',
                      'cna_fechacrea',
                      'cna_fechaini',
                      'cna_fechafin',
                      'cna_usercrea',
                      'cna_estado',
                      'cna_estadoserv',
                      'cna_nmingas',
                      'cna_barrio',
                      'cna_sector',
                      'cna_direccion',
                      'cna_referencia',
                      'cna_adjunto',
                      'trn_codigo',
                      'cna_teredad',
                      'cna_costoinst',
                      'cna_tarifa',
                      'cna_discapacidad')
        form_contra = self.first(sql, tupla_desc)

        tagpmeddao = TagpMedidorAguaDao(self.dbsession)
        form_med = tagpmeddao.get_form_edit(cna_id)
        tpersonadao = TPersonaDao(self.dbsession)
        formper = tpersonadao.aux_busca_por_prop_full('per_id', form_contra['per_id'])
        return {
            'form': form_contra,
            'formper': formper,
            'formmed': form_med
        }

    def editar(self, form, formref, formed, useredit, editcrearef=True):
        tagpcontrato = self.find_by_id(cna_id=form['cna_id'])

        if tagpcontrato is not None:
            self.aux_valid_crea(form)

            medidordao = TagpMedidorAguaDao(self.dbsession)
            medidordao.editar(form=formed, useredit=useredit)

            tagpcontrato.cna_tarifa = form['cna_tarifa']
            tagpcontrato.cna_barrio = form['cna_barrio']
            tagpcontrato.cna_sector = form['cna_sector']
            tagpcontrato.cna_direccion = cadenas.strip_upper(form['cna_direccion'])
            tagpcontrato.cna_referencia = cadenas.strip(form['cna_referencia'])
            tagpcontrato.cna_teredad = form['cna_teredad']

            self.dbsession.add(tagpcontrato)

            if editcrearef:
                tasidato = TasientoDao(self.dbsession)
                per_codigo, per_ciruc = tasidato.aux_save_datos_ref(formref=formref, creaupdref=True)

    def anular(self, form, useranula):
        tagpcontrago = self.find_by_id(form['cna_id'])
        if tagpcontrago is not None:
            tagpcontrago.cna_estado = 2
            tagpmeddao = TagpMedidorAguaDao(self.dbsession)
            tagpmeddao.anular_by_cna_id(cna_id=form['cna_id'], useranula=useranula)

            self.dbsession.add(tagpcontrago)

    def crear(self, form, formref, formed, usercrea, editcrearef=True):
        # Validar informacion ingresada

        self.aux_valid_crea(form)
        medidordao = TagpMedidorAguaDao(self.dbsession)

        per_codigo = int(formref['per_id'])

        if editcrearef:
            tasidato = TasientoDao(self.dbsession)
            per_codigo, per_ciruc = tasidato.aux_save_datos_ref(formref=formref, creaupdref=True)

        contratoagua = TAgpContrato()

        contratoagua.per_id = per_codigo
        contratoagua.cna_fechacrea = datetime.now()
        if cadenas.es_nonulo_novacio(form['cna_fechaini']):
            contratoagua.cna_fechaini = fechas.parse_cadena(form['cna_fechaini'])

        contratoagua.cna_usercrea = usercrea
        contratoagua.cna_estado = form['cna_estado']
        contratoagua.cna_estadoserv = form['cna_estadoserv']
        contratoagua.cna_nmingas = form['cna_nmingas']
        contratoagua.cna_barrio = form['cna_barrio']
        contratoagua.cna_fechaini = datetime.now()
        contratoagua.cna_sector = form['cna_sector']
        contratoagua.cna_direccion = cadenas.strip_upper(form['cna_direccion'])
        contratoagua.cna_referencia = cadenas.strip(form['cna_referencia'])
        contratoagua.trn_codigo = 0
        contratoagua.cna_teredad = form['cna_teredad']
        contratoagua.cna_costoinst = decimal.Decimal(form['cna_costoinst'])
        contratoagua.cna_tarifa = form['cna_tarifa']
        contratoagua.cna_discapacidad = form['cna_discapacidad']

        self.dbsession.add(contratoagua)
        self.flush()
        cna_id = contratoagua.cna_id

        formed['cna_id'] = cna_id
        medidordao.crear(form=formed, usercrea=usercrea)

        return cna_id

    def find_by_nummed(self, mdg_num):
        sql = "{0} where tm.mdg_num = '{1}'".format(self.BASE_SQL_CONTRATOS, cadenas.strip(mdg_num))
        return self.first(sql, self.BASE_TUPLA_DESC)

    def filter_by_nummed(self, filtro):
        if cadenas.es_nonulo_novacio(filtro):
            sql = "{0} where tm.mdg_num like '{1}%' order by tm.mdg_num limit 50 ".format(self.BASE_SQL_CONTRATOS,
                                                                                          cadenas.strip_upper(filtro))
            return self.all(sql, self.BASE_TUPLA_DESC)
        else:
            return []

    def find_by_per_codigo(self, per_codigo):
        sql = "{0} where per.per_id = {1}".format(self.BASE_SQL_CONTRATOS, per_codigo)
        return self.all(sql, self.BASE_TUPLA_DESC)

    def find_by_mdg_id(self, mdg_id):
        sql = "{0} where tm.mdg_id = {1}".format(self.BASE_SQL_CONTRATOS, cadenas.strip(str(mdg_id)))
        return self.first(sql, self.BASE_TUPLA_DESC)

    def listar_validos(self):
        sql = "{0} where cn.cna_estado = 1 order by nomapel asc".format(self.BASE_SQL_CONTRATOS)
        return self.all(sql, self.BASE_TUPLA_DESC)

    def listar_grid_for_view(self, filtro):
        griddao = TGridDao(self.dbsession)
        wherefiltro = self.get_filtro_contratos_view(filtro)
        return griddao.run_grid(grid_nombre='agp_contratos_view', wherefiltro=wherefiltro)

    def get_filtro_contratos(self, filtro):
        filtro = self.get_filtro_nomapelcedul(filtro)
        whereper = ''
        if cadenas.es_nonulo_novacio(filtro):
            whereper = u"""and ( {0} )""".format()
        return whereper

    def get_filtro_contratos_view(self, filtro):
        nomapelcedul = self.get_filtro_nomapelcedul(filtro)
        where = ''
        if cadenas.es_nonulo_novacio(filtro):
            filtronumed = " or (tm.mdg_num like '%{0}%')".format(filtro.strip())
            where = """
            and ( {0} {1} )
            """.format(nomapelcedul, filtronumed)
        return where

    def get_filtro_nomapelcedul(self, filtro):
        return sqls.get_filtro_nomapelcedul(filtro)

    def get_grid_contratos(self, filtro):
        tgriddao = TGridDao(self.dbsession)
        whereper = self.get_filtro_contratos(filtro=filtro)
        return tgriddao.run_grid(grid_nombre='agp_contratos', whereper=whereper)

    def get_grid_lecturas(self, filtro, anio, mes, estado):
        tgriddao = TGridDao(self.dbsession)
        whereper = self.get_filtro_contratos(filtro=filtro)
        wherelecto = ' and lm.lmd_anio =  {0}'.format(anio)

        joinlecto = 'left join'
        wherelast = ''
        if int(mes) > 0:
            wherelecto += ' and lm.lmd_mes = {0}'.format(mes)

        if int(estado) == 1:
            wherelast = 'where  coalesce(lm.lmd_id,0) = 0'
        elif int(estado) == 2:
            joinlecto = 'join'

        return tgriddao.run_grid(grid_nombre='agp_lecturas', whereper=whereper, wherelecto=wherelecto,
                                 joinlecto=joinlecto, wherelast=wherelast, anio=anio, mes=mes)

    def get_grid_pagos(self, filtro, anio, mes, estado):
        tgriddao = TGridDao(self.dbsession)
        whereper = self.get_filtro_contratos(filtro=filtro)
        wherelecto = ' and lm.lmd_anio =  {0}'.format(anio)

        joinlecto = 'left join'
        wherelast = ''
        if int(mes) > 0:
            wherelecto += ' and lm.lmd_mes = {0}'.format(mes)

        if int(estado) == 1:
            wherelast = 'where coalesce(pg.trn_codigo,0) = 0'
        elif int(estado) == 2:
            joinlecto = 'join'
            wherelast = 'where pg.trn_codigo>0'

        return tgriddao.run_grid(grid_nombre='agp_pagos', whereper=whereper, wherelecto=wherelecto,
                                 joinlecto=joinlecto, wherelast=wherelast, anio=anio, mes=mes)

    def get_form_filtros_listados(self):
        form = {
            'anio': fechas.get_anio_actual(),
            'mes': fechas.get_mes_actual(),
            'estado': 0,
            'filtro': ''
        }

        tmesdao = PublicTMesDao(self.dbsession)
        meses = tmesdao.listar()
        meses.append(tmesdao.get_mes_todos())

        anios = tmesdao.get_current_previus_year()
        estados = [{'label': 'Todos', 'value': 0},
                   {'label': 'Pendientes', 'value': 1},
                   {'label': 'Registrados', 'value': 2}]
        return {
            'form': form,
            'meses': meses,
            'anios': anios,
            'estados': estados
        }
