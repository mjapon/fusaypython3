# coding: utf-8
"""
Fecha de creacion 10/30/20
@autor: mjapon
"""
import logging
from datetime import datetime
from functools import reduce

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc, PixelUsadoExc
from fusayrepo.logica.mipixel.pixel_model import MiPixelModel
from fusayrepo.utils import cadenas, fechas

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

        hoy = datetime.now()
        mipixel.px_email = email
        mipixel.px_row = row
        mipixel.px_row_end = row_end
        mipixel.px_col = col
        mipixel.px_col_end = col_end
        mipixel.px_costo = costo
        mipixel.px_pathlogo = pathlogo
        mipixel.px_estado = estado
        mipixel.px_fecharegistro = hoy
        mipixel.px_tipo = tipo
        mipixel.px_url = pxurl
        mipixel.px_numpx = pxnumpx
        mipixel.px_texto = cadenas.strip(detalle)
        mipixel.px_fechacadu = fechas.sumar_meses(hoy, 12)

        if self.chk_pixel_usado(col=col, col_end=col_end, row=row, row_end=row_end):
            raise PixelUsadoExc('Algun pixel seleccionado ya fue comprado, favor seleccionar otra area')

        self.dbsession.add(mipixel)
        self.dbsession.flush()

        return mipixel.px_id

    def is_pixel_usado(self, pixelitem, newpixel):
        pxrw_start = pixelitem['rw_start']
        pxrw_end = pixelitem['rw_end']
        pxcl_start = pixelitem['cl_start']
        pxcl_end = pixelitem['cl_end']

        rw_start = newpixel['rw_start']
        rw_end = newpixel['rw_end']
        cl_start = newpixel['cl_start']
        cl_end = newpixel['cl_end']

        pixselusado = False
        pixelscomprados = {}

        for r in range(pxrw_start, pxrw_end + 1):
            for c in range(pxcl_start, pxcl_end + 1):
                pixelscomprados['{0},{1}'.format(r, c)] = True

        for r in range(rw_start, rw_end + 1):
            for c in range(cl_start, cl_end + 1):
                chkpixel = '{0},{1}'.format(r, c)
                pixselusado = chkpixel in pixelscomprados.keys()
                if pixselusado:
                    break
            else:
                continue
            break

        return pixselusado

    def chk_pixel_usado(self, col, col_end, row, row_end):
        sql = "select px_id, px_email, px_row, px_row_end, px_col, px_col_end from tpixel where px_estado in (0,2)"
        tupla_desc = ('px_id', 'px_email', 'px_row', 'px_row_end', 'px_col', 'px_col_end')

        res = self.all(sql, tupla_desc)

        it_col_start = col if col < col_end else col_end
        it_col_end = col_end if col_end > col else col
        it_row_start = row if row < row_end else row_end
        it_row_end = row_end if row_end > row else row

        usado = False
        for item in res:
            px_row = item['px_row']
            px_row_end = item['px_row_end']
            px_col = item['px_col']
            px_col_end = item['px_col_end']

            aux_row_start = px_row if px_row < px_row_end else px_row_end
            aux_row_end = px_row_end if px_row_end > px_row else px_row
            aux_col_start = px_col if px_col < px_col_end else px_col_end
            aux_col_end = px_col_end if px_col_end > px_col else px_col

            usado = self.is_pixel_usado(pixelitem={'rw_start': aux_row_start,
                                                   'rw_end': aux_row_end,
                                                   'cl_start': aux_col_start,
                                                   'cl_end': aux_col_end},
                                        newpixel={'rw_start': it_row_start,
                                                  'rw_end': it_row_end,
                                                  'cl_start': it_col_start,
                                                  'cl_end': it_col_end})
            if usado:
                break

        return usado

    def listar(self, estado):
        sql = """select px_id, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, 
        px_tipo, px_url, px_estado, case px_estado  when 0 then 'PENDIENTE'
                                                    when 1 then 'ANULADO'
                                                    when 2 then 'CONFIRMADO'
                                                    else 'DESCONOCIDO' end as estado, px_texto, px_fechacadu 
                 from tpixel where px_estado ={estado} order by px_id desc""".format(estado=estado)
        tupla_desc = (
            'px_id', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo', 'px_url',
            'px_estado', 'estado', 'px_texto', 'px_fechacadu')

        return self.all(sql, tupla_desc)

    def listar_no_anulados(self):
        status_anulado = 1
        sql = """select px_id, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, 
                px_tipo, px_url, px_estado, case px_estado  when 0 then 'PENDIENTE'
                                                            when 1 then 'ANULADO'
                                                            when 2 then 'CONFIRMADO'
                                                            else 'DESCONOCIDO' end as estado, px_texto, px_fechacadu 
                         from tpixel where px_estado !={estado} order by px_id desc""".format(estado=status_anulado)
        tupla_desc = (
            'px_id', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo', 'px_url',
            'px_estado', 'estado', 'px_texto', 'px_fechacadu')

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
                                                            px_texto, px_fechacadu
                         from tpixel order by px_id desc"""
        tupla_desc = (
            'px_id', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo', 'px_url',
            'px_estado', 'estado', 'px_fecharegistro', 'px_fechanula', 'px_fechaconfirma', 'px_numpx', 'px_texto',
            'px_fechacadu')

        return self.all(sql, tupla_desc)

    def sumar_confirmados(self, items):
        sumar = lambda x, y: x + y
        total = reduce(sumar, map(lambda x: x['px_costo'], filter(lambda x: x['px_estado'] == 2, items)), 0)
        return round(total, 2)

    def buscar(self, px_id):
        sql = """select px_id, px_numpx, px_email, px_row, px_col, px_row_end, px_col_end, px_costo, px_pathlogo, px_tipo, 
        px_url, px_estado, px_fechacadu, px_fechanula, px_obsanula, px_fechaconfirma, px_obsconfirma, px_fecharegistro,
        case px_estado  when 0 then 'PENDIENTE'
                                                            when 1 then 'ANULADO'
                                                            when 2 then 'CONFIRMADO'
                                                            else 'DESCONOCIDO' end as estado  
        from tpixel where px_id = {0}""".format(px_id)

        tupla_desc = (
            'px_id', 'px_numpx', 'px_email', 'px_row', 'px_col', 'px_row_end', 'px_col_end', 'px_costo', 'px_pathlogo',
            'px_tipo', 'px_url', 'px_estado', 'px_fechacadu', 'px_fechanula', 'px_obsanula', 'px_fechaconfirma',
            'px_obsconfirma', 'px_fecharegistro', 'estado')

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
            pixelmodel.px_fechacadu = fechas.sumar_meses(datetime.now(), 12)
