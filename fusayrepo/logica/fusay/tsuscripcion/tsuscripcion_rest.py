# coding: utf-8
"""
Fecha de creacion 1/22/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tsuscripcion.tsuscripcion_dao import TSuscripcionDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tsuscripcion', path='/api/tsuscripcion/{sus_id}', cors_origins=('*',))
class TSuscripcionRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        tsuscripdao = TSuscripcionDao(self.dbsession)
        if accion == 'form':
            codref = self.get_request_param('ref')
            form = tsuscripdao.get_form(codref)
            return self.res200({'form': form})
        elif accion == 'listbyref':
            per_id = self.get_request_param('ref')
            suscripciones = tsuscripdao.listar_suscripciones_byref(per_id=per_id)
            return self.res200({'items': suscripciones})
        elif accion == 'gdet':
            susid = self.get_request_param('suscod')
            detsuscrip = tsuscripdao.get_detalles_suscrip(sus_id=susid)
            return self.res200({'suscripcion': detsuscrip})

    def collection_post(self):
        accion = self.get_rqpa()
        tsuscripdao = TSuscripcionDao(self.dbsession)
        if accion == 'crea':
            tsuscripdao.crear(form=self.get_json_body(), user_crea=self.get_user_id())
            return self.res200({'msg': 'Suscripcion registrada exitosamente'})
        elif accion == 'cambiarestado':
            form = self.get_json_body()
            tsuscripdao.cambiar_estado(sus_id=form['sus_id'], nuevo_estado=form['estado'],
                                       user_upd=self.get_user_id())
            return self.res200({'msg': 'Actualizado exitosamente'})
