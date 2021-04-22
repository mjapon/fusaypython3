# coding: utf-8
"""
Fecha de creacion 3/7/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.utils.generatokenutil import GeneraTokenUtil
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tseccion', path='/api/tseccion/{sec_id}', cors_origins=('*',))
class TSeccionRest(TokenView):

    def collection_get(self):
        secdao = TSeccionDao(self.dbsession)
        secs = secdao.listar()
        return {'status': 200, 'items': secs}

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'setseccion':
            form = self.get_json_body()
            sec_id = form['sec_id']
            auth_token = self.request.headers['x-authtoken']
            genera_token_util = GeneraTokenUtil()

            secdao = TSeccionDao(self.dbsession)
            seccion = secdao.get_byid(sec_id)
            token = genera_token_util.update_secid_token(token=auth_token, sec_id=sec_id)

            # Se debe traer las puntos de emision para esta seccion
            ttpdvdao = TtpdvDao(self.dbsession)
            ttpdvs = ttpdvdao.listar_min_from_sec_codigo(sec_id=sec_id)
            if len(ttpdvs) == 0:
                raise ErrorValidacionExc(
                    'Esta sección({0}) no tiene puntos de emisión asociados, favor verficar'.format(sec_id))
            tdv_cod = ttpdvs[0]['tdv_codigo']
            token = genera_token_util.update_tdvcod_token(token=token, tdv_codigo=tdv_cod)

            return {'status': 200, 'token': token, 'seccion': seccion, 'tdv_codigo': tdv_cod, 'ttpdvs': ttpdvs}
