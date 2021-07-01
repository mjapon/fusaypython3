# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging
from datetime import datetime

from cornice.resource import resource

from fusayrepo.logica.fusay.treporte.treporte_dao import TReporteDao
from fusayrepo.utils import fechas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/treporte', path='/api/treporte/{rep_id}', cors_origins=('*',))
class TReporteRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        if accion == 'listar':
            repdao = TReporteDao(self.dbsession)
            reportes = repdao.listar()
            return self.res200({'reportes': reportes})
        elif accion == 'form':
            form = {
                'desde': fechas.parse_fecha(fechas.sumar_dias(datetime.now(), -7)),
                'hasta': fechas.parse_fecha(datetime.now()),
                'codrep': 0
            }
            return self.res200({'form': form})
