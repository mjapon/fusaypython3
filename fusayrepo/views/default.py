from random import random

from pyramid.response import FileResponse
from pyramid.view import view_config

from fusayrepo.logica.fusay.dental.todrxdocs.todrxdocs_dao import TOdRxDocsDao
from fusayrepo.logica.mipixel.pixel_dao import MiPixelDao


@view_config(route_name='home', renderer='../templates/indexf.jinja2')
def my_view(request):
    aleatorio = str(random())
    return {'version': 1.0, 'vscss': aleatorio}


@view_config(route_name='getlogopixel', request_method='GET')
def get_logo(request):
    esquema = 'fusay'
    request.dbsession.execute("SET search_path TO {0}".format(esquema))
    pixeldao = MiPixelDao(request.dbsession)
    pxid = request.params['pxid']
    pixel = pixeldao.buscar(px_id=pxid)
    if pixel is not None:
        px_pathlogo = pixel['px_pathlogo']
        px_tipo = pixel['px_tipo']
        response = FileResponse(px_pathlogo, content_type=px_tipo)
        return response


@view_config(route_name='grxdoc', request_method='GET')
def get_rxdoc(request):
    esquema = request.params['sqm']
    cod = request.params['codoc']
    request.dbsession.execute("SET search_path TO {0}".format(esquema))
    rxdosdao = TOdRxDocsDao(request.dbsession)
    datosdoc = rxdosdao.find_bycod(rxd_id=cod)
    rxd_ruta = datosdoc['rxd_ruta']
    rxd_ext = datosdoc['rxd_ext']
    rxd_filename = datosdoc['rxd_filename']
    response = FileResponse(rxd_ruta, content_type=rxd_ext)

    atach = 'inline'
    """
    atach = 'attachment'
    if 'image' in rxd_ext:
        atach = 'inline'
    """
    response.content_disposition = '{0}; filename="{1}"'.format(atach, rxd_filename)
    return response
