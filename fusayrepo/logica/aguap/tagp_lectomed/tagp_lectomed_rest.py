# coding: utf-8
"""
Fecha de creacion 5/17/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_lectomed.tagp_lectomed_dao import LectoMedAguaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagplectomed', path='/api/tagplectomed/{lmd_id}', cors_origins=('*',))
class LectoMedAguaRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        lectomeddao = LectoMedAguaDao(self.dbsession)
        if accion == 'form':
            form = lectomeddao.get_form()
            return self.res200({'form': form})
        elif accion == 'last':
            numed = self.get_request_param('numed')
            lastlectomed = lectomeddao.get_last_lectomed(mdg_num=numed)
            if lastlectomed is not None:
                return self.res200({'lectomed': lastlectomed})
            else:
                return self.res404({'msg': 'No hay registro de lecturas de medidor'})
        elif accion == 'conspend':
            codmed = self.get_request_param('codmed')
            consumos = lectomeddao.get_lecturas(mdg_id=codmed)
            return self.res200(consumos)

    def collection_post(self):
        accion = self.get_rqpa()
        lectomeddao = LectoMedAguaDao(self.dbsession)
        if accion == 'crea':
            form = self.get_json_body()
            lectomeddao.crear(form=form, user_crea=self.get_user_id())
            return self.res200({'msg': 'Registrado exitósamente'})
