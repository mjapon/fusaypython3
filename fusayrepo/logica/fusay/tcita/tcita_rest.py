# coding: utf-8
"""
Fecha de creacion 12/14/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tcita.tcita_dao import TCitaDao
from fusayrepo.logica.fusay.tcita.tcita_logic import TCitaLogic
from fusayrepo.logica.fusay.tpersona.tpersoncitadao import TPersonCitaDao
from fusayrepo.logica.fusay.ttipocita.ttipocita_dao import TTipoCitaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tcita', path='/api/tcita/{ct_id}', cors_origins=('*',))
class TCitaRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tcitadao = TCitaDao(self.dbsession)
        if accion == 'form':
            tcitalogic = TCitaLogic(self.request)
            return tcitalogic.get_form(tcitadao)
        elif accion == 'workhours':
            tcitalogic = TCitaLogic(self.request)
            return tcitalogic.get_working_hours(tcitadao)
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
        elif accion == 'gdatostipcita':
            tipocita = self.get_request_param('tipcita')
            tipcitadao = TTipoCitaDao(self.dbsession)
            datostipocita = tipcitadao.get_datos_tipo(tipc_id=tipocita)
            return self.res200({'dtipcita': datostipocita})

    def collection_post(self):
        accion = self.get_request_param('accion')
        tcitadao = TCitaDao(self.dbsession)
        if accion == 'guardar':
            tcitalogic = TCitaLogic(self.request)
            return tcitalogic.do_save(userid=self.get_user_id(), tcitadao=tcitadao)
        elif accion == 'anular':
            cod = self.get_request_param('cod')
            tcitadao.anular(ct_id=cod)
            return {'status': 200, 'msg': 'Cita anulada exitósamente'}
