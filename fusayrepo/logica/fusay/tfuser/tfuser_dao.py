# coding: utf-8
"""
Fecha de creacion 02/01/2020
@autor: mejg231019
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuser.tfuser_model import TFuser
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao

log = logging.getLogger(__name__)


class TFuserDao(BaseDao):

    def find_byid(self, us_id):
        return self.dbsession.query(TFuser).filter(TFuser.us_id == us_id).first()

    def autenticar(self, us_cuenta, us_clave):
        sql = """
        select count(*) as cuenta from tfuser where us_cuenta = '{0}' and us_clave = '{1}'  
        """.format(us_cuenta, us_clave)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def get_user(self, us_cuenta):
        sql = """select a.us_id,
        a.per_id,
        a.us_cuenta,
        a.us_fechacrea,
        a.us_estado,
        b.per_ciruc,
        b.per_nombres,
        b.per_apellidos,
        b.per_direccion,
        b.per_telf,
        b.per_movil,
        b.per_email,
        b.per_tipo,
        b.per_lugnac from tfuser a
        join tpersona b on a.per_id = b.per_id           
         where us_cuenta = '{0}'""".format(us_cuenta)

        tupla_desc = ('us_id', 'per_id', 'us_cuenta', 'us_fechacrea', 'us_estado',
                      'per_ciruc', 'per_nombres', 'per_apellidos', 'per_direccion', 'per_telf',
                      'per_movil', 'per_email', 'per_tipo', 'per_lugnac')

        datos_user = self.first(sql=sql, tupla_desc=tupla_desc)
        return datos_user

    def listar(self):
        sql = """
            select a.us_id, a.us_cuenta, a.us_clave, p.per_ciruc, coalesce(p.per_nombres,'')||' '||coalesce(p.per_apellidos,'') as nomapel,
            case when a.us_estado = 0 then 'ACTIVO' else 'INACTIVO' end as estado            
            from tfuser a join tpersona p on a.per_id = p.per_id order by 5 asc 
        """
        tupla_desc = ('us_id', 'us_cuenta', 'us_clave', 'per_ciruc', 'nomapel', 'estado')

        return self.all(sql, tupla_desc)

    def listargrid(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='usuarios')
        return data
