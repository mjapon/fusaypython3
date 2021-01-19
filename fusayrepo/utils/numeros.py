# coding: utf-8
"""
Fecha de creacion 1/8/21
@autor: mjapon
"""
import logging

log = logging.getLogger(__name__)


def roundm(cantidad, ndec):
    return round(cantidad, ndec)


def roundm2(valor):
    return roundm(valor, 2)


def roundm4(valor):
    return roundm(valor, 4)


def roundm6(valor):
    return roundm(valor, 6)


def get_valor_iva(valor, iva):
    return roundm6(valor * iva)
