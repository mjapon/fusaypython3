# coding: utf-8
"""
Fecha de creacion 12/8/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdAntecedentesVal(Declarative, JsonAlchemy):
    __tablename__ = 'todantecedentesval'

    od_antvid = Column(Integer, nullable=False, primary_key=True)
    od_antid = Column(Integer, nullable=False)
    cmtv_id = Column(Integer, nullable=False)
    od_antvval = Column(Text)
