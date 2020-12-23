# coding: utf-8
"""
Fecha de creacion 4/25/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, TIMESTAMP, Text, Date, Numeric, Boolean, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TCita(Declarative, JsonAlchemy):
    __tablename__ = 'tcita'

    ct_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ct_fecha = Column(Date, nullable=False)
    ct_hora = Column(Numeric(4, 2), nullable=False)
    ct_hora_fin = Column(Numeric(4, 2), nullable=False)
    pac_id = Column(Integer, nullable=False)
    ct_obs = Column(Text)
    med_id = Column(Integer, nullable=False)
    ct_serv = Column(Integer, nullable=False)
    ct_estado = Column(Integer, nullable=False, default=0)  # 0-pendiente,1-atendido,2-anulado
    user_crea = Column(Integer)
    ct_fechacrea = Column(TIMESTAMP)
    ct_td = Column(Boolean, nullable=False, default=False)
    ct_color = Column(String(50))
    ct_titulo = Column(String(80))
