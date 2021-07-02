# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.treporte.treporte_dao import TReporteDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/treporte', path='/api/treporte/{rep_id}', cors_origins=('*',))
class TReporteRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        repdao = TReporteDao(self.dbsession)
        if accion == 'listar':
            reportes = repdao.listar()
            return self.res200({'reportes': reportes})
        elif accion == 'form':
            form = repdao.get_form(self.get_sec_id())
            return self.res200({'form': form})
