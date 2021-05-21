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
from fusayrepo.logica.public.tmes_dao import PublicTMesDao
from fusayrepo.utils import cadenas, fechas

log = logging.getLogger(__name__)


class LectoMedAguaDao(BaseDao):

    def get_form(self):

        tmesdao = PublicTMesDao(self.dbsession)
        meses = tmesdao.get_current_previus()
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
            {'name': 'mdg_num', 'msg': 'Debe ingresar el número del medidor', 'select': True},
            {'name': 'mdg_id', 'mdg': 'Debe buscar el medidor', 'select': True},
            {'name': 'lmd_mes', 'msg': 'Debe seleccionar el mes', 'select': True},
            {'name': 'lmd_valor', 'msg': 'Debe ingresar el valor de la lectura actual'}
        ]

        meses.append({'mes_id': 0, 'mes_nombre': 'Elija el mes', 'mes_corto': ''})
        return {
            'form': form,
            'meses': meses,
            'anios': anios,
            'vfl': valid_fl
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
        if lmd_consumo <= 0:
            raise ErrorValidacionExc('El valor de lectura actual es incorrecto')

    def find_by_id(self, lmd_id):
        return self.dbsession.query(TAgpLectoMed).filter(TAgpLectoMed.lmd_id == lmd_id).first()

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

    def get_last_lectomed(self, mdg_num):
        sql = """
        select lm.lmd_id, lm.lmd_mes, lm.lmd_valor, lm.lmd_fechacrea, lm.lmd_usercrea, lm.lmd_obs,
        vu.referente as usercrea, mes.mes_nombre
        from tagp_lectomed lm
        join vusers vu on lm.lmd_usercrea = vu.us_id
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        join tagp_medidor md on lm.mdg_id = md.mdg_id
        where md.mdg_num = '{0}' and lm.lmd_estado = 1 order by lm.lmd_fechacrea desc limit 1 
        """.format(cadenas.strip(mdg_num))

        tupla_desc = ('lmd_id', 'lmd_mes', 'lmd_valor', 'lmd_fechacrea', 'lmd_usercrea', 'lmd_obs',
                      'usercrea', 'mes_nombre')
        return self.first(sql, tupla_desc)

    def crear(self, form, user_crea):
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

    def anular(self, lmd_id, lmd_useranula):
        lectomed = self.find_by_id(lmd_id)
        if lectomed is not None:
            current_state = lectomed.lmd_estado
            if current_state == 1:
                lectomed.lmd_estado = 2
                lectomed.lmd_fechanula = datetime.now()
                lectomed.lmd_useranula = lmd_useranula
                self.dbsession.add(lectomed)

    def get_lecturas(self, mdg_id):
        sql = """        
        select lm.lmd_id, lm.mdg_id, lm.lmd_anio, lm.lmd_mes, mes.mes_nombre, lm.lmd_fechacrea, lm.lmd_valor, 
        lm.lmd_usercrea, lm.lmd_estado, lm.lmd_consumo, lm.lmd_valorant, coalesce(pg.pg_id, 0) as pg_id, 
        pg.pg_fechacrea from tagp_lectomed lm
        left join tagp_pago pg on lm.lmd_id = pg.lmd_id and pg.pg_estado = 1                
        join public.tmes mes on lm.lmd_mes = mes.mes_id
        where lm.lmd_estado = 1 and lm.mdg_id = {mdg_id} order by lm.lmd_anio desc, lm.lmd_mes desc
        """.format(mdg_id=mdg_id)

        tupla_desc = (
            'lmd_id', 'mdg_id', 'lmd_anio', 'lmd_mes', 'mes_nombre', 'lmd_fechacrea', 'lmd_valor', 'lmd_usercrea',
            'lmd_estado', 'lmd_consumo', 'lmd_valorant', 'pg_id', 'pg_fechacrea')
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
                msg = 'NO tiene pagos pendientes'
                lastpago = lecturas[len(lecturas) - 1]
        else:
            msg = 'No hay lecturas registradas para este medidor'

        return {
            'has_lecturas': has_lecturas,
            'has_pagos_pend': pagos_pend,
            'msg': msg,
            'lecturaspend': pendientes,
            'lastpago': lastpago
        }

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
