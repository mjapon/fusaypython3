# coding: utf-8
"""
Fecha de creacion 12/23/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todrecetas.todrecetas_dao import TOdRecetasDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/treceta', path='/api/treceta/{rec_id}', cors_origins=('*',))
class TodRecetasRest(TokenView):

    def collection_get(self):
        accion = self.grqpa()
        recetadao = TOdRecetasDao(self.dbsession)
        if accion == 'form':
            form = recetadao.get_form()
            return self.res200({'form': form})
        elif accion == 'listar':
            pac_id = self.get_request_param('pac')
            items = recetadao.listar_validos(pac_id=pac_id)
            return self.res200({'items': items})

    def collection_post(self):
        accion = self.grqpa()
        recetadao = TOdRecetasDao(self.dbsession)
        if accion == 'guardar':
            form = self.get_request_json_body()
            rec_id = int(form['rec_id'])
            msg = 'Registrado exitosamente'
            if rec_id == 0:
                rec_id = recetadao.crear(form=form, user_crea=self.get_user_id())
            else:
                recetadao.editar(rec_id, form, user_edita=self.get_user_id())
                msg = 'Actualizado exitosamente'

            return self.res200({'msg': msg, 'rec_id': rec_id})
        elif accion == 'anular':
            form = self.get_request_json_body()
            recetadao.anular(rec_id=form['rec_id'], user_anula=self.get_user_id())
            return self.res200({'msg': 'Anulado exitosamente'})
