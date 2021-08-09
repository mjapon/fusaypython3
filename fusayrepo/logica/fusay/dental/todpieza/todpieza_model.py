# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""

import logging

from sqlalchemy import Column, Integer, DateTime, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdObspieza(Declarative, JsonAlchemy):
    __tablename__ = 'todobspieza'

    odo_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    odo_numpieza = Column(Integer, nullable=False)
    odo_fechacrea = Column(DateTime, nullable=False)
    user_crea = Column(Integer, nullable=False)
    odo_obs = Column(Text, nullable=False)
    pac_id = Column(Integer, nullable=False)


class TOdTratamientoPieza(Declarative, JsonAlchemy):
    __tablename__ = 'todtratamientopieza'

    odt_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    odt_numpieza = Column(Integer, nullable=False)
    odt_fechainitrata = Column(DateTime)
    odt_fechafintrata = Column(DateTime)
    odt_fecharegtrataext = Column(DateTime)
    pac_id = Column(Integer, nullable=False)
