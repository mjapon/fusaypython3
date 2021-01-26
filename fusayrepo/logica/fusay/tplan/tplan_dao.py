# coding: utf-8
"""
Fecha de creacion 1/21/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tplan.tplan_model import TPlan
from fusayrepo.utils import cadenas, ctes

log = logging.getLogger(__name__)


class TPlanDao(BaseDao):

    def listar_grid(self):
        tgriddado = TGridDao(self.dbsession)
        return tgriddado.run_grid('planes')

    def listar(self):
        sql = """
        select pln_id, pln_nombre, pln_obs, pln_fechacrea, pln_estado, trn_codigo
        from tplan order by pln_nombre
        """

        tupla_desc = ('pln_id', 'pln_nombre', 'pln_obs', 'pln_fechacrea', 'pln_estado', 'trn_codigo')
        planes = self.all(sql, tupla_desc)
        tasientodao = TasientoDao(self.dbsession)

        for plan in planes:
            detalles = tasientodao.get_detalles_doc(trn_codigo=plan['trn_codigo'],
                                                    dt_tipoitem=ctes.DT_TIPO_ITEM_DETALLE)
            plan['detalle'] = detalles
            totales = tasientodao.calcular_totales(detalles)
            plan['totales'] = totales

        return planes

    def get_form(self):
        return {
            'pln_id': 0,
            'pln_estado': 0,
            'pln_nombre': '',
            'pln_obs': '',
            'trn_codigo': 0
        }

    def existe_plan(self, pln_nombre):
        sql = "select count(*) as cuenta from tplan where pln_nombre = '{0}' and pln_estado in (0,2,5)".format(
            cadenas.strip_upper(pln_nombre))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form, usercrea):
        formplan = form['formplan']
        pln_nombre = cadenas.strip_upper(formplan['pln_nombre'])

        if not cadenas.es_nonulo_novacio(pln_nombre):
            raise ErrorValidacionExc('El nombre del plan es requerido')

        if self.existe_plan(pln_nombre):
            raise ErrorValidacionExc('Ya existe un plan con el nombre indicado ({0}) ingrese otro'.format(pln_nombre))

        tasientodao = TasientoDao(self.dbsession)
        trn_codigo = tasientodao.crear(form=form['form_cab'], form_persona=form['form_persona'],
                                       user_crea=usercrea,
                                       detalles=form['detalles'], pagos=form['pagos'],
                                       totales=form['totales'])

        tplan = TPlan()
        tplan.pln_fechacrea = datetime.now()
        tplan.pln_estado = formplan['pln_estado']
        tplan.pln_usercrea = usercrea
        tplan.pln_nombre = pln_nombre
        tplan.pln_obs = cadenas.strip(formplan['pln_obs'])
        tplan.trn_codigo = trn_codigo

        self.dbsession.add(tplan)
        self.dbsession.flush()
        pln_id = tplan.pln_id

        return pln_id
