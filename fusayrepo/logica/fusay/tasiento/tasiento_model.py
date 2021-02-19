# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Numeric, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsiento(Declarative, JsonAlchemy):
    __tablename__ = 'tasiento'
    trn_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    dia_codigo = Column(Integer, default=0, nullable=False)
    trn_fecreg = Column(Date, nullable=False)
    trn_compro = Column(String(15), nullable=False)
    trn_fecha = Column(DateTime, nullable=False)
    trn_valido = Column(Integer, default=0, nullable=False)
    trn_docpen = Column(String(1), default='F', nullable=False)
    trn_pagpen = Column(String(1), default='F', nullable=False)
    sec_codigo = Column(Integer, nullable=False)
    per_codigo = Column(Integer, nullable=False)
    tra_codigo = Column(Integer, nullable=False)
    us_id = Column(Integer, nullable=False)
    trn_observ = Column(Text)
    tdv_codigo = Column(Integer, nullable=False)
    fol_codigo = Column(Integer)
    trn_tipcom = Column(String(2))
    trn_suscom = Column(String(2))
    per_codres = Column(Integer)
    trn_impref = Column(Numeric(4, 2))


class TAsientoAud(Declarative, JsonAlchemy):
    __tablename__ = 'tasientoaud'
    aud_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    trn_codigo = Column(Integer, nullable=False)
    aud_accion = Column(Integer, nullable=False)  # 1: Anular, 2:Errar, 3:Editar, 4:Borrar
    aud_fecha = Column(TIMESTAMP, nullable=False)
    aud_user = Column(Integer, nullable=False)
    aud_obs = Column(Text)
