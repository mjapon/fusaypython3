# coding: utf-8
"""
Fecha de creacion 3/12/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tmodelocontab.tmodelocontab_dao import TModelocontabDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tmodelocontab', path='/api/tmodelocontab/{mc_id}', cors_origins=('*',))
class TModelocontabRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        tmodelocontabdao = TModelocontabDao(self.dbsession)
        if accion == 'listar':
            items = tmodelocontabdao.listar()
            return self.res200({'items': items})
