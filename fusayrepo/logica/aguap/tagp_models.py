# coding: utf-8
"""
Fecha de creacion 4/29/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Numeric, Boolean

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAgpContrato(Declarative, JsonAlchemy):
    __tablename__ = 'tagp_contrato'

    cna_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    per_id = Column(Integer, nullable=False)
    cna_fechacrea = Column(DateTime, nullable=False)
    cna_fechaini = Column(Date, nullable=False)
    cna_fechafin = Column(Date)
    cna_usercrea = Column(Integer, nullable=False)
    cna_estado = Column(Integer, default=1, nullable=False)
    cna_estadoserv = Column(Integer, default=1, nullable=False)
    cna_nmingas = Column(Integer)
    cna_barrio = Column(Integer, nullable=False, default=0)
    cna_sector = Column(String(80))
    cna_direccion = Column(String(100))
    cna_referencia = Column(String(80))
    cna_adjunto = Column(Integer)
    cna_teredad = Column(Boolean, default=False)
    cna_costoinst = Column(Numeric, default=0.0)
    trn_codigo = Column(Integer, nullable=False, default=0)
    cna_tarifa = Column(Integer, default=0, nullable=False)
    cna_discapacidad = Column(Boolean, default=False)
    # cna_fechaupd = Column(DateTime, nullable=False)


class TAgpMedidor(Declarative, JsonAlchemy):
    __tablename__ = 'tagp_medidor'

    mdg_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    cna_id = Column(Integer, nullable=False)
    mdg_num = Column(String(50), nullable=False, unique=True)
    mdg_fechacrea = Column(DateTime, nullable=False)
    mdg_usercrea = Column(Integer, nullable=False)
    mdg_estado = Column(Integer, default=1, nullable=False)
    mdg_estadofis = Column(Integer, default=1, nullable=False)
    mdg_obs = Column(Text)


class TAgpLectoMed(Declarative, JsonAlchemy):
    __tablename__ = 'tagp_lectomed'

    lmd_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    mdg_id = Column(Integer, nullable=False)
    lmd_mes = Column(Integer, nullable=False)
    lmd_valor = Column(Numeric(10, 2), default=0.0, nullable=False)
    lmd_userlee = Column(Integer)
    lmd_fechacrea = Column(DateTime, nullable=False)
    lmd_usercrea = Column(Integer, nullable=False)
    lmd_obs = Column(Text)
    lmd_estado = Column(Integer, default=1, nullable=False)
    lmd_foto = Column(Integer)
    lmd_useranula = Column(Integer)
    lmd_fechanula = Column(DateTime)
    lmd_consumo = Column(Numeric(10, 2), default=0.0)
    lmd_valorant = Column(Numeric(10, 2), default=0.0)
    lmd_desde = Column(Date, nullable=False)
    lmd_hasta = Column(Date, nullable=False)
    lmd_anio = Column(Integer, nullable=False)


class TagpPago(Declarative, JsonAlchemy):
    __tablename__ = 'tagp_pago'

    pg_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    lmd_id = Column(Integer, nullable=False)
    pg_estado = Column(Integer, default=0, nullable=False)
    pg_usercrea = Column(Integer, default=0, nullable=False)
    pg_fechacrea = Column(DateTime, nullable=False)
    trn_codigo = Column(Integer, nullable=False, default=0)
    pg_json = Column(Text)


class TagpPagosMavil(Declarative, JsonAlchemy):
    __tablename__ = 'tagp_pagosmavil'
    pgm_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pgm_anio = Column(Integer, nullable=False)
    pgm_mes = Column(Integer, nullable=False)
    pgm_fechacrea = Column(DateTime, nullable=False)
    pgm_usercrea = Column(Integer, nullable=False)
    pgm_total = Column(Numeric(12, 4), default=0.0, nullable=False)
    pgm_estado = Column(Integer, nullable=False, default=0)
    pgm_obs = Column(Text)
