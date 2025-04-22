# coding: utf-8
"""
Fecha de creacion: 09/04/2025
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tmedicoconsulta.tmedicoconsulta_model import TMedicoConsulta

log = logging.getLogger(__name__)


class TMedicoConsultaDao(BaseDao):

    def crear_medico_consulta(self, cosm_id, med_id, usercrea):
        medicoconsulta = TMedicoConsulta()
        medicoconsulta.cosm_id = cosm_id
        medicoconsulta.med_id = med_id
        medicoconsulta.fecharegistro = datetime.datetime.now()
        medicoconsulta.usercrea = usercrea

        self.dbsession.add(medicoconsulta)
        self.dbsession.flush()

        return medicoconsulta.cosmed_id

    def obtener_medico_consulta(self, cosmed_id):
        return self.dbsession.query(TMedicoConsulta).filter(TMedicoConsulta.cosmed_id == cosmed_id).first()

    def get_medicos_consulta(self, cosmed_id):
        sql = f"select med_id from tmedicoconsulta where cosm_id = {cosmed_id}"
        tupla_desc = ('med_id',)
        return self.all(sql, tupla_desc)

    def actualizar_medico_consulta(self, cosmed_id, **kwargs):
        medicoconsulta = self.obtener_medico_consulta(cosmed_id)
        if medicoconsulta:
            for key, value in kwargs.items():
                setattr(medicoconsulta, key, value)
            self.dbsession.flush()
            return True
        return False

    def eliminar_medico_consulta(self, cosmed_id):
        medicoconsulta = self.obtener_medico_consulta(cosmed_id)
        if medicoconsulta:
            self.dbsession.delete(medicoconsulta)
            self.dbsession.flush()
            return True
        return False
