# coding: utf-8
"""
Fecha de creacion 5/23/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, DateTime, Text, Date, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TConsultaMedica(Declarative, JsonAlchemy):
    __tablename__ = 'tconsultamedica'

    cosm_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    pac_id = Column(Integer)
    med_id = Column(Integer)
    cosm_fechacita = Column(DateTime, nullable=False)
    cosm_fechacrea = Column(DateTime, nullable=False)
    cosm_motivo = Column(Text)
    cosm_enfermactual = Column(Text)
    cosm_hallazgoexamfis = Column(Text)
    cosm_exmscompl = Column(Text)
    cosm_tratamiento = Column(Text)
    cosm_receta = Column(Text)
    cosm_indicsreceta = Column(Text)
    cosm_recomendaciones = Column(Text)
    cosm_diagnostico = Column(Integer)
    user_crea = Column(Integer)
    cosm_diagnosticoal = Column(Text)
    cosm_fechaproxcita = Column(Date)
    cosm_diagnosticos = Column(String(50))
    cosm_tipo = Column(Integer, default=1)#1-medica, 2-odontologica
    cosm_estado = Column(Integer, default=1)#1-valido, 2-anulado


class TConsultaMedicaValores(Declarative, JsonAlchemy):
    __tablename__ = 'tconsultam_valores'

    cosm_id = Column(Integer, nullable=False)
    valcm_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    valcm_tipo = Column(Integer, nullable=False)
    valcm_valor = Column(Text, nullable=False)
    valcm_categ = Column(Integer, nullable=False)
