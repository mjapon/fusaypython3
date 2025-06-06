# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging
from decimal import Decimal

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.financiero.tfin_cuentas.tfin_cuentas_model import TFinCuentas
from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_model import TFinMovimientos
from fusayrepo.utils import cadenas, fechas, numeros

log = logging.getLogger(__name__)


class TFinMovimientosDao(BaseDao):

    def get_form(self, cue_id):
        form = {
            'cue_id': cue_id,
            'cuen_num': '',
            'mov_numero_comprob': '',
            'mov_abreviado': '',
            'mov_deb_cred': 1,
            'mov_total_transa': 0.0,
            'mov_num_linea': 0,
            'mov_tipotransa': 0,
            'mov_obs': ''
        }

        sqltransa = """
        select 0 tipt_id, 'Elija uno' tipt_nombre, '' tipt_cod, 0 tipt_debcred,'Elija uno' codnombre
        union
        select
        tipt_id, tipt_nombre, tipt_cod, tipt_debcred, tipt_cod||' - '||tipt_nombre codnombre from tfin_tipostran order by tipt_nombre 
        """
        tupla_desc = ('tipt_id', 'tipt_nombre', 'tipt_cod', 'tipt_debcred', 'codnombre')

        transacciones = self.all(sqltransa, tupla_desc)

        return {
            'form': form,
            'tipostrans': transacciones
        }

    def get_mov_details(self, mov_id):
        sql = """
        select mov.mov_id, mov.mov_deb_cred, mov.mov_total_transa, mov.mov_saldo_transa,
        cta.per_id from tfin_movimientos mov 
        join tfin_cuentas cta on mov.cue_id = cta.cue_id
        where mov.mov_id = {0} and mov.mov_estado = 1
        """.format(mov_id)
        tupla_desc = ('mov_id', 'mov_deb_cred', 'mov_total_transa', 'mov_saldo_transa', 'per_id')
        return self.first(sql, tupla_desc)

    def contar_grid_movimientos(self, cue_id, filtro_fechas):
        sql = f"""
        select count(*) as cuenta from tfin_movimientos mov
                join tfin_tipostran tp on tp.tipt_id = mov.mov_tipotransa
                where cue_id = {cue_id} and mov_estado = 1 {filtro_fechas} 
        """
        result = self.first_raw(sql)
        return result[0] if result is not None else 0

    def listar(self, cue_id, desde='', hasta='', limit=50, first=0):
        qlimit = f"limit {limit}"
        qoffset = f"offset {first}"

        filtro_fechas = ""
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            filtro_fechas = " and date(mov_fecha_sistema)>='{0}' and date(mov_fecha_sistema)<='{1}' ".format(
                fechas.format_cadena_db(desde),
                fechas.format_cadena_db(hasta)
            )

        sql = f"""
        select mov_id, cue_id, user_crea, mov_abreviado, 
                case when mov_deb_cred=1 then mov_total_transa else null end ingreso,
                case when mov_deb_cred=-1 then mov_total_transa else null end egreso,
                tp.tipt_nombre,
                mov_fecha_sistema,
                mov_saldo_transa, mov_obs
                from tfin_movimientos mov
                join tfin_tipostran tp on tp.tipt_id = mov.mov_tipotransa
                where cue_id = {cue_id} and mov_estado = 1 {filtro_fechas}  order by mov_fecha_sistema desc 
                {qlimit} {qoffset} 
        """

        tupla_desc = ('mov_id',
                      'cue_id',
                      'user_crea',
                      'mov_abreviado',
                      'ingreso',
                      'egreso',
                      'tipt_nombre',
                      'mov_fecha_sistema',
                      'mov_saldo_transa', 'mov_obs')
        data = self.all(sql, tupla_desc)

        columnas = [
            {"label": "Fecha", "field": "mov_fecha_sistema"},
            {"label": "Tipo", "field": "mov_abreviado"},
            {"label": "Transacción", "field": "tipt_nombre"},
            {"label": "Ingreso", "field": "ingreso"},
            {"label": "Egreso", "field": "egreso"},
            {"label": "Saldo", "field": "mov_saldo_transa"},
            {"label": "Obs", "field": "mov_obs"}
        ]

        resultgrid = {
            'data': data,
            'cols': columnas
        }

        if int(first) == 0:
            total = self.contar_grid_movimientos(cue_id, filtro_fechas)
            resultgrid['total'] = total

        return resultgrid

    def crear(self, form, user_crea):
        tfin_mov = TFinMovimientos()

        total_transa = numeros.roundm2(form['mov_total_transa'])
        mov_deb_cred = int(form['mov_deb_cred'])
        cue_id = form['cue_id']
        tfin_mov.cue_id = cue_id
        tfin_mov.mov_fecha_sistema = datetime.datetime.now()
        tfin_mov.mov_numero_comprob = form['mov_numero_comprob']
        tfin_mov.mov_abreviado = form['mov_abreviado']
        tfin_mov.mov_deb_cred = mov_deb_cred
        tfin_mov.mov_total_transa = total_transa
        tfin_mov.mov_num_linea = form['mov_num_linea']
        tfin_mov.mov_tipotransa = form['mov_tipotransa']
        tfin_mov.mov_obs = cadenas.strip(form['mov_obs'])
        tfin_mov.user_crea = user_crea

        tfincuenta = self.dbsession.query(TFinCuentas).filter(TFinCuentas.cue_id == cue_id).first()
        if tfincuenta is None:
            raise ErrorValidacionExc('No pude recuperar la informacion de la cuenta')

        cue_saldo_disp = numeros.roundm2(tfincuenta.cue_saldo_disp)

        new_saldo_disp = numeros.roundm2(cue_saldo_disp + (total_transa * tfin_mov.mov_deb_cred))
        if new_saldo_disp < 0:
            raise ErrorValidacionExc(
                'Fondos insuficientes (saldo anterior:{0}, monto transacción:{1}, nuevo saldo:{2})'.format(
                    cue_saldo_disp, total_transa, new_saldo_disp))

        tfincuenta.cue_saldo_disp = new_saldo_disp
        tfincuenta.cue_saldo_total = tfincuenta.cue_saldo_bloq + Decimal(new_saldo_disp)
        tfin_mov.mov_saldo_transa = new_saldo_disp

        self.dbsession.add(tfin_mov)
        self.dbsession.add(tfincuenta)

        self.flush()
        return tfin_mov.mov_id

    def find_entity_by_id(self, mov_id):
        return self.dbsession.query(TFinMovimientos).filter(TFinMovimientos.mov_id == mov_id).first()

    def update_trn_codigo(self, mov_id, trn_codigo):
        tfinmovimiento = self.find_entity_by_id(mov_id)
        if tfinmovimiento is not None:
            tfinmovimiento.trn_codigo = trn_codigo
            self.dbsession.add(tfinmovimiento)

    """
    def mov_apertura(self, form, user_crea):
        #1Crear nota credito del deposito
        #2Crear nota de debito costo de emision de libreta
        #3Crear nota de debito por transferencia a cuenta de cert de aportacion
        #3	DÉBITO COSTO LIBRETA	NDCLI
        #15	DÉBITO CERT APORTACIÓN	NDCAP
        #12	CRÉDITO POR TRANSFERENCIA
        
        form_mov_costo = {
            'mov_total_transa':
        }
    """
