# coding: utf-8
"""
Fecha de creacion 12/23/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdReceta(Declarative, JsonAlchemy):
    __tablename__ = 'todrecetas'

    rec_id = Column(Integer, nullable=False, primary_key=True)
    rec_fechacrea = Column(TIMESTAMP, nullable=False)
    user_crea = Column(Integer, nullable=False)
    rec_fechaedit = Column(TIMESTAMP)
    user_edita = Column(Integer)
    rec_recomdciones = Column(Text)
    rec_indicaciones = Column(Text)
    rec_receta = Column(Text, nullable=False)
    pac_id = Column(Integer, nullable=False)
    med_id = Column(Integer, nullable=False)
    rec_estado = Column(Integer, default=1, nullable=False)
