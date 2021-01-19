# coding: utf-8
"""
Fecha de creacion 1/17/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TItemConfigSec(Declarative, JsonAlchemy):
    __tablename__ = 'titemconfig_sec'

    ics_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ic_id = Column(Integer, nullable=False)
    sec_id = Column(Integer, nullable=False)
