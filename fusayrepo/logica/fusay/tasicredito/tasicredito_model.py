# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsicredito(Declarative, JsonAlchemy):
    __tablename__ = 'tasicredito'

    cre_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    dt_codigo = Column(Integer, nullable=False)
    cre_fecini = Column(Date, nullable=False)
    cre_fecven = Column(Date)
    cre_intere = Column(Numeric(4, 2), default=0.0)
    cre_intmor = Column(Numeric(4, 2), default=0.0)
    cre_compro = Column(String(15), nullable=False)
    cre_codban = Column(Integer)
    cre_saldopen = Column(Numeric(15, 4), default=0.0)
    cre_tipo = Column(Integer, default=1, nullable=False)


class TAsicredProvs(Declarative, JsonAlchemy):
    """
    Mapeo de la tabla tasicred_provs
    Almacena información de proveedores relacionados con créditos
    """
    __tablename__ = 'tasicred_provs'

    crpr_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    cre_codigo = Column(Integer, ForeignKey('tasicredito.cre_codigo'), nullable=False, unique=True)
    crpr_sales_from = Column(Date, nullable=False)
    crpr_sales_to = Column(Date, nullable=False)
    crpr_creation_date = Column(DateTime, nullable=False)
    crpr_update_date = Column(DateTime)
    crpr_user_create = Column(Integer, nullable=False)
    crpr_user_update = Column(Integer)
    crpr_status = Column(Integer, default=1, nullable=False)


class TAsicredProvsDetails(Declarative, JsonAlchemy):
    """
    Mapeo de la tabla tasicred_provs_details
    Almacena detalles de artículos y montos para cada proveedor de crédito
    """
    __tablename__ = 'tasicred_provs_details'

    crpd_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    crpr_codigo = Column(Integer, ForeignKey('tasicred_provs.crpr_codigo'), nullable=False)
    dt_codigo = Column(Integer, ForeignKey('tasidetalle.dt_codigo'), nullable=False)
    crp_creation_date = Column(DateTime, nullable=False)
    crp_update_date = Column(DateTime)
    crp_user_create = Column(Integer, nullable=False)
    crp_user_update = Column(Integer)
    crp_status = Column(Integer, default=1, nullable=False)
