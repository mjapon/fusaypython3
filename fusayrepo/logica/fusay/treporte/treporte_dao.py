# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging
from datetime import datetime

import simplejson

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuser.tfuser_dao import TFuserDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils import fechas

log = logging.getLogger(__name__)


class TReporteDao(BaseDao):

    def get_form(self, sec_id):
        form = {
            'desde': fechas.parse_fecha(fechas.sumar_dias(datetime.now(), -7)),
            'hasta': fechas.parse_fecha(datetime.now()),
            'codrep': 0,
            'secid': sec_id,
            'refid': 0,
            'usid': 0,
            'formato': 1
        }

        secdao = TSeccionDao(self.dbsession)
        secciones = secdao.listar()
        userdao = TFuserDao(self.dbsession)
        usuarios = userdao.listar()

        usuarios.append({'us_id': 0, 'nomapel': 'Todos'})

        # formatos = [{'label': 'PDF', 'value': 1}, {'label': 'Excel', 'value': 2}, {'label': 'HTML', 'value': 3}]
        formatos = [{'label': 'PDF', 'value': 1}]

        return {
            'formatos': formatos,
            'form': form,
            'secciones': secciones,
            'usuarios': usuarios
        }

    def listar(self, sec_id=0):
        sql = """
        select rep_id, rep_nombre, rep_detalle, rep_params, rep_cat from treporte
        order by rep_nombre asc
        """

        tupla_desc = ('rep_id', 'rep_nombre', 'rep_detalle', 'rep_params', 'rep_cat')

        reportes = self.all(sql, tupla_desc)

        for rep in reportes:
            rep_params_json = simplejson.loads(rep['rep_params'])
            rep['params'] = rep_params_json

        return reportes
