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
from fusayrepo.utils.archivos import CargaArchivosUtil

log = logging.getLogger(__name__)


class TAdjuntoDao(BaseDao):

    def get_form(self):
        """
        Retorna formulario para creacion de un adjunto
        """
        return {
            'adj_id': 0,
            'adj_ruta': '',
            'adj_ext': '',
            'adj_nombre': '',
            'adj_filename': ''
        }

    def crear(self, form, user_crea, file):
        tparamsdao = TParamsDao(self.dbsession)
        rutaraiz = tparamsdao.get_param_value('rutaRaizAdjuntos')
        filename = form['adj_filename']
        current_date = datetime.datetime.now()

        rutafolder = '{0}/{1}/{2}/{3}'.format(rutaraiz, current_date.year, current_date.month, current_date.day)
        if not os.path.exists(rutafolder):
            os.makedirs(rutafolder)
        rutasave = '{0}/{1}'.format(rutafolder, filename)

        upload_file_util = CargaArchivosUtil()
        resdecodedfile = upload_file_util.get_decoded_file_data_type(file)

        upload_file_util.save_bytarray(rutasave, resdecodedfile['decoded'])

        tadjunto = TAdjunto()

        tadjunto.adj_ruta = rutasave
        tadjunto.adj_ext = resdecodedfile['data_type']
        tadjunto.adj_usercrea = user_crea
        tadjunto.adj_fechacrea = datetime.datetime.now()
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
