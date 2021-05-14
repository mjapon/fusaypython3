# coding: utf-8
"""
Fecha de creacion 5/11/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_contrato.tagp_contrato_dao import TAgpContratoDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagpcontrato', path='/api/tagpcontrato/{cna_id}', cors_origins=('*',))
class TagpContratoRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()

        tagpcontratodao = TAgpContratoDao(self.dbsession)
        if accion == 'form':
            # tipo = self.get_request_param('tipo')
            form = tagpcontratodao.get_form_anterior()
            return self.res200({'form': form})
        elif accion == 'gbyref':
            per_codigo = self.get_request_param('codref')
            items = tagpcontratodao.find_by_per_codigo(per_codigo=per_codigo)
            return self.res200({'items': items})

    def collection_post(self):
        accion = self.get_rqpa()
        tagpcontratodao = TAgpContratoDao(self.dbsession)
        if accion == 'crea':
            body = self.get_json_body()
            cna_id = tagpcontratodao.crear(form=body['form'], formref=body['formref'], formed=body['formmed'],
                                           usercrea=self.get_user_id())
            msg = 'Registro exitoso'
            return self.res200({'msg': msg, 'cna_id': cna_id})
