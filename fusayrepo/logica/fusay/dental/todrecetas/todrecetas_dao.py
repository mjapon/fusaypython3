# coding: utf-8
"""
Fecha de creacion 12/23/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.dental.todrecetas.todrecetas_model import TOdReceta
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TOdRecetasDao(BaseDao):

    def get_form(self):
        return {
            'rec_id': 0,
            'rec_recomdciones': '',
            'rec_indicaciones': '',
            'rec_receta': '',
            'med_id': 0,
            'pac_id': 0,
            'rec_estado': 1
        }

    def validar_form(self, form):
        if (not cadenas.es_nonulo_novacio(form['rec_receta'])):
            raise ErrorValidacionExc('Debe ingresar la receta')
        elif (not cadenas.es_nonulo_novacio(form['rec_indicaciones'])):
            raise ErrorValidacionExc('Debe ingresar las indicaciones')
        elif (not cadenas.es_nonulo_novacio(form['pac_id'])):
            raise ErrorValidacionExc('Debe especificar el paciente al cual está dirigido la receta')

    def crear(self, form, user_crea):
        self.validar_form(form)
        todreceta = TOdReceta()
        todreceta.rec_fechacrea = datetime.now()
        todreceta.user_crea = user_crea
        todreceta.rec_recomdciones = cadenas.strip(form['rec_recomdciones'])
        todreceta.rec_indicaciones = cadenas.strip(form['rec_indicaciones'])
        todreceta.rec_receta = cadenas.strip(form['rec_receta'])
        todreceta.med_id = form['med_id']
        todreceta.pac_id = form['pac_id']
        todreceta.rec_estado = form['rec_estado']

        self.dbsession.add(todreceta)
        self.dbsession.flush()

        return todreceta.rec_id

    def listar_validos(self, pac_id):
        sql = """
        select rec_id, rec_fechacrea, user_crea, rec_recomdciones, rec_indicaciones, rec_receta, pac_id, med_id, 
        rec_estado from todrecetas where pac_id = {0} and rec_estado = 1 order by rec_fechacrea desc
        """.format(pac_id)

        tupla_desc = (
            'rec_id', 'rec_fechacrea', 'user_crea', 'rec_recomdciones', 'rec_indicaciones', 'rec_receta', 'pac_id',
            'med_id', 'rec_estado')

        return self.all(sql, tupla_desc)

    def find_by_id(self, rec_id):
        return self.dbsession.query(TOdReceta).filter(TOdReceta.rec_id == rec_id).first()

    def editar(self, rec_id, form, user_edita):
        self.validar_form(form)
        todreceta = self.find_by_id(rec_id)
        if todreceta is not None:
            todreceta.rec_receta = cadenas.strip(form['rec_receta'])
            todreceta.rec_indicaciones = cadenas.strip(form['rec_indicaciones'])
            todreceta.rec_recomdciones = cadenas.strip(form['rec_recomdciones'])
            todreceta.rec_fechaedit = datetime.now()
            todreceta.user_edita = user_edita
            self.dbsession.add(todreceta)

    def anular(self, rec_id, user_anula):
        todreceta = self.find_by_id(rec_id)
        if todreceta is not None:
            todreceta.rec_estado = 2
            todreceta.rec_fechaedit = datetime.now()
            todreceta.user_edita = user_anula
