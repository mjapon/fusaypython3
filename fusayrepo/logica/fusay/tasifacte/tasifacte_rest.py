# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasifacte.tasifacte_dao import TasiFacteDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasifacte', path='/api/tasifacte/{trn_codigo}', cors_origins=('*',))
class TasiFacteRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()

        asifactedato = TasiFacteDao(self.dbsession)
        tipos_estados = asifactedato.get_tipos_estados()
        form = asifactedato.get_form_buscar()

        if accion == 'form':
            return self.res200({'tipos_estados': tipos_estados, 'form': form})

    def collection_post(self):

        accion = self.get_rqpa()
        asifactedato = TasiFacteDao(self.dbsession)

        if accion == 'buscar':
            form = self.get_request_json_body()
            comprobantes = asifactedato.buscar_comprobantes(form=form)
            return self.res200({'comprobantes': comprobantes})
