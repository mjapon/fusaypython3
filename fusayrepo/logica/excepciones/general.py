# -*- coding:UTF-8 -*-
"""
Created on '04/03/2015'
@author: 'Manuel'
"""
import json
import logging

from pyramid.response import Response
from pyramid.view import view_config

from fusayrepo.utils.jsonutil import SEJsonEncoder

log = logging.getLogger(__name__)

DB_MESSAGE_PREFIX = '(psycopg2.errors'
DB_OPERATIONAL_PREFIX = '(psycopg2.OperationalError'
DB_CUSTOM_MESSAGE_PREFIX = '(psycopg2.DatabaseError'
GENERAL_ERROR_MESSAGE = 'Ha ocurrido un error'


def procesar_excepcion(exc, request):
    emp_codigo = 0
    try:
        if 'emp_codigo' in request.headers:
            emp_codigo = request.headers["emp_codigo"]
    except:
        log.error(u"Exception capturada, no pude recuperar el codigo de la empresa", exc_info=True)

    log.error(' Exception capturada: ', exc_info=True)
    log.error(' Empresa donde se genera el error es: {0} '.format(emp_codigo))

    exc_mgs = proccess_exception_message(exc)
    log.error("Mensaje retornado: ")
    log.error(exc_mgs)

    inputid = ""
    if 'inputid' in dir(exc):
        inputid = exc.inputid

    status_code = None
    if 'status_code' in dir(exc):
        status_code = exc.status_code
    if status_code is None:
        status_code = 400  # Bad request

    error_code = None
    if 'error_code' in dir(exc):
        error_code = exc.error_code
    if error_code is None:
        error_code = status_code

    ss_expirada = 0

    return {
        'msg': exc_mgs,
        'inputid': inputid,
        'status_code': status_code,
        'error_code': error_code,
        'ss_expirada': ss_expirada
    }


def add_status_to_response(response, exc_res):
    response.status_code = exc_res.get("status_code", 400)
    return response


def proccess_exception_message(exc):
    exc_msg = str(exc)
    if exc_msg is not None and (exc_msg.startswith(DB_MESSAGE_PREFIX) or exc_msg.startswith(DB_OPERATIONAL_PREFIX)):
        exc_msg = GENERAL_ERROR_MESSAGE
    elif exc_msg.startswith(DB_CUSTOM_MESSAGE_PREFIX):
        exc_msg = procesar_msg_postgres(exc_msg)

    return exc_msg


@view_config(context=Exception, renderer='excepcion/general.html')
def exc_general(exc, request):
    res = procesar_excepcion(exc, request)
    response = Response(json.dumps(res, cls=SEJsonEncoder))
    response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
    })
    return add_status_to_response(response, res)


def procesar_msg_postgres(msg):
    msgdb = msg
    pgflag = '(psycopg2.DatabaseError)'
    pgctxflag = 'CONTEXT:'

    idf = msg.find(pgflag)
    idc = msg.find(pgctxflag)

    if idf >= 0 and idc > 0:
        msgdb = 'DB:{0}'.format(msg[idf + len(pgflag):idc])

    return msgdb
