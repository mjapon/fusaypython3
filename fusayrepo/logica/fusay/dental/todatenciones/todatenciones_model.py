# coding: utf-8
"""
Fecha de creacion 12/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, SMALLINT, TIMESTAMP, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TOdAtenciones(Declarative, JsonAlchemy):
    __tablename__ = 'todatenciones'

    ate_id = Column(Integer, nullable=False, primary_key=True)
    ate_fechacrea = Column(TIMESTAMP, nullable=False)
    user_crea = Column(Integer, nullable=False)
    pac_id = Column(Integer, nullable=False)
    med_id = Column(Integer, nullable=False)
    ate_diagnostico = Column(Text)
    ate_procedimiento = Column(Text)
    ate_estado = Column(SMALLINT, nullable=False, default=1)
    cta_id = Column(Integer)  # cita asociada
    pnt_id = Column(Integer)  # plan de tratamiento asociado
    ate_nro = Column(Integer, default=1, nullable=False)

    ate_fechanula = Column(TIMESTAMP)
    user_anula = Column(Integer)
    ate_obsanula = Column(Text)

    ate_odontograma = Column(Text)
    ate_odontograma_sm = Column(Text)
