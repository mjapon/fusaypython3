# coding: utf-8
"""
Fecha de creacion 10/26/19
@autor: mjapon
"""
import logging

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DATETIME


class TFusayEvent(Declarative, JsonAlchemy):
    __tablename__ = 'tevents'

    ev_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ev_fecha = Column(Date, nullable=False)
    ev_fechacrea = Column(DATETIME, nullable=False)
    ev_creadopor = Column(Integer)
    ev_lugar = Column(Integer)
    ev_horainicio = Column(Text)
    ev_horafin = Column(Text)
    ev_nota = Column(Text)
    ev_publicidad = Column(Text)
    ev_tipo = Column(Integer, nullable=False)  # 1:Cer, 2:Bañ, 3:Limp con med, 4:Limp ca, 5:Danza, 6: Temazcal
    ev_precionormal = Column(Numeric(15, 4), default=0.0)
    ev_precioespecial = Column(Numeric(15, 4), default=0.0)
    ev_img = Column(Text)
    ev_estado = Column(Integer)
    ev_url = Column(String(40))
