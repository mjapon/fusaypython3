# coding: utf-8
"""
Fecha de creacion 3/5/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.titemconfig_autdit.titemconfigaudit_dao import TItemConfigAuditDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/titemconfigaudit', path='/api/titemconfigaudit/{ic_id}', cors_origins=('*',))
class TItemConfigAuditRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        itemconfigauditdao = TItemConfigAuditDao(self.dbsession)
        if accion == 'listar':
            codprod = self.get_request_param('codprod')
            items = itemconfigauditdao.listar_eventos(ic_id=codprod)
            return self.res200({'items': items})
