# coding: utf-8
"""
Fecha de creacion 10/10/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.fusay.tpermiso.tpermiso_dao import TPermisoDao
from fusayrepo.logica.fusay.trol.trol_dao import TRolDao
from fusayrepo.utils.pyramidutil import TokenView
from cornice.resource import resource

log = logging.getLogger(__name__)


@resource(collection_path='/api/trol', path='/api/trol/{rl_id}', cors_origins=('*',))
class TRolRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        troldao = TRolDao(self.dbsession)
        if accion == 'listar':
            roles = troldao.listargrid()
            return {'status': 200, 'items': roles}
        elif accion == 'form':
            form = troldao.get_form_crea()
            tpermisodao = TPermisoDao(self.dbsession)
            permisos = tpermisodao.listar()
            return {'status': 200, 'form': form, 'permisos': permisos}
        elif accion == 'listafu':  # listar for users
            roles = troldao.listar()
            return {'status': 200, 'items': roles}

    def get(self):
        rl_id = self.get_request_matchdict('rl_id')
        troldao = TRolDao(self.dbsession)
        form_edita = troldao.get_form_edita(rl_id=rl_id)
        return {'status': 200, 'form': form_edita}

    def collection_post(self):
        accion = self.get_request_param('accion')
        troldao = TRolDao(self.dbsession)
        if accion == 'crear':
            rform = self.get_request_json_body()
            form = rform['form']
            if int(form['rl_id']) == 0:
                troldao.crear(form, form['permisos'], self.get_user_id())
                return {'status': 200, 'msg': 'Registrado satisfactoriamente'}
            else:
                troldao.editar(form=form, permisos=form['permisos'])
                return {'status': 200, 'msg': 'Actualizado satisfactoriamente'}
        elif accion == 'editar':
            rform = self.get_request_json_body()
            form = rform['form']
            troldao.editar(form=form, permisos=form['permisos'])
            return {'status': 200, 'msg': 'Actualizado satisfactoriamente'}
        elif accion == 'anular':
            form = self.get_request_json_body()
            troldao.anular(rl_id=form['rl_id'])
            return {'status': 200, 'msg': 'Rol anulado exitosamente'}
