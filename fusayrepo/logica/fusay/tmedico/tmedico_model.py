# coding: utf-8
"""
Fecha de creacion 9/11/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, DateTime

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TMedico(Declarative, JsonAlchemy):
    __tablename__ = 'tmedico'

    med_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    per_id = Column(Integer, nullable=False)
    med_fecreg = Column(DateTime)


class TMedicoEspe(Declarative, JsonAlchemy):
    __tablename__ = 'tmedicoespe'

    medesp_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    med_id = Column(Integer, nullable=False)
    esp_id = Column(Integer, nullable=False)
    medesp_estado = Column(Integer, nullable=False, default=0)