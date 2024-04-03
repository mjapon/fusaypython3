# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from sqlalchemy import Column, Integer, DateTime, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFinSms(Declarative, JsonAlchemy):
    __tablename__ = 'tsms'

    sms_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    sms_status = Column(String(40), nullable=False)
    sms_error_code = Column(String(40))
    sms_error_message = Column(String(100))
    sms_phone = Column(String(15), nullable=False)
    sms_message = Column(String(500))
    sms_external_id = Column(String(50))
    sms_fecha_creacion = Column(DateTime, nullable=False, default=datetime.datetime.now())
