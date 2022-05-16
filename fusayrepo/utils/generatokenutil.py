# coding: utf-8
"""
Fecha de creacion '16/02/16'
@autor: 'serviestudios'
"""
import datetime
import logging

import jwt

from fusayrepo.utils import numeros, fechas

log = logging.getLogger(__name__)


class GeneraTokenUtil(object):

    def get_token(self, clave='sosecret'):
        return jwt.encode({'some': 'payload'}, clave, algorithm='HS256')

    def gen_token(self, us_id, emp_codigo, emp_esquema, sec_id, clave="fusay4793", tdv_codigo=1):
        data = {'us_id': us_id, 'emp_codigo': emp_codigo, 'emp_esquema': emp_esquema,
                'sec_id': sec_id, 'tdv_codigo': tdv_codigo}
        encoded_jwt = jwt.encode(data, clave, algorithm='HS256')
        return encoded_jwt

    def gen_token_pixel(self, us_id, clave="fusay4793"):
        data = {'us_id': us_id, 'emp_codigo': 1, 'emp_esquema': 'fusay', 'sec_id': 1}
        encoded_jwt = jwt.encode(data, clave, algorithm='HS256')
        return encoded_jwt

    def update_secid_token(self, token, sec_id):
        datos_token = self.get_datos_fromtoken(token)
        return self.gen_token(datos_token['us_id'], datos_token['emp_codigo'],
                              datos_token['emp_esquema'], sec_id, clave="fusay4793",
                              tdv_codigo=datos_token['tdv_codigo'])

    def update_tdvcod_token(self, token, tdv_codigo):
        datos_token = self.get_datos_fromtoken(token)
        return self.gen_token(datos_token['us_id'], datos_token['emp_codigo'],
                              datos_token['emp_esquema'], datos_token['sec_id'], clave="fusay4793",
                              tdv_codigo=tdv_codigo)

    def get_datos_fromtoken(self, token, clave="fusay4793"):
        decoded_value = jwt.decode(token, clave, algorithms=['HS256'])
        return decoded_value


def get_fila(saldo_ini, cuota_mensual, tasa, fecha):
    interes = saldo_ini * tasa / 12
    roud_interes = numeros.roundm2(interes)
    capital = cuota_mensual - interes
    round_capital = numeros.roundm2(capital)
    saldo = saldo_ini - capital
    # round_saldo = numeros.roundm2(saldo)
    next_date = fechas.sumar_meses(fecha, 1)
    return {
        'capital': round_capital,
        'interes': roud_interes,
        'saldo': saldo,
        'nextdate': next_date
    }


if __name__ == '__main__':

    print("Se ejecuta main--->")
    feca = '05/04/2022'
    fecb = '02/04/2022'
    print(fechas.son_fechas_iguales(feca, fecb))