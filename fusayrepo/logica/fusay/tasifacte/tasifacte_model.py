# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, String, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsiFacte(Declarative, JsonAlchemy):
    __tablename__ = 'tasifacte'

    tfe_codigo = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    trn_codigo = Column(Integer, nullable=False)
    tfe_claveacceso = Column(String(200), nullable=False)
    tfe_numautoriza = Column(String(200))
    tfe_estado = Column(Integer, default=0, nullable=False)
    tfe_fecautoriza = Column(String(80))
    tfe_ambiente = Column(Integer, default=0, nullable=False)
    tfe_mensajes = Column(Text)
    tfe_estadosri = Column(String(20))
