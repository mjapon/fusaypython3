# coding: utf-8
"""
Fecha de creacion 5/12/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.aguap.tagp_models import TAgpMedidor
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TagpMedidorAguaDao(BaseDao):

    @staticmethod
    def _aux_valid_mdg_num(form):
        if not cadenas.es_nonulo_novacio(form['mdg_num']):
            raise ErrorValidacionExc('Ingrese el número de cédula, ruc o pasaporte')

    @staticmethod
    def get_form():
        return {
            'mdg_id': 0,
            'cna_id': 0,
            'mdg_num': '',
            'mdg_estado': 1,
            'mdg_estadofis': 1,
            'mdg_obs': ''
        }

    def existe(self, mdg_num):
        sql = """
        select count(*) as cuenta from tagp_medidor where mdg_num = '{0}'
        and mdg_estado = 1
        """.format(cadenas.strip(mdg_num))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def validarcrea(self, form):
        self._aux_valid_mdg_num(form)
        mdg_num = form['mdg_num']
        if self.existe(mdg_num):
            raise ErrorValidacionExc(
                'Ya existe un medidor registrado con el número \'{0}\', favor verificar'.format(mdg_num))

    def crear(self, form, usercrea):
        self.validarcrea(form)
        medidor = TAgpMedidor()
        medidor.cna_id = form['cna_id']
        medidor.mdg_num = form['mdg_num']
        medidor.mdg_estado = form['mdg_estado']
        medidor.mdg_estadofis = form['mdg_estadofis']
        medidor.mdg_obs = form['mdg_obs']
        medidor.mdg_fechacrea = datetime.now()
        medidor.mdg_usercrea = usercrea
        self.dbsession.add(medidor)
