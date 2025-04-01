# coding: utf-8
"""
Fecha de creacion 12/24/20
@autor: mjapon
"""
import datetime
import logging
import os

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todrxdocs.todrxdocs_model import TOdRxDocs
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.archivos import CargaArchivosUtil

log = logging.getLogger(__name__)


class TOdRxDocsDao(BaseDao):

    @staticmethod
    def get_form(pac_id, tipo):
        return {
            'rxd_id': 0,
            'rxd_ruta': '',
            'rxd_ext': '',
            'rxd_tipo': tipo,
            'rxd_nota': '',
            'rxd_nombre': '',
            'pac_id': pac_id,
            'rxd_nropieza': 0,
            'rxd_filename': ''
        }

    def listar(self, pac_id, tipo):
        sql = """
        select rxd_id, rxd_nombre, rxd_ruta, rxd_ext, rxd_nota, pac_id, user_crea, rxd_fechacrea, rxd_nropieza, 
        rxd_tipo, rxd_estado, rxd_filename  from todrxdocs where pac_id = {0} 
        and rxd_tipo = {1} and rxd_estado = 1 order by rxd_fechacrea 
        """.format(pac_id, tipo)
        tupla_desc = (
            'rxd_id', 'rxd_nombre', 'rxd_ruta', 'rxd_ext', 'rxd_nota', 'pac_id', 'user_crea', 'rxd_fechacrea',
            'rxd_nropieza',
            'rxd_tipo',
            'rxd_estado', 'rxd_filename')

        docs = self.all(sql, tupla_desc)
        faicon = 'fa-paperclip'
        for doc in docs:
            rxd_ext = doc['rxd_ext']
            if 'image' in rxd_ext:
                faicon = 'fa-file-image'
            if 'doc' in rxd_ext:
                faicon = 'fa-file-word'
            if 'pdf' in rxd_ext:
                faicon = 'fa-file-pdf'

            doc['fa_icon'] = faicon
        return docs

    def find_bycod(self, rxd_id):
        sql = """
                select rxd_id, rxd_nombre,  rxd_ruta, rxd_ext, rxd_nota, pac_id, user_crea, rxd_fechacrea, rxd_nropieza, 
                rxd_tipo, rxd_estado, rxd_filename from todrxdocs where rxd_id = {0} 
                """.format(rxd_id)

        tupla_desc = (
            'rxd_id', 'rxd_nombre', 'rxd_ruta', 'rxd_ext', 'rxd_nota', 'pac_id', 'user_crea', 'rxd_fechacrea',
            'rxd_nropieza',
            'rxd_tipo',
            'rxd_estado', 'rxd_filename')

        return self.first(sql, tupla_desc)

    def crear(self, form, user_crea, file):
        tparamsdao = TParamsDao(self.dbsession)
        rutaraiz = tparamsdao.get_param_value('rutaRaizRxDocs')
        filename = form['rxd_filename']
        pac_id = form['pac_id']
        rxd_tipo = form['rxd_tipo']
        rutafolder = '{0}/{1}/{2}'.format(rutaraiz, pac_id, rxd_tipo)
        if not os.path.exists(rutafolder):
            os.makedirs(rutafolder)
        rutasave = '{0}/{1}'.format(rutafolder, filename)

        upload_file_util = CargaArchivosUtil()
        resdecodedfile = upload_file_util.get_decoded_file_data_type(file)

        upload_file_util.save_bytarray(rutasave, resdecodedfile['decoded'])

        todrxdoc = TOdRxDocs()
        todrxdoc.rxd_ruta = rutasave
        todrxdoc.rxd_ext = resdecodedfile['data_type']
        todrxdoc.rxd_nota = form['rxd_nota']
        todrxdoc.pac_id = pac_id
        todrxdoc.user_crea = user_crea
        todrxdoc.rxd_fechacrea = datetime.datetime.now()
        todrxdoc.rxd_nropieza = int(form['rxd_nropieza'])
        todrxdoc.rxd_nombre = cadenas.strip(form['rxd_nombre'])
        todrxdoc.rxd_tipo = int(rxd_tipo)
        todrxdoc.rxd_estado = 1
        todrxdoc.rxd_filename = filename

        self.dbsession.add(todrxdoc)
        self.dbsession.flush()
        return todrxdoc.rxd_id

    def find_by_id(self, rxd_id):
        return self.dbsession.query(TOdRxDocs).filter(TOdRxDocs.rxd_id == rxd_id).first()

    def editar(self, form):
        rxd_id = form['rxd_id']
        odrxdoc = self.find_by_id(rxd_id)
        if odrxdoc is not None:
            odrxdoc.rxd_nombre = cadenas.strip(form['rxd_nombre'])
            odrxdoc.rxd_nota = cadenas.strip(form['rxd_nota'])
            self.dbsession.add(odrxdoc)

    def eliminar(self, rxd_id):
        odrxdoc = self.find_by_id(rxd_id)
        if odrxdoc is not None:
            if os.path.exists(odrxdoc.rxd_ruta):
                os.remove(odrxdoc.rxd_ruta)
            self.dbsession.delete(odrxdoc)
