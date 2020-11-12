# coding: utf-8
"""
Fecha de creacion 11/12/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)

class TPixelUserDao(BaseDao):

    def autenticar(self, us_cuenta, us_clave):
        sql = """
        select count(*) as cuenta from tpxuser where pxus_cuenta = '{0}' and pxus_clave = '{1}'  
        """.format(us_cuenta, us_clave)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def get_user(self, us_cuenta):
        sql = """select a.pxus_id,        
        a.pxus_cuenta,
        a.pxus_nombre,
        a.pxus_email,
        a.pxus_fechacrea,
        a.pxus_estado
        from tpxuser a where pxus_cuenta = '{0}'""".format(us_cuenta)

        tupla_desc = ('pxus_id','pxus_cuenta','pxus_nombre','pxus_email','pxus_fechacrea','pxus_estado')

        datos_user = self.first(sql=sql, tupla_desc=tupla_desc)
        return datos_user