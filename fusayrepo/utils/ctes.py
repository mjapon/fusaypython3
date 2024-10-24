# -*- coding:UTF-8 -*-
"""
Created on '01/12/2014'
@author: 'Manuel'
"""
import logging

log = logging.getLogger(__name__)

IP_REDIS_SERVER = "localhost"
APP_FMT_FECHA = "%d/%m/%Y"
APP_FMT_FECHA_GMAIL = "%y/%m/%d"
APP_FMT_HORA = "%H:%M"
APP_FMT_FECHA_HORA = APP_FMT_FECHA + ' ' + APP_FMT_HORA
APP_FMT_FECHA_DB = "%Y-%m-%d"
MONEDA = "DOLAR"
MOTIVO_NC = u"DEVOLUCIÓN"
IVA = 0.12
NDECIMALESPRECIOS_VIEW = 4
NDECIMALESPRECIOS_DB = 6

LEN_DOC_TRANSACC = 15
LEN_DOC_SECUENCIA = 9

TRA_COD_CRED_VENTA = 11
TRA_COD_CRED_COMPRA = 10
TRA_COD_NOTA_CREDITO = 4
TRA_COD_FACT_VENTA = 1
TRA_COD_NOTAVENTA = 2
TRA_COD_FACT_COMPRA = 7
TRA_COD_ABO_VENTA = 8
TRA_COD_ABO_COMPRA = 9
TRA_COD_PLAN = 12
TRA_COD_ASI_CONTABLE = 13

DT_TIPO_ITEM_DETALLE = 1
DT_TIPO_ITEM_PAGO = 2
DT_TIPO_ITEM_IMPUESTO = 3
DT_TIPO_ITEM_DETASIENTO = 4

TRA_TIPO_VENTA = 1
TRA_TIPO_COMPRA = 2

TIPOITEM_PRODUCTO = 1
TIPOITEM_SERVICIO = 2
TIPOITEM_CNTACONTABLE = 3
TIPOITEM_RUBRO = 4

AUD_ASIENTO_ANULAR = 1
AUD_ASIENTO_ERRAR = 2
AUD_ASIENTO_EDITAR = 3
AUD_ASIENTO_ELIMINAR = 4

VERSION_APP = 1.4

# Contantes para las clase de cuentas contables
CLASECC_EFECTIVO = "E"
CLASECC_BANCOS = "B"
CLASECC_CTAXCOBRAR = "XC"
CLASECC_CTAXPAGAR = "XP"
CLASECC_SALDOINIBILL = "SI"

# MODO_LOGOUT_ISYPLUS2 = 1#1-DESARROLLO 2-PRODUCCION
MODO_LOGOUT_DESARROLLO = 1
MODO_LOGOUT_PRODUCCION = 2
APP_CONTABLE_URL = 'v2'
# APP_DOMINIO = 'localhost'
# APP_DOMINIO = '192.168.0.12'
# APP_DOMINIO = 'www.isyplus.com'

# MODULOS DE REPORTES
MODULOS_REPORTES_DICT = {1: 'CONTABILIDAD',
                         2: 'REFERENTES',
                         3: 'MODULO'}

# Nombre de los parametros para la creacion de asientos contables en depositos o retiros
CTA_CONTABLE_MOV_NC_DEBE = 'cj_cta_mov_nc_debe'
CTA_CONTABLE_MOV_NC_HABER = 'cj_cta_mov_nc_haber'
CTA_CONTABLE_MOV_ND_DEBE = 'cj_cta_mov_nd_debe'
CTA_CONTABLE_MOV_ND_HABER = 'cj_cta_mov_nd_haber'

PERMISO_APP_CONFIG = 'APP_CONFIG'
