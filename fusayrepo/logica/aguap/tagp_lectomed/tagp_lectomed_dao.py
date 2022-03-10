# coding: utf-8
"""
Fecha de creacion 5/17/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.aguap.tagp_models import TAgpLectoMed
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.public.tmes_dao import PublicTMesDao
from fusayrepo.utils import cadenas, fechas

log = logging.getLogger(__name__)


class LectoMedAguaDao(BaseDao):

    def get_form(self):

        tmesdao = PublicTMesDao(self.dbsession)
        meses = tmesdao.listar()
        anios = tmesdao.get_current_previus_year()

        form = {
            'lmd_id': 0,
            'mdg_id': 0,
            'lmd_anio': fechas.get_anio_actual(),
            'lmd_mes': fechas.get_mes_actual(),
            'lmd_valor': 0,
            'lmd_valorant': 0.0,
            'lmd_consumo': 0,
            'lmd_userlee': 0,
            'lmd_desde': '',
            'lmd_hasta': '',
            'mdg_num': '',
            'lmd_obs': ''
        }

        valid_fl = [
            {'name': 'mdg_num', 'msg': 'Debe ingresar el número del medidor'},
            {'name': 'mdg_id', 'msg': 'Debe buscar el medidor', 'select': True},
            {'name': 'lmd_mes', 'msg': 'Debe seleccionar el mes', 'select': True},
            {'name': 'lmd_valor', 'msg': 'Debe ingresar el valor de la lectura actual'}
        ]

        # meses.append({'mes_id': 0, 'mes_nombre': 'Elija el mes', 'mes_corto': ''})

        steps = [
            {'label': 'Buscar referente'},
            {'label': 'Seleccionar medidor'},
            {'label': 'Registra Lectura'}
        ]

        return {
            'form': form,
            'meses': meses,
            'anios': anios,
            'vfl': valid_fl,
            'steps': steps
        }

    @staticmethod
    def _aux_valid_lmd_valor(form):
        if not cadenas.es_nonulo_novacio(form['lmd_valor']):
            raise ErrorValidacionExc('Ingrese el valor de la lectura actual')

        lmd_valor = float(form['lmd_valor'])
        if lmd_valor <= 0:
            raise ErrorValidacionExc('Valor incorrecto de lectura actual')

    @staticmethod
    def _aux_valid_lmd_valorant(form):
        if not cadenas.es_nonulo_novacio(form['lmd_valorant']):
            raise ErrorValidacionExc('Ingrese el valor de la lectura anterior')

        lmd_valor = float(form['lmd_valorant'])
        if lmd_valor <= 0:
            raise ErrorValidacionExc('Valor incorrecto de lectura anterior')

    @staticmethod
    def _aux_valid_mdg_id(form):
        if not cadenas.es_nonulo_novacio(form['mdg_id']):
            raise ErrorValidacionExc('Debe especificar el numero del medidor')

    @staticmethod
    def _aux_valid_lmd_mes(form):
        if not cadenas.es_nonulo_novacio(form['lmd_mes']):
            raise ErrorValidacionExc('Ingrese el mes al que corresponde la lectura actual')

        lmd_valor = int(form['lmd_mes'])
        if lmd_valor <= 0:
            raise ErrorValidacionExc('Debe seleccionar el mes correspondiente a la lectura actual del medidor')

    @staticmethod
    def _aux_valid_lmd_anio(form):
        if not cadenas.es_nonulo_novacio(form['lmd_anio']):
            raise ErrorValidacionExc('Ingrese el año al que corresponde la lectura actual')

        lmd_valor = int(form['lmd_mes'])
        if lmd_valor <= 0:
            raise ErrorValidacionExc('Debe seleccionar el mes correspondiente a la lectura actual del medidor')

    @staticmethod
    def _aux_valid_lmd_consumo(form):
        if not cadenas.es_nonulo_novacio(form['lmd_consumo']):
            raise ErrorValidacionExc('El valor de lectura actual es incorrecto')

        lmd_consumo = float(form['lmd_consumo'])
        if lmd_consumo < 0:
            raise ErrorValidacionExc('El valor de lectura actual es incorrecto')

    def find_by_id(self, lmd_id):
        return self.dbsession.query(TAgpLectoMed).filter(TAgpLectoMed.lmd_id == lmd_id).first()

    def find_per_id_from_mdg_id(self, mdg_id):
        """
        Busca el codigo del referente dado el codigo del medidor
        """
        sql = """
        select contra.per_id
                from tagp_medidor med
                join tagp_contrato contra on med.cna_id = contra.cna_id
                where med.mdg_id = {0}
        """.format(mdg_id)
        return self.first_col(sql, 'per_id')

    def existe_lectura(self, mdg_id, lmd_mes, lmd_anio):
        sql = """
        select count(*) as cuenta from tagp_lectomed where mdg_id = {0} and lmd_mes = {1} and lmd_anio = {2} 
        and lmd_estado = 1
        """.format(mdg_id, lmd_mes, lmd_anio)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def chk_existe_lectomed(self, mdg_id, lmd_mes, lmd_anio):
        if self.existe_lectura(mdg_id, lmd_mes, lmd_anio):
            raise ErrorValidacionExc(
                'Ya se encuentra registrado lectura de medidor para el mes seleccionado')

    def get_back_lecto(self, mdg_id, anio, mes):
        aux_fecha_str = '{0}/{1}/{2}'.format('01', mes, anio)
        aux_fecha_str_db = fechas.format_cadena_db(aux_fecha_str)
        sql = """
        select lm.lmd_id, lm.lmd_mes, lm.lmd_valorant,  lm.lmd_valor, lm.lmd_fechacrea, lm.lmd_usercrea, lm.lmd_obs,
        lmd_consumo, vu.referente as usercrea, mes.mes_nombre
        from tagp_lectomed lm
        join vusers vu on lm.lmd_usercrea = vu.us_id
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        join tagp_medidor md on lm.mdg_id = md.mdg_id
        where lm.lmd_estado = 1 and md.mdg_id = '{mdg_id}' and 
        to_date('01-'||lmd_mes||'-'|| lmd_anio,'dd-mm-yyyy')<'{fecha}' order by lm.lmd_fechacrea desc limit 1
        """.format(mdg_id=mdg_id, fecha=aux_fecha_str_db)
        tupla_desc = ('lmd_id', 'lmd_mes', 'lmd_valorant', 'lmd_valor', 'lmd_fechacrea', 'lmd_usercrea', 'lmd_obs',
                      'lmd_consumo', 'usercrea', 'mes_nombre')

        return self.first(sql, tupla_desc)

    def get_previous_lectomed(self, mdg_num, anio, mes):
        anio_param = anio
        mes_param = mes
        if int(mes) == 1:
            mes_param = 12
            anio_param = int(anio) - 1

        sql = """
        select lm.lmd_id, lm.lmd_mes, lm.lmd_valorant,  lm.lmd_valor, lm.lmd_fechacrea, lm.lmd_usercrea, lm.lmd_obs,
        lmd_consumo, vu.referente as usercrea, mes.mes_nombre
        from tagp_lectomed lm
        join vusers vu on lm.lmd_usercrea = vu.us_id
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        join tagp_medidor md on lm.mdg_id = md.mdg_id
        where md.mdg_num = '{num}' and lm.lmd_estado = 1 and lm.lmd_anio<={anio} and lm.lmd_mes<={mes} order by lm.lmd_fechacrea desc limit 1 
        """.format(num=cadenas.strip(mdg_num), anio=anio_param, mes=mes_param)

        tupla_desc = ('lmd_id', 'lmd_mes', 'lmd_valorant', 'lmd_valor', 'lmd_fechacrea', 'lmd_usercrea', 'lmd_obs',
                      'lmd_consumo', 'usercrea', 'mes_nombre')
        return self.first(sql, tupla_desc)

    def get_last_lectomed(self, mdg_num):
        sql = """
                select lm.lmd_id, lm.lmd_mes, lm.lmd_valorant, lm.lmd_valor, lm.lmd_fechacrea, lm.lmd_usercrea, lm.lmd_obs,
                lmd_consumo, vu.referente as usercrea, mes.mes_nombre
                from tagp_lectomed lm
                join vusers vu on lm.lmd_usercrea = vu.us_id
                join public.tmes mes on lm.lmd_mes = mes.mes_id
                join tagp_medidor md on lm.mdg_id = md.mdg_id
                where md.mdg_num = '{num}' and lm.lmd_estado = 1 order by lm.lmd_anio desc, lm.lmd_mes desc  limit 1 
                """.format(num=cadenas.strip(mdg_num))

        tupla_desc = ('lmd_id', 'lmd_mes', 'lmd_valorant', 'lmd_valor', 'lmd_fechacrea', 'lmd_usercrea', 'lmd_obs',
                      'lmd_consumo', 'usercrea', 'mes_nombre')
        return self.first(sql, tupla_desc)

    def crear(self, form, user_crea, sec_id, tdv_codigo):
        self._aux_valid_mdg_id(form)
        self._aux_valid_lmd_mes(form)
        self._aux_valid_lmd_valor(form)
        self._aux_valid_lmd_valorant(form)
        self._aux_valid_lmd_consumo(form)

        self.chk_existe_lectomed(mdg_id=form['mdg_id'], lmd_mes=form['lmd_mes'], lmd_anio=form['lmd_anio'])

        lectomed = TAgpLectoMed()
        lectomed.mdg_id = form['mdg_id']
        lectomed.lmd_mes = form['lmd_mes']
        lectomed.lmd_anio = form['lmd_anio']
        lectomed.lmd_valor = float(form['lmd_valor'])
        lectomed.lmd_valorant = float(form['lmd_valorant'])
        lectomed.lmd_userlee = form['lmd_userlee']
        lectomed.lmd_obs = form['lmd_obs']
        lectomed.lmd_consumo = float(form['lmd_consumo'])
        lectomed.lmd_usercrea = user_crea
        lectomed.lmd_estado = 1
        lectomed.lmd_fechacrea = datetime.now()

        desde = fechas.parse_cadena('{0}/{1}/{2}'.format('01', form['lmd_mes'], form['lmd_anio']))
        lectomed.lmd_desde = desde
        lectomed.lmd_hasta = fechas.sumar_dias(desde, 30)

        self.dbsession.add(lectomed)
        self.dbsession.flush()

        lecto_id = lectomed.lmd_id

        trn_codigo = 0

        from fusayrepo.logica.aguap.tagp_pago.tagp_adelantos import AdelantosManageUtil
        adelantos_dao = AdelantosManageUtil(self.dbsession)
        per_id = self.find_per_id_from_mdg_id(mdg_id=form['mdg_id'])
        saldo_adelantos = adelantos_dao.get_saldo_adelantos(per_id=per_id)
        if saldo_adelantos > 0.0:
            alcanza_adelanto = adelantos_dao.check_saldo_adelanto_contra_total_fact(lecto_id=lecto_id,
                                                                                    saldo_adelanto=saldo_adelantos,
                                                                                    sec_codigo=sec_id,
                                                                                    tdv_codigo=tdv_codigo)
            if alcanza_adelanto:
                trn_codigo = adelantos_dao.crear_factura(lecto_id=lecto_id, per_id=per_id, user_crea=user_crea,
                                                         sec_codigo=sec_id,
                                                         tdv_codigo=tdv_codigo)

        return trn_codigo

    def anular(self, lmd_id, lmd_useranula):
        lectomed = self.find_by_id(lmd_id)

        from fusayrepo.logica.aguap.tagp_pago.tagp_pago_dao import TagpCobroDao
        cobrodao = TagpCobroDao(self.dbsession)
        if cobrodao.is_lecto_with_pago(lmd_id=lmd_id):
            raise ErrorValidacionExc('No se puede anular esta lectura, existe un cobro realizado')

        if lectomed is not None:
            current_state = lectomed.lmd_estado
            if current_state == 1:
                lectomed.lmd_estado = 2
                lectomed.lmd_fechanula = datetime.now()
                lectomed.lmd_useranula = lmd_useranula
                self.dbsession.add(lectomed)

    def get_lectopend_by_lmd_id(self, lmd_id):
        sql = """        
                        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, mes.mes_nombre, lm.lmd_fechacrea, lm.lmd_valor, 
                        lm.lmd_usercrea, lm.lmd_estado, lm.lmd_consumo, lm.lmd_valorant, coalesce(pg.pg_id, 0) as pg_id, 
                        pg.pg_fechacrea, coalesce(pg.trn_codigo, 0) as trn_codigo, true as marcado 
                        from tagp_lectomed lm
                        left join tagp_pago pg on lm.lmd_id = pg.lmd_id and pg.pg_estado = 1                
                        join public.tmes mes on lm.lmd_mes = mes.mes_id
                        where lm.lmd_estado = 1 and lm.lmd_id = {lmd_id} and coalesce(pg.pg_id, 0)=0 order by lm.lmd_anio desc, lm.lmd_mes desc
                        """.format(lmd_id=lmd_id)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'mes_nombre', 'lmd_fechacrea', 'lmd_valor', 'lmd_usercrea',
            'lmd_estado', 'lmd_consumo', 'lmd_valorant', 'pg_id', 'pg_fechacrea', 'trn_codigo', 'marcado')
        lecturas = self.all(sql, tupla_desc)

        return lecturas

    def get_lecturas_pendientes(self, mdg_id):
        """
        Busca todas las lecturas pendientes de pago
        """
        sql = """        
                select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, mes.mes_nombre, lm.lmd_fechacrea, lm.lmd_valor, 
                lm.lmd_usercrea, lm.lmd_estado, lm.lmd_consumo, lm.lmd_valorant, coalesce(pg.pg_id, 0) as pg_id, 
                pg.pg_fechacrea, coalesce(pg.trn_codigo, 0) as trn_codigo, true as marcado 
                from tagp_lectomed lm
                left join tagp_pago pg on lm.lmd_id = pg.lmd_id and pg.pg_estado = 1                
                join public.tmes mes on lm.lmd_mes = mes.mes_id
                where lm.lmd_estado = 1 and lm.mdg_id = {mdg_id} and coalesce(pg.pg_id, 0)=0 order by lm.lmd_anio desc, lm.lmd_mes desc
                """.format(mdg_id=mdg_id)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'mes_nombre', 'lmd_fechacrea', 'lmd_valor', 'lmd_usercrea',
            'lmd_estado', 'lmd_consumo', 'lmd_valorant', 'pg_id', 'pg_fechacrea', 'trn_codigo', 'marcado')
        lecturas = self.all(sql, tupla_desc)

        return lecturas

    def get_lecturas(self, mdg_id):
        sql = """        
        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, mes.mes_nombre, lm.lmd_fechacrea, lm.lmd_valor, 
        lm.lmd_usercrea, lm.lmd_estado, lm.lmd_consumo, lm.lmd_valorant, coalesce(pg.pg_id, 0) as pg_id, 
        pg.pg_fechacrea, coalesce(pg.trn_codigo, 0) as trn_codigo from tagp_lectomed lm
        left join tagp_pago pg on lm.lmd_id = pg.lmd_id and pg.pg_estado = 1                
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        where lm.lmd_estado = 1 and lm.mdg_id = {mdg_id} order by lm.lmd_anio desc, lm.lmd_mes desc
        """.format(mdg_id=mdg_id)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'mes_nombre', 'lmd_fechacrea', 'lmd_valor', 'lmd_usercrea',
            'lmd_estado', 'lmd_consumo', 'lmd_valorant', 'pg_id', 'pg_fechacrea', 'trn_codigo')
        lecturas = self.all(sql, tupla_desc)

        # Analizar si tiene lecturas pendientes de pago
        pendientes = []
        lastpago = {}
        for item in lecturas:
            pg_id = item['pg_id']
            if pg_id == 0:
                pendientes.append(item)

        has_lecturas = False
        pagos_pend = len(pendientes) > 0
        msg = ''
        if len(lecturas) > 0:
            has_lecturas = True
            if pagos_pend:
                msg = 'Tiene pagos pendientes'
            else:
                msg = 'No tiene pagos pendientes'
                lastpago = lecturas[0]

        else:
            msg = 'No hay lecturas registradas para este medidor'

        return {
            'has_lecturas': has_lecturas,
            'has_pagos_pend': pagos_pend,
            'msg': msg,
            'lecturaspend': pendientes,
            'lastpago': lastpago
        }

    def listar_lecturas_medidor(self, mdg_id, limit=24):
        gridao = TGridDao(self.dbsession)
        where = "lm.mdg_id  ={0}".format(mdg_id)
        grid = gridao.run_grid(grid_nombre='agp_lecturas_view', where=where, limit=limit)

        return grid

    def get_lecturas_nopagadas(self, mdg_id):
        sql = """
        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, mes.mes_nombre, lm.lmd_fechacrea, lm.lmd_valor, 
        lm.lmd_usercrea, lm.lmd_estado, lm.lmd_consumo, lm.lmd_valorant 
        from tagp_lectomed lm
        join public.tmes mes on lm.lmd_mes = mes.mes_id
         where lm.lmd_id not in(
            select lmi.lmd_id from tagp_lectomed lmi join
                tagp_pago pg on lmi.lmd_id = pg.lmd_id
                where pg.pg_estado = 1 and lmi.lmd_estado = 1 and lm.mdg_id = {mdg_id}
        ) and lm.mdg_id = {mdg_id} order by lm.lmd_anio, lm.lmd_mes
        """.format(mdg_id=mdg_id)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'mes_nombre', 'lmd_fechacrea', 'lmd_valor', 'lmd_usercrea',
            'lmd_estado', 'lmd_consumo', 'lmd_valorant')

        return self.all(sql, tupla_desc)

    def get_info_basic_lectura(self, lecto_id):
        sql = """
        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, lm.lmd_valor, 
        lm.lmd_consumo, lm.lmd_fechacrea, lm.lmd_valorant, mes.mes_nombre from tagp_lectomed lm
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        where lm.lmd_id = {0}  
        """.format(lecto_id)
        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'lmd_valor', 'lmd_consumo', 'lmd_fechacrea', 'lmd_valorant',
            'mes_nombre')
        return self.first(sql, tupla_desc)

    def get_datos_lectura(self, ids):
        sql = """
        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, lm.lmd_valor, 
        lm.lmd_consumo, lm.lmd_fechacrea, lm.lmd_valorant, coalesce(pg.pg_id,0) as pg_id 
        from tagp_lectomed lm
        left join tagp_pago pg on lm.lmd_id = pg.lmd_id and pg.pg_estado = 1
        where lm.lmd_id in ({0}) order by lm.lmd_anio desc, lm.lmd_mes desc
        """.format(ids)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'lmd_valor', 'lmd_consumo', 'lmd_fechacrea', 'lmd_valorant',
            'pg_id')
        return self.all(sql, tupla_desc)
