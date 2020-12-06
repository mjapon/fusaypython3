# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todontograma.todontograma_dao import TOdontogramaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/todontograma', path='/api/todontograma/{od_id}', cors_origins=('*',))
class TOdontogramaRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        odon_dao = TOdontogramaDao(self.dbsession)
        if accion == 'form':
            pac_id = self.get_request_param('pac')
            tipo = self.get_request_param('tipo')  # 1 permante, 2 temporal
            datosodon = odon_dao.get_odontograma(pac_id=pac_id, tipo=tipo)
            form = odon_dao.get_form()
            form['od_tipo'] = int(tipo)
            form['pac_id'] = pac_id
            if datosodon is not None:
                form['od_id'] = datosodon['od_id']
                form['od_protesis'] = datosodon['od_protesis']
                form['od_odontograma'] = datosodon['od_odontograma']
                form['od_fechacrea'] = datosodon['od_fechacrea']
                form['od_fechaupd'] = datosodon['od_fechaupd']
                form['od_obsodonto'] = datosodon['od_obsodonto']
                form['pac_id'] = datosodon['pac_id']

            return {'status': 200, 'form': form}
        elif accion == 'getodon':
            pac_id = self.get_request_param('pac')
            tipo = self.get_request_param('tipo')  # 1 permante, 2 temporal
            datosodon = odon_dao.get_odontograma(pac_id=pac_id, tipo=tipo)
            status = 200
            if datosodon is None:
                status = 404
            return {'statos': status, 'datosodon': datosodon}

    def collection_post(self):
        odon_dao = TOdontogramaDao(self.dbsession)
        form = self.get_json_body()
        od_id = int(form['od_id'])
        msg = 'Registrado exitosamente'
        if od_id == 0:
            od_id = odon_dao.crear(user_crea=self.get_user_id(),
                                   pac_id=form['pac_id'],
                                   od_tipo=form['od_tipo'],
                                   od_odontograma=form['od_odontograma'],
                                   od_obs=form['od_obs'],
                                   od_protesis=form['od_protesis'])
        else:
            odon_dao.actualizar(od_id=od_id, user_upd=self.get_user_id(),
                                od_odontograma=form['od_odontograma'],
                                od_obs=form['od_obs'],
                                od_protesis=form['od_protesis'])
            msg = 'Actualizado exitosamente'

        return {'status': 200, 'msg': msg, 'od_id': od_id}
