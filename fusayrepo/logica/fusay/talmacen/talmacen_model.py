# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, BOOLEAN

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAlmacen(Declarative, JsonAlchemy):
    __tablename__ = 'talmacen'

    alm_codigo = Column(Integer, nullable=False, primary_key=True)
    alm_numest = Column(String(3), default='001', nullable=False)
    alm_razsoc = Column(String(70), nullable=False)
    alm_descri = Column(String(80))
    alm_direcc = Column(String(80))
    alm_repleg = Column(String(80))
    alm_email = Column(String(70))
    alm_websit = Column(String(70))
    alm_fono1 = Column(String(50))
    alm_fono2 = Column(String(50))
    alm_movil = Column(String(50))
    alm_ruc = Column(String(50))
    alm_ciudad = Column(Integer)
    alm_sector = Column(String(50))
    alm_fecreg = Column(DateTime, nullable=False)
    alm_seccion = Column(Integer, nullable=False)
    cnt_codigo = Column(Integer, default=0)
    alm_matriz = Column(Integer, default=0)
    alm_tipoamb = Column(Integer, default=0)
    alm_contab = Column(BOOLEAN, default=False)
