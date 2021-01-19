# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsiAbono(Declarative, JsonAlchemy):
    __tablename__ = 'tasiabono'

    abo_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    dt_codigo = Column(Integer, nullable=False)
    dt_codcre = Column(Integer, nullable=False)
