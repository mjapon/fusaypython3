# coding: utf-8
"""
Fecha de creacion 3/5/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, TIMESTAMP, Text, Numeric, Date

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTicket(Declarative, JsonAlchemy):
    __tablename__ = 'ttickets'

    tk_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    tk_nro = Column(Integer, nullable=False)
    tk_fechahora = Column(TIMESTAMP, nullable=False)
    tk_perid = Column(Integer, nullable=False)
    tk_observacion = Column(Text)
    tk_usercrea = Column(Text, nullable=False)
    tk_costo = Column(Numeric(4, 2), default=0.0, nullable=False)
    tk_dia = Column(Date)
    tk_estado = Column(Integer, default=1, nullable=False)
    tk_servicios = Column(Text)
    sec_id = Column(Integer)
