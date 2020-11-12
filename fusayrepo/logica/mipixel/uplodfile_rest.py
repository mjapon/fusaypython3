# coding: utf-8
"""
Fecha de creacion 10/28/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.mipixel.pixel_dao import MiPixelDao
from fusayrepo.utils.archivos import CargaArchivosUtil
from fusayrepo.utils.pyramidutil import FusayPublicView
from cornice.resource import resource

log = logging.getLogger(__name__)


@resource(collection_path='/api/public/uploadfile', path='/api/public/uploadfile/{upload_id}', cors_origins=('*',))
class UploadView(FusayPublicView):

    def collection_post(self):
        accion = self.get_request_param('accion')
        """
        if accion == 'anular':
            jsonbody = self.get_request_json_body()
            pixeldao = MiPixelDao(self.dbsession)
            pixeldao.anular(px_id=jsonbody['px_id'], obsanula=jsonbody['px_obs'])
            return {'status': 200, 'msg': 'Registro anulado exitosamente'}

        elif accion == 'confirmar':
            jsonbody = self.get_request_json_body()
            pixeldao = MiPixelDao(self.dbsession)
            pixeldao.confirmar(px_id=jsonbody['px_id'], obs_confirma=jsonbody['px_obs'])
            return {'status': 200, 'msg': 'Registro confirmado exitosamente'}
        else:
        """
        if accion == 'updatecode':
            jsonbody = self.get_request_json_body()
            nombre_archivo = jsonbody['nombre']
            param_dao = TParamsDao(self.dbsession)
            pathfolder = param_dao.get_param_value('rutaPixelLogos')
            ruta = '{0}/{1}'.format(pathfolder, nombre_archivo)
            form = jsonbody['form']
            try:
                pixeldao = MiPixelDao(self.dbsession)
                uploadFileUtil = CargaArchivosUtil()
                res = uploadFileUtil.get_decoded_file_data_type(jsonbody['archivo'])
                uploadFileUtil.save_bytarray(ruta, res['decoded'])
                px_id = pixeldao.crear(form=form, pathlogo=ruta, tipo=jsonbody['tipo'])
                estado = 200
                msg = 'Registro satisfactorio'
                return {'status': estado, 'msg': msg, 'px_id': px_id}
            except Exception as ex:
                estado = -1
                msg = '{0}'.format(ex)
                return {'status': estado, 'msg': msg}
                log.error(u'Error al tratar de guardar el trabajo de impresión: {0}'.format(ex))

    def collection_get(self):
        accion = self.get_request_param('accion')
        if accion == 'listar':
            pixeldao = MiPixelDao(self.dbsession)
            statusactivo = 2
            items = pixeldao.listar(estado=statusactivo)
            return {'status': 200, 'items': items}
        elif accion == 'listarall':
            pixeldao = MiPixelDao(self.dbsession)
            items = pixeldao.listar_all()
            return {'status': 200, 'items': items}
        elif accion == 'getpixel':
            pxid = self.get_request_param('pxid')
            pixeldao = MiPixelDao(self.dbsession)
            pixel = pixeldao.buscar(px_id=pxid)
            return {'status': 200, 'pixel': pixel}
