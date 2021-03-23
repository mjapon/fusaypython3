# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasicredito', path='/api/tasicredito/{trn_codigo}', cors_origins=('*',))
class TAsiCreditoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasicredao = TAsicreditoDao(self.dbsession)
        if accion == 'listarcreds':
            tra_codigo = self.get_request_param('tracod')
            per_codigo = self.get_request_param('per')
            creds, sumas = tasicredao.listar_creditos(per_codigo=per_codigo, tra_codigo=tra_codigo,
                                                      solo_pendientes=False)
            return self.res200({'creds': creds, 'totales': sumas})
        elif accion == 'gdet':
            cre_codigo = self.get_request_param('codcred')
            datoscredito = tasicredao.get_datos_credito(cre_codigo)
            return self.res200({'datoscred': datoscredito})
        elif accion == 'listargrid':
            tipo = self.get_request_param('tipo')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            filtro = self.get_request_param('filtro')
            data, totales = tasicredao.listar(tipo, desde, hasta, filtro)
            return self.res200({'grid': data, 'totales': totales})
