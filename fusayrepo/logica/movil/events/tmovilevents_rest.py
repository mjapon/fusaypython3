# coding: utf-8
from cornice.resource import resource

from fusayrepo.logica.fusay.tcita.tcita_dao import TCitaDao
from fusayrepo.logica.fusay.tcita.tcita_logic import TCitaLogic
from fusayrepo.utils.pyramidutil import TokenMovilView


@resource(collection_path='/api/movil/tcita', path='/api/movil/tcita/{ct_id}', cors_origins=('*',))
class TMovilEventsRest(TokenMovilView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tcitadao = TCitaDao(self.dbsession)
        if 'form' == accion:
            tcitalogic = TCitaLogic(self.request)
            return tcitalogic.get_form(tcitadao=tcitadao)

    def collection_post(self):
        form = self.get_request_json_body()
        accion = form['accion']
        tcitadao = TCitaDao(self.dbsession)
        if accion == 'lstw':
            desde = form['desde']
            hasta = form['hasta']
            tipo = form['tipo']
            citas = tcitadao.listar_validos(desde, hasta, tipo)
            return {'status': 200, 'citas': citas}
        elif accion == 'getinfocalendar':
            calendar_data = tcitadao.get_user_calendar_data(us_email=self.user_email)
            return {'status': 200, 'caluserdata': calendar_data}
        elif accion == 'guardar':
            tcitalogic = TCitaLogic(self.request)
            return tcitalogic.do_save(userid=self.get_user_id(), tcitadao=tcitadao)
        elif accion == 'anular':
            cod = self.get_request_param('cod')
            tcitadao.anular(ct_id=cod)
            return {'status': 200, 'msg': 'Cita anulada exitosamente'}
