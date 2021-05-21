# coding: utf-8
"""
Fecha de creacion 5/19/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_pago.tagp_pago_dao import TagpCobroDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagpcobro', path='/api/tagpcobro/{mdg_id}', cors_origins=('*',))
class TagpCobroRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        cobrodao = TagpCobroDao(self.dbsession)
        if accion == 'form':
            form = cobrodao.get_form()
            return self.res200({'form': form})

    def collection_post(self):
        accion = self.get_rqpa()
        cobrodao = TagpCobroDao(self.dbsession)
        if accion == 'gcalpag':
            body = self.get_json_body()
            secdao = TSeccionDao(self.dbsession)
            alm_codigo = secdao.get_alm_codigo_from_sec_codigo(sec_codigo=self.get_sec_id())
            datospago = cobrodao.get_calculo_pago(lectoids=body['lectos'], alm_codigo=alm_codigo,
                                                  tdv_codigo=self.get_tdv_codigo(), sec_codigo=self.get_sec_id())
            return self.res200({'datospago': datospago})
