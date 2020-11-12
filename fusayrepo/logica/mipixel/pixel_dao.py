# coding: utf-8
"""
Fecha de creacion 10/30/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.mipixel.pixel_model import MiPixelModel
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class MiPixelDao(BaseDao):

    def crear(self, form, pathlogo, tipo):
        mipixel = MiPixelModel()

        email = form['px_email']
        row = form['px_row']
        col = form['px_col']
        row_end = form['px_row_end']
        col_end = form['px_col_end']
        costo = form['px_costo']
        pxurl = form['px_url']
        pxnumpx = form['px_numpx']
        pathlogo = pathlogo
        estado = 0
        detalle = form['px_texto']

        if not pxurl.startswith('http'):
            pxurl = 'http://{0}'.format(pxurl)

        if not cadenas.es_nonulo_novacio(email):
            raise ErrorValidacionExc('Debe ingresar el correo del usuario')

        if not cadenas.es_nonulo_novacio(row):
            raise ErrorValidacionExc('Debe seleccionar los pixeles que desea comprar')

        if not cadenas.es_nonulo_novacio(pathlogo):
            raise ErrorValidacionExc('Por favor ingrese el path del logo')

        if not cadenas.es_nonulo_novacio(pxurl):
            raise ErrorValidacionExc('Por favor ingrese la url del pixel')

        mipixel.px_email = email
        mipixel.px_row = row
        mipixel.px_row_end = row_end
        mipixel.px_col = col
        mipixel.px_col_end = col_end
        mipixel.px_costo = costo
        mipixel.px_pathlogo = pathlogo
        mipixel.px_estado = estado
        mipixel.px_fecharegistro = datetime.now()
        mipixel.px_tipo = tipo
        mipixel.px_url = pxurl
        mipixel.px_numpx = pxnumpx
        mipixel.px_texto = cadenas.strip(detalle)

        self.dbsession.add(mipixel)
        self.dbsession.flush()

        return mipixel.px_id

    def listar(self, estado):
        sql = """select px_id, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, 
        px_tipo, px_url, px_estado, case px_estado  when 0 then 'PENDIENTE'
                                                    when 1 then 'ANULADO'
                                                    when 2 then 'CONFIRMADO'
                                                    else 'DESCONOCIDO' end as estado, px_texto 
                 from tpixel where px_estado ={estado} order by px_id desc""".format(estado=estado)
        tupla_desc = (
            'px_id', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo', 'px_url',
            'px_estado', 'estado', 'px_texto')

        return self.all(sql, tupla_desc)

    def listar_all(self):
        sql = """select px_id, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, 
                px_tipo, px_url, px_estado, case px_estado  when 0 then 'PENDIENTE'
                                                            when 1 then 'ANULADO'
                                                            when 2 then 'CONFIRMADO'
                                                            else 'DESCONOCIDO' end as estado,
                                                            px_fecharegistro,
                                                            px_fechanula,
                                                            px_fechaconfirma,
                                                            px_numpx,
                                                            px_texto
                         from tpixel order by px_id desc"""
        tupla_desc = (
            'px_id', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo', 'px_url',
            'px_estado', 'estado', 'px_fecharegistro', 'px_fechanula', 'px_fechaconfirma', 'px_numpx', 'px_texto')

        return self.all(sql, tupla_desc)

    def buscar(self, px_id):
        sql = """select px_id, px_numpx, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, px_tipo, px_url, px_estado 
        from tpixel where px_id = {0}""".format(px_id)

        tupla_desc = (
            'px_id', 'px_numpx', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo',
            'px_tipo',
            'px_url', 'px_estado')

        return self.first(sql, tupla_desc)

    def anular(self, px_id, obsanula):
        pixelmodel = self.dbsession.query(MiPixelModel).filter(MiPixelModel.px_id == px_id).first()
        if pixelmodel is not None:
            pixelmodel.px_estado = 1
            pixelmodel.px_fechanula = datetime.now()
            pixelmodel.px_obsanula = obsanula

    def confirmar(self, px_id, obs_confirma):
        pixelmodel = self.dbsession.query(MiPixelModel).filter(MiPixelModel.px_id == px_id).first()
        if pixelmodel is not None:
            pixelmodel.px_estado = 2
            pixelmodel.px_fechaconfirma = datetime.now()
            pixelmodel.px_obsconfirma = obs_confirma
