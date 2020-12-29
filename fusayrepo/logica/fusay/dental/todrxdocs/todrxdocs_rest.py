# coding: utf-8
"""
Fecha de creacion 12/24/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todrxdocs.todrxdocs_dao import TOdRxDocsDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/todrxdocs', path='/api/todrxdocs/{rxd_id}', cors_origins=('*',))
class TodRxDocsRest(TokenView):

    def collection_get(self):
        accion = self.grqpa()
        rxdocsdao = TOdRxDocsDao(self.dbsession)
        if accion == 'form':
            pac_id = self.get_request_param('pac_id')
            tipo = self.get_request_param('tipo')
            form = rxdocsdao.get_form(pac_id, tipo)
            return self.res200({'form': form})
        elif accion == 'listar':
            pac_id = self.get_request_param('pac_id')
            tipo = self.get_request_param('tipo')
            docs = rxdocsdao.listar(pac_id, tipo)
            return self.res200({'docs': docs})

    def collection_post(self):
        accion = self.grqpa()
        rxdocsdao = TOdRxDocsDao(self.dbsession)
        jsonbody = self.get_request_json_body()
        if accion == 'crear':
            rxdocsdao.crear(form=jsonbody['form'], user_crea=self.get_user_id(), file=jsonbody['archivo'])
            msg = 'Registrado exitosamente'
            return self.res200({'msg': msg})
        elif accion == 'editar':
            rxdocsdao.editar(form=jsonbody['form'])
            return self.res200({'msg': 'Actualizado exitosamente'})
        elif accion == 'borrar':
            rxdocsdao.eliminar(rxd_id=self.get_request_json_body()['cod'])
            return self.res200({'msg': 'Documento eliminado exitosamente'})
