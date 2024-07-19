# coding: utf-8
from fusayrepo.logica.fusay.tcita.tcita_dao import TCitaDao
from fusayrepo.utils.pyramidutil import TokenMovilView
from cornice.resource import resource


@resource(collection_path='/api/movil/tcita', path='/api/movil/tcita/{ct_id}', cors_origins=('*',))
class TMovilEventsRest(TokenMovilView):

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
