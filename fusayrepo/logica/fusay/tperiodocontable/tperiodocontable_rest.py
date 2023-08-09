# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tperiodocontable.tperiodo_dao import TPeriodoContableDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/tperiodocontable", path='/api/tperiodocontable/{per_id}', cors_origins=('*',))
class TPeriodoContableRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        if accion == 'current':
            periododao = TPeriodoContableDao(self.dbsession)
            periodo_contable = periododao.get_datos_periodo_contable()
            if periodo_contable is None:
                raise ErrorValidacionExc('No hay un periodo contable configurado, favor verificar')
            else:
                return {'periodo': periodo_contable}
