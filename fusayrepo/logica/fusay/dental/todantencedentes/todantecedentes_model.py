# coding: utf-8
"""
Fecha de creacion 12/8/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, SMALLINT, TIMESTAMP, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdAntecedentes(Declarative, JsonAlchemy):
    __tablename__ = 'todantecedentes'

    od_antid = Column(Integer, nullable=False, primary_key=True)
    od_antfechacrea = Column(TIMESTAMP, nullable=False)
    od_antusercrea = Column(Integer, nullable=False)
    od_tipo = Column(SMALLINT, default=1)
    pac_id = Column(Integer, nullable=False)
    od_antestado = Column(SMALLINT, default=1)  # 1:valido, 2:anulado
    od_fechanula = Column(TIMESTAMP)
    od_useranula = Column(Integer)
    od_hallazgoexamfis = Column(Text)
