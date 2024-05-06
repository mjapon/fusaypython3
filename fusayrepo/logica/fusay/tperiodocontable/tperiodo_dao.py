# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tperiodocontable.tperiodocontable_model import TPeriodoContable
from fusayrepo.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TPeriodoContableDao(BaseDao):

    def get_datos_periodo_contable(self):
        sql = "select pc_id, pc_desde, pc_hasta, pc_fechacrea from tperiodocontable where pc_activo = true"
        tupla_desc = ('pc_id', 'pc_desde', 'pc_hasta', 'pc_fechacrea')
        return self.first(sql, tupla_desc)

    def get_datos_periodo_anterior(self):
        sql = "select pc_id, pc_desde, pc_hasta, pc_fechacrea from tperiodocontable " \
              "where pc_activo = false order by pc_hasta desc limit 1"
        tupla_desc = ('pc_id', 'pc_desde', 'pc_hasta', 'pc_fechacrea')
        return self.first(sql, tupla_desc)

    def get_info_cta_utilidades_acumuladas(self):
        paramsdao = TParamsDao(self.dbsession)
        cta_contab_result = paramsdao.get_param_value('cta_contresult_acum')
        # TODO: Validar existencia de parametro
        sql = """
        select ic.ic_id, ic_code, ic_nombre, ic_code||' '||ic_nombre as codenombre, ic_padre, ic_haschild, 
                    0.0 as total 
                    from titemconfig ic where ic.ic_code = '{0}'
        """.format(cta_contab_result)

        tupla = ('ic_id', 'ic_code', 'ic_nombre', 'codenombre', 'ic_padre', 'ic_haschild', 'total')
        return self.first(sql, tupla)

    def get_asientos_cierre(self, pc_id):
        sql = "select pc_id, pc_asientos_cierre from tperiodocontable where pc_id = {0}" \
            .format(pc_id)
        tupla = ('pc_id', 'pc_asientos_cierre')
        datos_cierre = self.first(sql, tupla)
        if datos_cierre is not None:
            asientos = datos_cierre['pc_asientos_cierre']
            if cadenas.es_nonulo_novacio(asientos):
                sqldet = """
                        select det.dt_codigo, det.cta_codigo, det.dt_cant, det.dt_debito, det.dt_tipoitem, det.dt_valor,
                               det.dt_valor as dt_valor_in, ic.ic_clasecc, ic.ic_code, ic.ic_nombre, det.per_codigo, det.pry_codigo,
                               det.dt_codsec
                            from tasidetalle det
                            join titemconfig ic on det.cta_codigo = ic.ic_id
                            where det.trn_codigo in ({0}) order by det.dt_debito desc, ic.ic_nombre
                        """.format(asientos)

                tupla_desc = ('dt_codigo', 'cta_codigo', 'dt_cant', 'dt_debito', 'dt_tipoitem', 'dt_valor',
                              'dt_valor_in', 'ic_clasecc', 'ic_code', 'ic_nombre', 'per_codigo', 'pry_codigo',
                              'dt_codsec')

                detalles = self.all(sqldet, tupla_desc)
                return detalles
        return None

    def find_by_id(self, pc_id):
        return self.dbsession.query(TPeriodoContable).filter(TPeriodoContable.pc_id == pc_id).first()

    def cerrar(self, pc_id, user_cierra, fecha_cierre, asientos):
        tperiodo = self.find_by_id(pc_id)
        if tperiodo is not None and tperiodo.pc_activo:
            tperiodo.pc_fechaupd = datetime.datetime.now()
            tperiodo.pc_userupd = user_cierra
            tperiodo.pc_hasta = fechas.parse_cadena(fecha_cierre)
            tperiodo.pc_activo = False

            # Registro de asientos contabls
            tasiento_dao = TasientoDao(self.dbsession)
            codigos_asientos = []
            for asiento in asientos:
                trn_codigo = tasiento_dao.crear_asiento(formcab=asiento['formcab'],
                                                        formref=asiento['formref'],
                                                        usercrea=user_cierra,
                                                        detalles=asiento['detalles'])
                codigos_asientos.append(trn_codigo)

            if len(codigos_asientos) > 0:
                str_codigos = ",".join([str(it) for it in codigos_asientos])
                tperiodo.pc_asientos_cierre = str_codigos

            self.dbsession.add(tperiodo)

    def crear(self, form, user_crea):
        # Verificamos si existe un periodo contable actual
        periodoactual = self.get_datos_periodo_contable()
        if periodoactual is not None and periodoactual['pc_id'] > 0:
            raise ErrorValidacionExc('No se puede aperturar un nuevo periodo '
                                     + 'contable, ya existe un periodo vigente, primero cierre el periodo actual')

        tperiodo = TPeriodoContable()

        tperiodo.pc_fechacrea = datetime.datetime.now()
        tperiodo.pc_usercrea = user_crea
        tperiodo.pc_desde = fechas.parse_cadena(form['desde'])
        tperiodo.pc_hasta = fechas.parse_cadena(form['hasta'])
        tperiodo.pc_activo = True

        trn_codigo = None
        if form['asiento'] is not None:
            asiento = form['asiento']
            tasiento_dao = TasientoDao(self.dbsession)
            trn_codigo = tasiento_dao.crear_asiento(formcab=asiento['formcab'],
                                                    formref=asiento['formref'],
                                                    usercrea=user_crea,
                                                    detalles=asiento['detalles'])

        tperiodo.pc_asiento_inicial = trn_codigo
        self.dbsession.add(tperiodo)
        self.flush()
        return tperiodo.pc_id
