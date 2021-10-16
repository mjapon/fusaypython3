# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tcierre.tcierre_model import TCierre
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.utils import fechas, numeros


class TCierreDao(BaseDao):

    def get_form_apertura(self):
        return {
            'cie_codigo': 0,
            'cie_dia': fechas.get_str_fecha_actual(),
            'cie_obsaper': ''
        }

    def get_form_cierre(self, cie_codigo):
        return {
            'cie_codigo': cie_codigo,
            'cie_obscierre': ''
        }

    def existe_cierre(self, cie_dia):
        sql = "select count(*) as cuenta from tcierre where cie_dia = '{0}' and cie_estado = 0".format(
            fechas.format_cadena_db(cie_dia))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def abrir_caja(self, form, user_crea):
        tcierre = TCierre()
        if self.existe_cierre(form['cie_dia']):
            raise ErrorValidacionExc('Ya se ya realizado la apertura de caja para el dia: {0}'.format(form['cie_dia']))

        tcierre.cie_dia = fechas.parse_cadena(form['cie_dia'])
        tcierre.cie_usercrea = user_crea
        tcierre.cie_fechapertura = datetime.datetime.now()
        tcierre.cie_estado = 0
        tcierre.cie_estadocierre = 0
        tcierre.cie_obsaper = form['cie_obsaper']
        self.dbsession.add(tcierre)

    def find_by_id(self, cie_codigo):
        return self.dbsession.query(TCierre).filter(TCierre.cie_codigo == cie_codigo).first()

    def anular_cierre(self, cie_codigo):
        tcierre = self.find_by_id(cie_codigo=cie_codigo)
        if tcierre is not None:
            tcierre.cie_estado = 1

    def cerrar_caja(self, form, user_cierra):
        cie_codigo = form['cie_codigo']
        tcierre = self.find_by_id(cie_codigo=cie_codigo)
        if tcierre is not None:
            tcierre.cie_estadocierre = 1
            tcierre.cie_obscierre = form['cie_obscierre']
            tcierre.cie_usercierra = user_cierra
            self.dbsession.add(tcierre)

    def get_reporte_cierre(self, dia, sec_id):

        """
        UPDATE fusay.tgrid SET grid_nombre = 'cierre_ventas' WHERE grid_id = 21;
        UPDATE fusay.tgrid SET grid_nombre = 'cierre_abonos' WHERE grid_id = 22;
        UPDATE fusay.tgrid SET grid_nombre = 'cierre_gastos' WHERE grid_id = 23;
        """

        swhere = " and date(a.trn_fecha) = '{0}' and a.sec_codigo = {1} ".format(fechas.format_cadena_db(dia), sec_id)

        gridDao = TGridDao(self.dbsession)
        gridventas = gridDao.run_grid('cierre_ventas', swhere=swhere)
        gridabonos = gridDao.run_grid('cierre_abonos', swhere=swhere)
        gridgastos = gridDao.run_grid('cierre_gastos', swhere=swhere)

        totalventas = 0.0
        totalabos = 0.0
        totalgast = 0.0

        for item in gridventas['data']:
            totalventas += item['efectivo']

        for item in gridabonos['data']:
            totalabos += item['abono']

        for item in gridgastos['data']:
            totalgast += item['monto']

        totales = {
            'totventas': numeros.roundm2(totalventas),
            'totabos': numeros.roundm2(totalabos),
            'totgast': numeros.roundm2(totalgast)
        }

        return {
            'gridventas': gridventas,
            'gridabos': gridabonos,
            'gridgast': gridgastos,
            'totales': totales
        }
