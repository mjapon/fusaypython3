# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_dao import TFinMovimientosDao
from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_service import TFinMovimientosService
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
            limit = self.get_request_param('limit')
            first = self.get_request_param('page')
            gridmovs = movsdao.listar(cue_id=cta, desde=desde, hasta=hasta, limit=limit, first=first)
            return self.res200({'gmovs': gridmovs})

    def collection_post(self):
        movsdao = TFinMovimientosDao(self.dbsession)
        accion = self.get_rqpa()
        if accion == 'crea':
            form = self.get_json_body()
            mov_id = movsdao.crear(form=form, user_crea=self.get_user_id())
            movsservice = TFinMovimientosService(self.dbsession)
            trn_codgen = movsservice.generar_asiento(mov_id=mov_id, sec_codigo=self.get_sec_id(),
                                                     usercrea=self.get_user_id())
            if trn_codgen is not None:
                movsdao.update_trn_codigo(mov_id=mov_id, trn_codigo=trn_codgen)
            msg = "Registro exitoso"
            return self.res200({'msg': msg})
