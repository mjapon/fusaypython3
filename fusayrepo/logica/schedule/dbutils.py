# coding: utf-8
"""
Fecha de creacion 18/06/2024
@autor: Manuel Japon
"""
from sqlalchemy.orm import sessionmaker

URL_DB = "postgresql://postgres:postgres@localhost:5432/imprentadb"


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory
