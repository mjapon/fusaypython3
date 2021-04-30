# coding: utf-8
"""
Fecha de creacion 4/29/21
@autor: mjapon
"""
import datetime
import logging
import os

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tadjunto.tadjunto_model import TAdjunto
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.archivos import CargaArchivosUtil

log = logging.getLogger(__name__)


class TAdjuntoDao(BaseDao):

    def get_form(self, folder_root):
        """
        Retorna formulario para creacion de un adjunto
        :param folder_root: Nombre de la carpeta que se debe crear y en donde se registrara este adjunto
        :return:
        """
        return {
            'adj_id': 0,
            'adj_ruta': '',
            'adj_ext': '',
            'adj_nombre': '',
            'adj_filename': '',
            'folder_root': folder_root
        }

    def crear(self, form, user_crea, file):
        tparamsdao = TParamsDao(self.dbsession)
        rutaraiz = tparamsdao.get_param_value('rutaRaizRxDocs')
        filename = form['adj_filename']
        froot = form['folder_root']
        # TODO: Verificar que no se repital el mismo nombre de archivo para el usuario y carpeta especifiado
        rutafolder = '{0}/{1}/{2}'.format(rutaraiz, froot, user_crea)
        if not os.path.exists(rutafolder):
            os.makedirs(rutafolder)
        rutasave = '{0}/{1}'.format(rutafolder, filename)

        uploadFileUtil = CargaArchivosUtil()
        resdecodedfile = uploadFileUtil.get_decoded_file_data_type(file)

        uploadFileUtil.save_bytarray(rutasave, resdecodedfile['decoded'])

        tadjunto = TAdjunto()

        tadjunto.adj_ruta = rutasave
        tadjunto.adj_ext = resdecodedfile['data_type']
        tadjunto.user_crea = user_crea
        tadjunto.adj_fechacrea = datetime.datetime.now()
        tadjunto.adj_nombre = cadenas.strip(form['adj_nombre'])
        tadjunto.adj_estado = 1
        tadjunto.adj_filename = filename

        self.dbsession.add(tadjunto)
        self.dbsession.flush()
        return tadjunto.adj_id

    def find_by_id(self, adj_id):
        return self.dbsession.query(TAdjunto).filter(TAdjunto.adj_id == adj_id).first()

    def eliminar(self, adj_id):
        tadjunto = self.find_by_id(adj_id)
        if tadjunto is not None:
            if os.path.exists(tadjunto.adj_ruta):
                os.remove(tadjunto.adj_ruta)
            self.dbsession.delete(tadjunto)
