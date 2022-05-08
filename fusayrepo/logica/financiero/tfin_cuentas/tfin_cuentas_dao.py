# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tfin_cuentas.tfin_cuentas_model import TFinCuentas

log = logging.getLogger(__name__)


class TFinCuentasDao(BaseDao):

    def has_cuenta(self, per_id, tipo):
        sql = """
        select count(*) as cuenta from tfin_cuentas where per_id = {0} and tc_id = {1} and 
        cue_estado <=3 
        """.format(per_id, tipo)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def get_datos_cuenta_by_num(self, cue_id):
        sql = """
        
        select cue_id,
                cue.per_id,
                cue.tc_id,
                cue_fecha_apertura,
                cue_estado,
                cue_nombre,
                cue_num_libreta,
                cue_fecha_cierre,
                cue_saldo_total,
                cue_saldo_bloq,
                cue_saldo_disp,
                user_crea,
                user_cierre,
                per.per_nombres,
                per.per_apellidos,
                per.per_nombres||' '||per.per_apellidos as per_nomapel,
                per.per_ciruc,
                per.per_direccion,
                per.per_telf,
                per.per_movil,
                per.per_email,
                tipc.tc_nombre	
                from tfin_cuentas cue
                join tpersona per on cue.per_id = per.per_id
                join tfin_tiposcuenta tipc on cue.tc_id = tipc.tc_id
                where cue_id = {0} 
        """.format(cue_id)
        tupla_desc = (
            'cue_id',
            'per_id',
            'tc_id',
            'cue_fecha_apertura',
            'cue_estado',
            'cue_nombre',
            'cue_num_libreta',
            'cue_fecha_cierre',
            'cue_saldo_total',
            'cue_saldo_bloq',
            'cue_saldo_disp',
            'user_crea',
            'user_cierre', 'per_nombres',
            'per_apellidos',
            'per_nomapel',
            'per_ciruc',
            'per_direccion',
            'per_telf',
            'per_movil',
            'per_email',
            'tc_nombre'
        )
        return self.first(sql, tupla_desc)

    def get_datos_cuenta(self, per_id, tc_id):
        sql = """
        select cue_id,
                per_id,
                tc_id,
                cue_fecha_apertura,
                cue_estado,
                cue_nombre,
                cue_num_libreta,
                cue_fecha_cierre,
                cue_saldo_total,
                cue_saldo_bloq,
                cue_saldo_disp,
                user_crea,
                user_cierre from  tfin_cuentas where per_id = {0} and tc_id = {1} 
        """.format(per_id, tc_id)

        tupla_desc = (
            'cue_id',
            'per_id',
            'tc_id',
            'cue_fecha_apertura',
            'cue_estado',
            'cue_nombre',
            'cue_num_libreta',
            'cue_fecha_cierre',
            'cue_saldo_total',
            'cue_saldo_bloq',
            'cue_saldo_disp',
            'user_crea',
            'user_cierre'
        )
        return self.first(sql, tupla_desc)

    def get_form(self, per_id):
        form = {
            'tc_id': 1,
            'per_id': per_id,
            'cue_nombre': 'CTA AHORROS',
            'cue_num_libreta': '',
            'max_cue_id': 1
        }

        sql_tipos_cuenta = """
        select tc_id, tc_nombre from tfin_tiposcuenta order by tc_id 
        """

        sql_max_tipo_cuenta = """
        select coalesce(max(cue_id),0)+1 as max_cue_id from tfin_cuentas
        """
        max_cue_id = self.first_col(sql_max_tipo_cuenta, 'max_cue_id')
        form['max_cue_id'] = max_cue_id

        tipos_cuenta = self.all(sql_tipos_cuenta, tupla_desc=('tc_id', 'tc_nombre'))
        return {
            'form': form,
            'tiposcuenta': tipos_cuenta
        }

    def find_by_id(self, cue_id):
        return self.dbsession.query(TFinCuentas).filter(TFinCuentas.cue_id == cue_id).first()

    def crear(self, form, user_crea, crea_cta_certificados=True):
        tfin_cuenta = TFinCuentas()

        tfin_cuenta.per_id = form['per_id']
        tfin_cuenta.tc_id = 1
        tfin_cuenta.cue_fecha_apertura = datetime.datetime.now()
        tfin_cuenta.cue_estado = 1
        tfin_cuenta.cue_nombre = form['cue_nombre']
        tfin_cuenta.cue_num_libreta = form['cue_num_libreta']
        tfin_cuenta.user_crea = user_crea

        self.dbsession.add(tfin_cuenta)
        self.dbsession.flush()

        if crea_cta_certificados:
            tfin_cuenta_cert = TFinCuentas()
            tfin_cuenta_cert.tc_id = 2
            tfin_cuenta_cert.per_id = form['per_id']
            tfin_cuenta_cert.cue_fecha_apertura = datetime.datetime.now()
            tfin_cuenta_cert.cue_estado = 1
            tfin_cuenta_cert.cue_nombre = 'CERTIFICADOS'
            tfin_cuenta_cert.cue_num_libreta = ''
            tfin_cuenta_cert.user_crea = user_crea
            self.dbsession.add(tfin_cuenta_cert)

        return tfin_cuenta.cue_id

    def cambiar_estado(self, cue_id, new_estado):
        tfincuenta = self.find_by_id(cue_id)
        if tfincuenta is not None:
            tfincuenta.cue_estado = new_estado
            self.dbsession.add(tfincuenta)
