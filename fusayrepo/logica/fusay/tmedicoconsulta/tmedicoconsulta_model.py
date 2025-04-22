# coding: utf-8
"""
Fecha de creacion: 09/04/2025
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, DateTime

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)

class TMedicoConsulta(Declarative, JsonAlchemy):
    __tablename__ = 'tmedicoconsulta'

    cosmed_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    cosm_id = Column(Integer, nullable=False)
    med_id = Column(Integer, nullable=False)
    fecharegistro = Column(DateTime, nullable=False)
    usercrea = Column(Integer, nullable=False)
