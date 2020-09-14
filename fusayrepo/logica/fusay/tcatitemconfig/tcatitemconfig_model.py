# coding: utf-8
"""
Fecha de creacion 2/17/20
@autor: mjapon
"""
import logging

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)
from sqlalchemy import Column, Integer, String


class TCatItemConfig(Declarative, JsonAlchemy):
    __tablename__ = 'tcatitemconfig'

    catic_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    catic_nombre = Column(String(60), nullable=False)
    catic_estado = Column(Integer, default=1, nullable=False)
