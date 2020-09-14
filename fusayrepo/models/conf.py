# -*- coding:UTF-8 -*-
"""
Created on '01/12/2014'
@author: 'Manuel'
"""
import logging
from sqlalchemy.ext.declarative.api import as_declarative

log = logging.getLogger(__name__)

ENGINE_DBCOMUN_DIC = {}

@as_declarative()
class Declarative(object):
    pass