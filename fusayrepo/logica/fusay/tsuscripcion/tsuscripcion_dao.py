# coding: utf-8
"""
Fecha de creacion 1/21/21
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tsuscripcion.tsuscripcion_model import TSuscripcion
from fusayrepo.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TSuscripcionDao(BaseDao):

    @staticmethod
    def get_form(codref):
        form = {
            'sus_id': 0,
            'pln_id': 0,
            'per_id': codref,
            'sus_estado': 0,
            'sus_diacobro': 1,
            'sus_diasgracia': 0,
            'sus_periodicidad': 1,
            'sus_observacion': '',
            'sus_plantobsfact': '',
            'sus_fechainiserv': '',
            'sus_fechainiservobj': ''
        }

        return form

    def get_detalles_suscrip(self, sus_id):
        sql = """
        select a.sus_id, a.pln_id, a.per_id, a.sus_estado, c.sue_nombre as estado,  a.sus_diacobro, a.sus_diasgracia, 
        a.sus_periodicidad, a.sus_fechacrea, a.sus_observacion, a.sus_plantobsfact, b.pln_nombre, b.pln_estado, 
        b.trn_codigo, a.sus_fechainiserv, a.sus_usercrea, 
        coalesce(perfuser.per_nombres,'')||coalesce(perfuser.per_apellidos,'') as nomapelfusercrea, fuser.us_cuenta,
        a.sus_fechaupd, a.sus_userupd 
        from tsuscripcion a 
        join tsuscripestado c on a.sus_estado = c.sue_id
        join tplan b on a.pln_id = b.pln_id
        left join tfuser fuser on a.sus_usercrea = fuser.us_id
        left join tpersona perfuser on fuser.per_id = perfuser.per_id 
        where a.sus_id = {0} 
        """.format(sus_id)

        tupla_desc = ('sus_id', 'pln_id', 'per_id', 'sus_estado', 'estado', 'sus_diacobro', 'sus_diasgracia',
                      'sus_periodicidad', 'sus_fechacrea', 'sus_observacion', 'sus_plantobsfact', 'pln_nombre',
                      'pln_estado', 'trn_codigo', 'sus_fechainiserv', 'sus_usercrea', 'nomapelfusercrea', 'us_cuenta',
                      'sus_fechaupd', 'sus_userupd')

        return self.first(sql, tupla_desc)

    def listar_suscripciones_byref(self, per_id):
        sql = """
        select a.sus_id, a.pln_id, a.per_id, a.sus_estado, c.sue_nombre as estado,  a.sus_diacobro, a.sus_diasgracia, a.sus_periodicidad,
        a.sus_fechacrea, a.sus_observacion, a.sus_plantobsfact, b.pln_nombre, b.pln_estado, b.trn_codigo
        from tsuscripcion a 
        join tsuscripestado c on a.sus_estado = c.sue_id
        join tplan b on a.pln_id = b.pln_id where a.per_id = {0} order by a.sus_fechacrea
        """.format(per_id)
        tupla_desc = (
            'sus_id', 'pln_id', 'per_id', 'sus_estado', 'estado', 'sus_diacobro', 'sus_diasgracia', 'sus_periodicidad',
            'sus_fechacrea', 'sus_observacion', 'sus_plantobsfact', 'pln_nombre', 'pln_estado', 'trn_codigo')
        return self.all(sql, tupla_desc)

    def is_ref_registertoplan(self, per_id, pln_id):
        sql = """
        select count(*) as cuenta from tsuscripcion where sus_estado !=2 and per_id = {0} and pln_id = {1}
        """.format(per_id, pln_id)

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form, user_crea):
        tsuscripcion = TSuscripcion()

        # Verificar si el referetente ya se encuentra suscrito a un plan especifico
        if self.is_ref_registertoplan(per_id=form['per_id'], pln_id=form['pln_id']):
            raise ErrorValidacionExc('El referente ya esta registrado al plan seleccionado')

        tsuscripcion.pln_id = form['pln_id']
        tsuscripcion.per_id = form['per_id']
        tsuscripcion.sus_estado = form['sus_estado']
        tsuscripcion.sus_diacobro = form['sus_diacobro']
        tsuscripcion.sus_diasgracia = form['sus_diasgracia']
        tsuscripcion.sus_periodicidad = form['sus_periodicidad']
        tsuscripcion.sus_observacion = form['sus_observacion']
        tsuscripcion.sus_plantobsfact = form['sus_plantobsfact']
        tsuscripcion.sus_fechacrea = datetime.datetime.now()
        if cadenas.es_nonulo_novacio(form['sus_fechainiserv']):
            tsuscripcion.sus_fechainiserv = fechas.parse_cadena(form['sus_fechainiserv'])

        tsuscripcion.sus_usercrea = user_crea

        self.dbsession.add(tsuscripcion)

    def find_by_id(self, sus_id):
        return self.dbsession.query(TSuscripcion).filter(TSuscripcion.sus_id == sus_id).first()

    def cambiar_estado(self, sus_id, nuevo_estado, user_upd):
        tsuscrip = self.find_by_id(sus_id)
        if tsuscrip is not None:
            if tsuscrip.sus_estado != nuevo_estado:
                tsuscrip.sus_estado = nuevo_estado
                tsuscrip.sus_fechaupd = datetime.datetime.now()
                tsuscrip.sus_userupd = user_upd
                self.dbsession.add(tsuscrip)

    def generar_factura(self, sus_id):

        detsuscrip = self.get_detalles_suscrip(sus_id)
        trn_codigo = detsuscrip['trn_codigo']


