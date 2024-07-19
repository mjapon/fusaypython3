# coding: utf-8

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy


class TUserEmail(Declarative, JsonAlchemy):
    __tablename__ = 'tuseremail'
    ue_id = Column(Integer, nullable=False, primary_key=True)
    ue_email = Column(String(50), nullable=False)
    ue_emplist = Column(String(50), nullable=False)
    ue_create_date = Column(DateTime, nullable=False)
    ue_status = Column(Boolean, nullable=False)
    ue_usercreate = Column(Integer, nullable=False)
    ue_update_date = Column(DateTime)
    ue_userupdate = Column(Integer)
    ue_password = Column(String(100), nullable=False)
    ue_passtemp = Column(Boolean, nullable=False)
