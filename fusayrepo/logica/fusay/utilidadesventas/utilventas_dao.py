# coding: utf-8
"""
Fecha de creacion 3/28/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.utils import fechas, numeros

log = logging.getLogger(__name__)


class UtilidadesVentasDao(BaseDao):

    def get_form(self):
        form = {
            'desde': fechas.parse_fecha(fechas.sumar_dias(datetime.now(), -7)),
            'hasta': fechas.parse_fecha(datetime.now()),
            'tipotra': 0,
            'tipopago': 0,
            'tipoprod': 1
        }

        transaccdao = TTransaccDao(self.dbsession)
        transaccs = transaccdao.listar_min("'1','2'")

        transaccsret = [{'tra_codigo': 0, 'tra_nombre': 'Todos'}]
        for cuenta in transaccs:
            transaccsret.append(cuenta)

        formaspago = [
            {'label': 'Todos', 'value': 0},
            {'label': 'Efectivo', 'value': 1},
            {'label': 'Crédito', 'value': 2},
            {'label': 'Crédito cancelados', 'value': 3},
            {'label': 'Crédito pendientes', 'value': 4},
        ]

        tiposprodserv = [
            {'label': 'Todos', 'value': 0},
            {'label': 'Productos', 'value': 1},
            {'label': 'Servicios', 'value': 2},
        ]

        return {
            'form': form,
            'transaccs': transaccsret,
            'formaspago': formaspago,
            'tiposprodserv': tiposprodserv
        }

    def listar_grid(self, form):
        griddado = TGridDao(self.dbsession)
        swhere = """ and  ( asi.trn_fecreg between '{0}' and '{1}' ) """.format(
            fechas.format_cadena_db(form['desdestr']),
            fechas.format_cadena_db(form['hastastr']))
        if int(form['tipotra']) > 0:
            swhere = """ {0} and asi.tra_codigo = {1} """.format(swhere, form['tipotra'])

        tipopago = int(form['tipopago'])
        if tipopago > 0:
            if tipopago == 1:
                swhere = """ {0} and pagos.credito = 0.0 """.format(swhere)
            elif tipopago == 2:
                swhere = """ {0} and pagos.credito > 0.0 """.format(swhere)
            elif tipopago == 3:
                swhere = """ {0} and pagos.credito > 0.0 and pagos.saldopend = 0.0 """.format(swhere)
            elif tipopago == 4:
                swhere = """ {0} and pagos.credito > 0.0 and pagos.saldopend > 0.0 """.format(swhere)

        if int(form['tipoprod']) > 0:
            swhere = """ {0} and ic.tipic_id = {1} """.format(swhere, form['tipoprod'])

        data = griddado.run_grid('utilidades', swhere=swhere)

        # Totalizar
        totales = {'efectivo': 0.0, 'credito': 0.0, 'saldopend': 0.0, 'utilidad': 0.0}
        for item in data['data']:
            totales['utilidad'] += item['utilidad']

        totales['utilidad'] = numeros.roundm2(totales['utilidad'])

        return data, totales
