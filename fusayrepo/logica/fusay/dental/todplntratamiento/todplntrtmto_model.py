# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, DATETIME

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdPlnTrtmto(Declarative, JsonAlchemy):
    __tablename__ = 'todplntrtmto'

    pnt_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pnt_nombre = Column(String(50), nullable=False)
    pnt_fechacrea = Column(DateTime, nullable=False, default=datetime.now())
    user_crea = Column(Integer, nullable=False)
    pnt_estado = Column(Integer, default=0)
    med_id = Column(Integer, nullable=False)
    pac_id = Column(Integer, nullable=False)
    trn_codigo = Column(Integer)
    pnt_obs = Column(Text)
    user_upd = Column(Integer)
    fecha_upd = Column(DATETIME)
