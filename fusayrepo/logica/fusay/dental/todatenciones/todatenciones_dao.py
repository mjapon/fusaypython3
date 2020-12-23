# coding: utf-8
"""
Fecha de creacion 12/9/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todatenciones.todatenciones_model import TOdAtenciones
from fusayrepo.logica.fusay.dental.todontograma.todontograma_dao import TOdontogramaDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao

log = logging.getLogger(__name__)


class TOdAtencionesDao(BaseDao):

    def get_form(self, pac_id):
        return {
            'ate_id': 0,
            'pac_id': pac_id,
            'med_id': 0,
            'ate_diagnostico': '',
            'ate_procedimiento': '',
            'ate_estado': 1,
            'cta_id': 0,
            'pnt_id': 0
        }

    def get_next_nroat(self, pac_id):
        sql = "select max(ate_nro)+1 as ate_nro  from todatenciones where pac_id = {0} and ate_estado = 1".format(
            pac_id)
        ate_nro = self.first_col(sql, 'ate_nro')
        if ate_nro is not None:
            return ate_nro
        return 1

    def crear(self, form, user_crea):
        # todo: Se debe cambiar par que se muestre el médido que esta atendiendo
        form['med_id'] = user_crea

        pac_id = int(form['pac_id'])

        todatencion = TOdAtenciones()
        todatencion.user_crea = user_crea
        todatencion.ate_fechacrea = datetime.datetime.now()
        todatencion.med_id = int(form['med_id'])
        todatencion.pac_id = pac_id
        todatencion.ate_diagnostico = form['ate_diagnostico']
        todatencion.ate_procedimiento = form['ate_procedimiento']
        todatencion.ate_estado = 1

        if int(form['cta_id']) > 0:
            todatencion.cta_id = form['cta_id']

        if int(form['pnt_id']) > 0:
            todatencion.pnt_id = form['pnt_id']

        todatencion.ate_nro = self.get_next_nroat(pac_id=form['pac_id'])

        odontograma_dao = TOdontogramaDao(self.dbsession)
        lastod = odontograma_dao.get_last_odontograma(pac_id)
        if lastod is not None:
            if 1 in lastod.keys():
                todatencion.ate_odontograma = lastod[1]
            if 2 in lastod.keys():
                todatencion.ate_odontograma_sm = lastod[2]

        self.dbsession.add(todatencion)

    def find_byid(self, ate_id):
        return self.dbsession.query(TOdAtenciones).filter(TOdAtenciones.ate_id == ate_id).first()

    def get_detalles(self, ate_id):
        sql = """
        select a.ate_id, a.ate_fechacrea, a.user_crea, a.med_id, a.ate_diagnostico, a.ate_procedimiento, a.cta_id, 
        a.pnt_id, a.ate_nro, a.ate_odontograma, a.ate_odontograma_sm,
        a.pac_id from todatenciones a where a.ate_id = {0}""".format(ate_id)

        tupla_desc = (
            'ate_id', 'ate_fechacrea', 'user_crea', 'med_id', 'ate_diagnostico', 'ate_procedimiento', 'cta_id',
            'pnt_id', 'ate_nro', 'ate_odontograma', 'ate_odontograma_sm', 'pac_id')
        res = self.first(sql, tupla_desc)
        if res is not None:
            personadao = TPersonaDao(self.dbsession)
            respac = personadao.buscar_porperid_full(per_id=str(res['pac_id']))
            if respac is not None:
                for key in respac.keys():
                    res[key] = respac[key]

        return res

    def listar(self, pac_id):
        sql = """
        select a.ate_id, a.ate_fechacrea, a.user_crea, a.med_id, a.ate_diagnostico, a.ate_procedimiento, a.cta_id, 
        a.pnt_id, a.ate_nro from todatenciones a          
        where a.pac_id = {0} and a.ate_estado = 1 order by a.ate_nro asc
        """.format(pac_id)

        tupla_desc = (
            'ate_id', 'ate_fechacrea', 'user_crea', 'med_id', 'ate_diagnostico', 'ate_procedimiento', 'cta_id',
            'pnt_id',
            'ate_nro')
        return self.all(sql, tupla_desc)

    def anular(self, ate_id, user_anula):
        odatencion = self.find_byid(ate_id)
        if odatencion is not None:
            odatencion.ate_estado = 2
            odatencion.user_anula = user_anula
            odatencion.ate_fechanula = datetime.datetime.now()
