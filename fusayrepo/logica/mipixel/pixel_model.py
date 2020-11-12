# coding: utf-8
"""
Fecha de creacion 10/27/20
@autor: mjapon
"""
import logging
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class MiPixelModel(Declarative, JsonAlchemy):
    __tablename__ = 'tpixel'

    px_id = Column(Integer, nullable=False, primary_key=True)
    px_email = Column(String(80), nullable=False)
    px_fecharegistro = Column(DateTime, nullable=False)
    px_row = Column(Integer, nullable=False)
    px_col = Column(Integer, nullable=False)
    px_row_end = Column(Integer, nullable=False)
    px_col_end = Column(Integer, nullable=False)
    px_costo = Column(Numeric(10, 3))
    px_pathlogo = Column(String(200))
    px_estado = Column(Integer, default=0, nullable=False)
    px_tipo = Column(String(100))
    px_url = Column(String(1000))
    px_fechanula = Column(DateTime)
    px_obsanula = Column(Text)
    px_fechaconfirma = Column(DateTime)
    px_obsconfirma = Column(Text)
    px_numpx = Column(Integer)
    px_texto = Column(String(50))

