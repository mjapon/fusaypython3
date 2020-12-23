# coding: utf-8
"""
Fecha de creacion 12/8/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todantencedentes.todantecedentes_dao import TOdAntecedentesDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/todantecedentes', path='/api/todantecedentes/{od_antid}', cors_origins=('*',))
class TOdAntecedentesRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        odontodao = TOdAntecedentesDao(self.dbsession)

        if accion == 'form':
            od_tipo = self.get_request_param('tipo')
            pac_id = self.get_request_param('pac_id')
            form = odontodao.get_form(od_tipo, pac_id)
            return {'status': 200, 'form': form}

        elif accion == 'historicos':
            od_tipo = self.get_request_param('tipo')
            pac_id = self.get_request_param('pac_id')
            items = odontodao.get_registros_antiguos(pac_id=pac_id, od_tipo=od_tipo)
            return {'status': 200, 'items': items}

        elif accion == 'detbyid':
            cod = self.get_request_param('cod')
            res = odontodao.get_detalles_byantid(od_antid=cod)
            return {'status': 200, 'res': res}

        elif accion == 'lastvalid':
            od_tipo = self.get_request_param('tipo')
            pac_id = self.get_request_param('pac_id')
            res = odontodao.get_valid_last(pac_id=pac_id, od_tipo=od_tipo)
            if res is not None:
                return {'status': 200, 'res': res}
            else:
                return {'status': 404}

    def collection_post(self):
        accion = self.get_request_param('accion')
        odontodao = TOdAntecedentesDao(self.dbsession)
        if accion == 'crear':
            form = self.get_request_json_body()
            odontodao.guardar(form=form, user_crea=self.get_user_id())
            return {'status': 200, 'msg': 'Registrado exitosamente'}
        elif accion == 'anular':
            jsonbody = self.get_json_body()
            odontodao.anular(od_antid=jsonbody['cod'], user_anula=self.get_user_id())
            return {'status': 200, 'msg': 'Registro anulado exitosamente'}
        elif accion == 'actualizar':
            od_antid = self.get_request_param('cod')
            jsonbody = self.get_json_body()
            odontodao.actualizar(od_antid=od_antid, form=jsonbody, user_edita=self.get_user_id())
            return {'status': 200, 'msg': 'Actualizado exitosamente'}
