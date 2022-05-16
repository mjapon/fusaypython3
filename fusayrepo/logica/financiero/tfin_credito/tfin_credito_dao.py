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
from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_dao import TFinAmortizaDao
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_model import TFinCredito
from fusayrepo.logica.financiero.tfin_credito.tfin_histocred_dao import TFinHistoCredDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.utils import sqls, cadenas, fechas

log = logging.getLogger(__name__)


class TFinCreditoDao(BaseDao):

    def find_by_credid(self, cre_id):
        return self.dbsession.query(TFinCredito).filter(TFinCredito.cre_id == cre_id).first()

    def get_form_lista(self):
        sqlestados = """
        select est_id, est_nombre from tfin_estadocred 
            union select 0,'Todos' order by est_id
        """
        tupla_desc = ('est_id', 'est_nombre')
        estados = self.all(sqlestados, tupla_desc)
        form = {
            'filtro': '',
            'estado': 0
        }
        return {
            'form': form,
            'estados': estados
        }

    def get_form(self, per_id):
        paramsdao = TParamsDao(self.dbsession)
        paramtasa = 'cj_tasa_gen'
        paramtasa_value = paramsdao.get_param_value(paramtasa)
        if paramtasa_value is None:
            raise ErrorValidacionExc('El parámetro cj_tasa_gen no está registrado, favor verificar')

        form = {
            'per_id': per_id,
            'per_ciruc': '',
            'cre_id': 0,
            'cre_monto': 0.0,
            'cre_tasa': float(paramtasa_value),
            'cre_obs': '',
            'cre_plazo': 12,
            'cre_tipoint': 1,
            'cre_prod': 1,
            'cre_fecprestamo': fechas.get_str_fecha_actual(),
            'marca_aprobado': False
        }

        sqlprod = """
        select prod_id, prod_nombre, prod_tasa from tfin_producto order by prod_nombre
        """
        tupla_desc = ('prod_id', 'prod_nombre', 'prod_tasa')

        productos = self.all(sqlprod, tupla_desc)
        if len(productos) > 0:
            producto = productos[0]
            form['cre_tasa'] = producto['prod_tasa']

        return {
            'form': form,
            'productos': productos
        }

    def get_datos_credito(self, cre_id):
        sql = """
        select cre.cre_id, cre.per_id, cre.cre_monto, cre.cre_tasa, 
        cre.cre_fechacrea, cre.cre_usercrea, cre.cre_fecaprob, cre.cre_fecaprob::date as fecaprob,
        cre.cre_estado, est.est_nombre, cre.cre_obs, cre.cre_plazo,
        cre.cre_cuota, cre.cre_totalint, cre.cre_totalseguro,
        cre.cre_prod, cre.cre_tipoint, prod.prod_nombre, cre.cre_saldopend , cre.cre_fecprestamo
        from tfin_credito cre
        join tfin_estadocred est on cre.cre_estado = est.est_id
        join tfin_producto prod on cre.cre_prod = prod.prod_id
         where cre_id = {0}
        """.format(cre_id)
        tupla_desc = ('cre_id', 'per_id', 'cre_monto', 'cre_tasa', 'cre_fechacrea', 'cre_usercrea', 'cre_fecaprob',
                      'fecaprob', 'cre_estado', 'est_nombre', 'cre_obs', 'cre_plazo', 'cre_cuota', 'cre_totalint',
                      'cre_totalseguro', 'cre_prod', 'cre_tipoint', 'prod_nombre', 'cre_saldopend', 'cre_fecprestamo')
        return self.first(sql, tupla_desc)

    def get_grid(self, filtro, estado=0):
        grid_dao = TGridDao(self.dbsession)
        sqlwhere = sqls.get_filtro_nomapelcedul(filtro)
        where = ""
        wherestado = ""
        if int(estado) > 0:
            wherestado = " cre.cre_estado={0}".format(estado)

        if cadenas.es_nonulo_novacio(sqlwhere):
            where = " ({0}) ".format(sqlwhere)
            if cadenas.es_nonulo_novacio(wherestado):
                where += " and {0}".format(wherestado)
        elif cadenas.es_nonulo_novacio(wherestado):
            where = " {0} ".format(wherestado)

        if cadenas.es_nonulo_novacio(where):
            where = " where {0} ".format(where)

        grid = grid_dao.run_grid(grid_nombre='fin_creditos', where=where)
        return grid

    def get_datos_credito_full(self, cre_id):
        datos_cred = self.get_datos_credito(cre_id)
        persondao = TPersonaDao(self.dbsession)
        amordao = TFinAmortizaDao(self.dbsession)
        referente = persondao.buscar_porperid_full(per_id=datos_cred['per_id'])
        tabla = amordao.get_tabla(cre_id=cre_id)
        return {
            'credito': datos_cred,
            'referente': referente,
            'tabla': tabla
        }

    def cambiar_estado(self, form, user_edit, sec_codigo):
        cre_id = form['cre_id']
        cre_estado = int(form['cre_estado'])
        obs = form['obs']

        credito = self.find_by_credid(cre_id=cre_id)
        if credito is None:
            raise ErrorValidacionExc('No existe ningún crédito registrado con el código {0}'.format(cre_id))

        current_state = credito.cre_estado

        accion = 'actualizado'
        map_acciones = {
            2: 'aprobado',
            3: 'liquidado',
            4: 'anulado'
        }
        if cre_estado in map_acciones.keys():
            accion = map_acciones[cre_estado]

        msg = 'El crédito fue {0} exitosamente'.format(accion)
        credito.cre_estado = cre_estado
        histocred_dao = TFinHistoCredDao(self.dbsession)
        histocred_dao.crear(cre_id=cre_id,
                            user_crea=user_edit,
                            previus_state=current_state,
                            new_state=cre_estado,
                            obs=obs)

        # Si el credito cambia a estado aprobado entonces se debe generar el asiento contable
        if cre_estado == 2:
            credito.cre_fecaprob = datetime.datetime.now()
            tasicred_dao = TAsicreditoDao(self.dbsession)
            monto_credito = credito.cre_monto
            tasicred_dao.create_asiento_prestamo(per_codigo=credito.per_id, sec_codigo=sec_codigo,
                                                 monto=monto_credito, usercrea=user_edit)

            # En el caso en que la fecha de aprobacion sea distinta a la fecha de creacion, se actualiza tabla amortiza
            if credito.cre_fecaprob.date() != credito.cre_fechacrea.date():
                amordao = TFinAmortizaDao(self.dbsession)
                amordao.anular_tabla(cred_id=cre_id)

                amortiza_dao = TFinAmortizaDao(self.dbsession)
                result_tbl = amortiza_dao.generar_guardar_tabla(
                    cred_id=cre_id,
                    monto_prestamo=float(credito.cre_monto),
                    tasa_interes=float(credito.cre_tasa),
                    fecha_prestamo=credito.cre_fecaprob,
                    ncuotas=credito.cre_plazo,
                    user_crea=user_edit
                )

                if result_tbl is not None:
                    credito.cre_totalint = result_tbl['total_int']
                    credito.cre_cuota = result_tbl['cuota_mensual']
                    credito.cre_totalseguro = result_tbl['total_seguro']

        self.dbsession.add(credito)

        return msg

    def reversar_saldo_pend(self, cred_id, capital, user_reversa):
        credito = self.find_by_credid(cred_id)
        if credito is not None:
            cre_saldopend = credito.cre_saldopend
            new_saldopend = cre_saldopend + capital
            if new_saldopend > credito.cre_monto:
                credito.cre_saldopend = credito.cre_monto
            else:
                credito.cre_saldopend = new_saldopend

            self.dbsession.add(credito)

            histocred_dao = TFinHistoCredDao(self.dbsession)
            current_state = credito.cre_estado

            if current_state == 5:
                credito.cre_estado = 3  # Si estuvo en cancelado se ponde nuevamente como liquidado
                histocred_dao.crear(cre_id=cred_id,
                                    user_crea=user_reversa,
                                    previus_state=current_state,
                                    new_state=credito.cre_estado,
                                    obs='Se hizo reverso de pago de credito')

    def update_saldo_pend(self, cred_id, capital, user_upd):
        credito = self.find_by_credid(cred_id)
        new_saldopend = 0
        if credito is not None:
            cre_saldopend = credito.cre_saldopend
            new_saldopend = cre_saldopend - capital
            if new_saldopend < 0:
                new_saldopend = 0.0

            credito.cre_saldopend = new_saldopend

            if new_saldopend == 0.0:
                current_state = credito.cre_estado
                credito.cre_estado = 5  # Se marca como credito cancelado

                histocred_dao = TFinHistoCredDao(self.dbsession)
                histocred_dao.crear(cre_id=cred_id,
                                    user_crea=user_upd,
                                    previus_state=current_state,
                                    new_state=credito.cre_estado,
                                    obs='Se registra cancelación total de deuda')

            self.dbsession.add(credito)

        return new_saldopend

    def crear(self, form, user_crea):

        per_id = form['per_id']
        persondao = TPersonaDao(self.dbsession)
        tpersona = persondao.get_entity_byid(per_id=per_id)
        if tpersona is None:
            raise ErrorValidacionExc('Debe especificar el referente del crédito')

        param_monto_max = 'cj_monto_max'
        paramsdao = TParamsDao(self.dbsession)
        param_monto_max_value = paramsdao.get_param_value(param_monto_max)
        if param_monto_max_value is None:
            raise ErrorValidacionExc('El parámetro cj_monto_max no está registrado, favor verificar')

        cre_monto = Decimal(form['cre_monto'])
        if cre_monto <= 0 or cre_monto > Decimal(param_monto_max_value):
            raise ErrorValidacionExc(
                'El monto del prestamo no puede ser negativo, ni cero,  ni superior al monto máximo ({0}) '.format(
                    param_monto_max_value))

        cre_tasa = Decimal(form['cre_tasa'])
        if cre_tasa <= 0 or cre_tasa >= 100.0:
            raise ErrorValidacionExc('El valor de la tasa ingresada es incorrecta, favor verificar')

        cre_plazo = int(form['cre_plazo'])
        param_plazo_max = 'cj_plaxo_max'
        param_plazo_max_value = paramsdao.get_param_value(param_plazo_max)
        if cre_plazo <= 0 or cre_plazo > int(param_plazo_max_value):
            raise ErrorValidacionExc(
                'El plazo  ingresado es incorrecto debe estar entre 1 y {0}'.format(param_plazo_max_value))

        cre_fecprestamo = form['cre_fecprestamo']
        if not cadenas.es_nonulo_novacio(cre_fecprestamo):
            raise ErrorValidacionExc('Debe ingresar la fecha de emisión del préstamo')

        credito = TFinCredito()
        credito.per_id = per_id
        credito.cre_monto = cre_monto
        credito.cre_tasa = cre_tasa
        credito.cre_fechacrea = datetime.datetime.now()
        credito.cre_usercrea = user_crea
        credito.cre_estado = 1
        credito.cre_obs = form['cre_obs']
        credito.cre_plazo = cre_plazo
        credito.cre_prod = form['cre_prod']
        credito.cre_tipoint = form['cre_tipoint']
        credito.cre_cuota = 0.0
        credito.cre_totalint = 0.0
        credito.cre_saldopend = cre_monto
        credito.cre_fecprestamo = fechas.parse_cadena(cre_fecprestamo)

        marca_aprobado = form['marca_aprobado']
        if marca_aprobado:
            credito.cre_estado = 2

        self.dbsession.add(credito)
        self.dbsession.flush()

        cre_id = credito.cre_id

        amortiza_dao = TFinAmortizaDao(self.dbsession)
        result_tbl = amortiza_dao.generar_guardar_tabla(
            cred_id=cre_id,
            monto_prestamo=float(cre_monto),
            tasa_interes=float(cre_tasa),
            fecha_prestamo=credito.cre_fecprestamo,
            ncuotas=cre_plazo,
            user_crea=user_crea
        )

        if result_tbl is not None:
            credito = self.find_by_credid(cre_id=cre_id)
            credito.cre_totalint = result_tbl['total_int']
            credito.cre_cuota = result_tbl['cuota_mensual']
            credito.cre_totalseguro = result_tbl['total_seguro']

            self.dbsession.add(credito)

        return cre_id
