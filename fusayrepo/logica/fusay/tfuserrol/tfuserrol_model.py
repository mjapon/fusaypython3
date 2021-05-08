# coding: utf-8
"""
Fecha de creacion 10/11/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, DateTime

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFuserRol(Declarative, JsonAlchemy):
    __tablename__ = 'tfuserrol'

    usrl_id = Column(Integer, primary_key=True, nullable=False)
    us_id = Column(Integer, nullable=False)
    rl_id = Column(Integer, nullable=False)
    usrl_fechacrea = Column(DateTime)
