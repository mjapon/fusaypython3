# coding: utf-8
"""
Fecha de creacion 12/14/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tcita.tcita_dao import TCitaDao
from fusayrepo.logica.fusay.tpersona.tpersoncitadao import TPersonCitaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tcita', path='/api/tcita/{ct_id}', cors_origins=('*',))
class TCitaRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tcitadao = TCitaDao(self.dbsession)
        if accion == 'form':
            pac_id = self.get_request_param('pac')
            form = tcitadao.get_form(pac_id=pac_id)
            horas = tcitadao.get_horas_for_form()
            colores = tcitadao.get_lista_colores()
            return {'status': 200, 'form': form, 'horas': horas, 'colores': colores}
        elif accion == 'lstw':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            tipo = self.get_request_param('tipo')
            citas = tcitadao.listar_validos(desde, hasta, tipo)
            return {'status': 200, 'citas': citas}
        elif accion == 'countm':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            tipo = self.get_request_param('tipo')
            citas = tcitadao.contar_validos(desde, hasta, tipo)
            return {'status': 200, 'citas': citas}
        elif accion == 'gdet':
            cod = self.get_request_param('cod')
            datoscita = tcitadao.get_detalles_cita(ct_id=cod)
            return {'status': 200, 'cita': datoscita}
        elif accion == 'glastv':
            pac_id = self.get_request_param('pac')
            ct_tipo = self.get_request_param('tipo')
            lastvalid = tcitadao.get_last_valid_cita(per_id=pac_id, ct_tipo=ct_tipo)
            if lastvalid is not None:
                return {'status': 200, 'cita': lastvalid}
            else:
                return {'status': 404}
        elif accion == 'getproxvcita':
            pac_id = self.get_request_param('pac')
            ct_tipo = self.get_request_param('tipo')
            ct_fecha = self.get_request_param('fecha')
            lastvalid = tcitadao.get_prox_valid_cita(per_id=pac_id, ct_tipo=ct_tipo, ct_fecha=ct_fecha)
            if lastvalid is not None:
                return {'status': 200, 'cita': lastvalid}
            else:
                return {'status': 404}
        elif accion == 'gpercita':
            tpersoncitadao = TPersonCitaDao(self.dbsession)
            personscita = tpersoncitadao.listar()
            return self.res200({'personscita': personscita})

    def collection_post(self):
        accion = self.get_request_param('accion')
        tcitadao = TCitaDao(self.dbsession)
        if accion == 'guardar':
            form = self.get_request_json_body()
            ct_id = int(form['ct_id'])
            msg = 'Registrado exitosamente'
            if ct_id > 0:
                msg = 'Actualizado exitosamente'
                tcitadao.actualizar(form, user_edita=self.get_user_id())
            else:
                tcitadao.guardar(form, user_crea=self.get_user_id())
            return {'status': 200, 'msg': msg}
        elif accion == 'anular':
            cod = self.get_request_param('cod')
            tcitadao.anular(ct_id=cod)
            return {'status': 200, 'msg': 'Cita anulada exitosamente'}