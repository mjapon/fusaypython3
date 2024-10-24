import datetime
import logging

from fusayrepo.logica.compele.compele_util import CompeleUtilDao
from fusayrepo.logica.compele.gen_data import GenDataForFacte
from fusayrepo.logica.compele.tdatosfacte_dao import TDatosFacteDao
from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


def get_ndias_caducar(expiry_date):
    current_date = datetime.datetime.now()
    delta = expiry_date - current_date
    return delta.days


class DatosLoggedService(BaseDao):

    def get_info_factele(self, sec_id):
        gendataforfacte = GenDataForFacte(self.dbsession)
        compeleutil = CompeleUtilDao(self.dbsession)

        tipoambiente = compeleutil.get_facte_tipoamb(sec_id)

        fecha_caducidad = ''
        ndiascaducar = None

        try:
            if tipoambiente > 0:
                talm_matriz = gendataforfacte.get_datos_alm_matriz(sec_codigo=sec_id)
                if talm_matriz is not None:
                    alm_ruc = talm_matriz['alm_ruc']
                    datosfactedato = TDatosFacteDao(self.dbsession)
                    datos_facte_emp = datosfactedato.find_by_emp_codigo(emp_ruc=alm_ruc)
                    if datos_facte_emp is not None and datos_facte_emp['df_pathdigital_sign'] is not None:
                        fecha_caducidad = compeleutil.get_fecha_caducidad(
                            path_firma_digital=datos_facte_emp['df_pathdigital_sign'],
                            clave_firma_digital=datos_facte_emp['df_passdigital_sign'])
                        ndiascaducar = get_ndias_caducar(fecha_caducidad)
        except Exception as ex:
            log.error('Se prudujo un error controlado al tratar de obtener la informacionde facturacion electronica',
                      ex)

        return {
            'tipoambiente': tipoambiente,
            'fechacaducidadfirma': self.type_json(fecha_caducidad),
            'ndiasxcaducar': ndiascaducar
        }
