# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsientoauth(Declarative, JsonAlchemy):
    __tablename__ = 'tasientoaut'

    aau_codigo = Column(Integer, nullable=False, primary_key=True)
    trn_codigo = Column(Integer, nullable=False)
    trn_autnum = Column(Text)
    trn_autele = Column(Integer)
    trn_numsol = Column(Integer)
    trn_numaprob = Column(Integer)
