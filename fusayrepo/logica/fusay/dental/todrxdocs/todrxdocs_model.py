# coding: utf-8
"""
Fecha de creacion 12/24/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Text, DateTime, SMALLINT

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdRxDocs(Declarative, JsonAlchemy):
    __tablename__ = 'todrxdocs'

    rxd_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    rxd_ruta = Column(String(500), nullable=False)
    rxd_ext = Column(String(80))
    rxd_nota = Column(Text)
    pac_id = Column(Integer, nullable=False)
    user_crea = Column(Integer, nullable=False)
    rxd_fechacrea = Column(DateTime, nullable=False)
    rxd_nropieza = Column(SMALLINT)
    rxd_tipo = Column(SMALLINT, nullable=False, default=1)
    rxd_estado = Column(SMALLINT, nullable=False, default=1)
    rxd_nombre = Column(String(100))
    rxd_filename = Column(String(100))
