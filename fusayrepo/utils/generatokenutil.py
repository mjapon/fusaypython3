# coding: utf-8
"""
Fecha de creacion '16/02/16'
@autor: 'serviestudios'
"""
import logging

import jwt

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


if __name__ == '__main__':
    print("Se ejecuta main--->")

    from dateutil.relativedelta import *
    from datetime import date

    today = date.today()
    dob = date(1985, 1, 25)
    age = relativedelta(today, dob)
    print(age)
