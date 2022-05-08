# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_dao import TFinMovimientosDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/fin/movs', path='/api/fin/movs/{movid}', cors_origins=('*',))
class TFinMovimientosRest(TokenView):

    def collection_get(self):
        movsdao = TFinMovimientosDao(self.dbsession)
        accion = self.get_rqpa()
        if accion == 'form':
            cuenta = self.get_request_param('cta')
            form = movsdao.get_form(cue_id=cuenta)
            return self.res200({'form': form})
        elif accion == 'listar':
            cta = self.get_request_param('cta')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            gridmovs = movsdao.listar(cue_id=cta, desde=desde, hasta=hasta)
            return self.res200({'gmovs': gridmovs})

    def collection_post(self):
        movsdao = TFinMovimientosDao(self.dbsession)
        accion = self.get_rqpa()
        if accion == 'crea':
            form = self.get_json_body()
            movsdao.crear(form=form, user_crea=self.get_user_id())
            msg = "Registro exitoso"
            return self.res200({'msg': msg})
