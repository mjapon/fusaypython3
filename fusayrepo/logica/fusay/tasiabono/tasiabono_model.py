# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsiAbono(Declarative, JsonAlchemy):
    __tablename__ = 'tasiabono'

    abo_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    dt_codigo = Column(Integer, nullable=False)
    dt_codcre = Column(Integer, nullable=False)


class TAsiAbonoProv(Declarative, JsonAlchemy):
    __tablename__ = 'tasiabo_provs'

    abop_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    cre_codigo = Column(Integer, nullable=False)
    abo_codigo = Column(Integer, nullable=False, default=0)
    abop_sales_from = Column(Integer, nullable=False)
    abop_sales_to = Column(Integer, nullable=False)
    abop_creation_date = Column(Integer, nullable=False)
    abop_update_date = Column(Integer, nullable=True)
    abop_user_create = Column(Integer, nullable=False)
    abop_user_update = Column(Integer, nullable=True)
    abop_status = Column(Integer, nullable=False, default=1)


class TAsiAbonoProvDetail(Declarative, JsonAlchemy):
    __tablename__ = 'tasiabo_provs_details'

    abpd_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    abop_codigo = Column(Integer, nullable=False)
    abpd_creation_date = Column(Integer, nullable=False)
    abpd_update_date = Column(Integer, nullable=True)
    abpd_user_create = Column(Integer, nullable=False)
    abpd_user_update = Column(Integer, nullable=True)
    abpd_status = Column(Integer, nullable=False, default=1)
    dt_codigo_venta = Column(Integer, nullable=False)
    