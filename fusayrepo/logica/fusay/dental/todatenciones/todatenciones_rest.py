# coding: utf-8
"""
Fecha de creacion 12/9/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todatenciones.todatenciones_dao import TOdAtencionesDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/todatenciones', path='/api/todatenciones/{ate_id}', cors_origins=('*',))
class TodAtencionesRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        atenciones_dao = TOdAtencionesDao(self.dbsession)
        if accion == 'form':
            pac_id = self.get_request_param('pac')
            form = atenciones_dao.get_form(pac_id)
            return {'status': 200, 'form': form}
        elif accion == 'historia':
            pac_id = self.get_request_param('pac')
            historia = atenciones_dao.listar(pac_id)
            return {'status': 200, 'historia': historia}
        elif accion == 'gdet':
            ate_id = self.get_request_param('ate_id')
            res = atenciones_dao.get_detalles(ate_id=ate_id)
            return {'status': 200, 'atencion': res}

    def collection_post(self):
        accion = self.get_request_param('accion')
        atenciones_dao = TOdAtencionesDao(self.dbsession)
        if accion == 'crear':
            form = self.get_request_json_body()
            atenciones_dao.crear(form, user_crea=self.get_user_id())
            return {'status': 200, 'msg': 'Registrado existosamente'}
        elif accion == 'anular':
            form = self.get_request_json_body()
            atenciones_dao.anular(ate_id=form['ate_id'], user_anula=self.get_user_id())
            return {'status': 200, 'msg': 'Anulado existosamente'}
