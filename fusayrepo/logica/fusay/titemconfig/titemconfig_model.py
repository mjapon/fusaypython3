# coding: utf-8
"""
Fecha de creacion 2/15/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, TIMESTAMP, Text, Boolean, String
from sqlalchemy.sql.functions import current_date

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TItemConfig(Declarative, JsonAlchemy):
    __tablename__ = 'titemconfig'

    ic_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ic_nombre = Column(Text, nullable=False)
    ic_code = Column(Text, unique=True)
    ic_padre = Column(Integer)
    tipic_id = Column(Integer, default=1, nullable=False)
    ic_estado = Column(Integer, default=1, nullable=False)
    ic_nota = Column(Text)
    catic_id = Column(Integer, default=1, nullable=False)
    clsic_id = Column(Integer)
    ic_fechacrea = Column(TIMESTAMP, nullable=False, default=current_date)
    ic_usercrea = Column(Integer)
    ic_useractualiza = Column(Integer)
    ic_fechaactualiza = Column(TIMESTAMP)
    ic_dental = Column(Boolean, default=False)
    ic_clasecc = Column(String(2))
    ic_alias = Column(String(80))
    ic_haschild = Column(Boolean, default=False, nullable=False)
