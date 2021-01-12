# coding: utf-8
"""
Fecha de creacion 1/8/21
@autor: mjapon
"""
import logging

log = logging.getLogger(__name__)


def redondear(cantidad, ndec):
    return round(cantidad, ndec)
