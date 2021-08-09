# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text, TIMESTAMP, Date

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdontograma(Declarative, JsonAlchemy):
    __tablename__ = 'todontograma'

    od_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    od_fechacrea = Column(TIMESTAMP)
    od_fechaupd = Column(TIMESTAMP)
    user_upd = Column(Integer)
    user_crea = Column(Integer)
    od_odontograma = Column(Text)
    od_obsodonto = Column(Text)
    pac_id = Column(Integer)
    od_tipo = Column(Integer)
    od_protesis = Column(Text)


class TOdontogramaHist(Declarative, JsonAlchemy):
    __tablename__ = 'todontograma_hist'

    odh_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    odh_fechacrea = Column(TIMESTAMP)
    odh_odontograma = Column(Text)
    odh_protesis = Column(Text)
    odh_tipo = Column(Integer, default=1, nullable=False)
    pac_id = Column(Integer, nullable=False)
    user_crea = Column(Integer, default=0, nullable=False)
    odh_fecha = Column(Date)
