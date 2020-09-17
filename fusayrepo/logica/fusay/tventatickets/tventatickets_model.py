# coding: utf-8
"""
Fecha de creacion 9/14/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, TIMESTAMP, Numeric

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TVentaTickets(Declarative, JsonAlchemy):
    __tablename__ = 'tventatickets'

    vt_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    vt_fechareg = Column(TIMESTAMP, nullable=False)
    vt_monto = Column(Numeric(4,2), default=0.0, nullable=False)
    vt_tipo = Column(Integer, nullable=False)
    vt_estado = Column(Integer, nullable=False)#--0- borrador, 1- confirmado, 2- anulado
    vt_obs = Column(Text)
    vt_clase = Column(Integer, default=1)
    vt_fecha = Column(Date, nullable=False)