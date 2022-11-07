# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.compele import ctes_facte
from fusayrepo.logica.compele.tcomprobante.tcomprobante_dao import TComprobanteDao
from fusayrepo.utils.pyramidutil import FacteView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tfacte', path='/api/tfacte/{trn_codigo}', cors_origins=('*',))
class FacteComprobRest(FacteView):

    def collection_get(self):
        accion = self.get_request_param('accion')

        if accion == 'facturas':
            comprobantedao = TComprobanteDao(self.dbsession)
            comprobantes = comprobantedao.listar_grid(cnt_id=self.get_user_id(), tipo=ctes_facte.COD_DOC_FACTURA)

            return self.res200({'comprobantes': comprobantes})
