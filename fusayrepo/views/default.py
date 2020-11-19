from random import random

from pyramid.response import FileResponse
from pyramid.view import view_config

from fusayrepo.logica.mipixel.pixel_dao import MiPixelDao


@view_config(route_name='home', renderer='../templates/indexf.jinja2')
def my_view(request):
    aleatorio = str(random())
    return {'version': 1.0, 'vscss': aleatorio}

    """
    try:
        query = request.dbsession.query(models.MyModel)
        one = query.filter(models.MyModel.name == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'fusay'}
    """


@view_config(route_name='postfile', renderer='json', request_method='POST')
def post_file(request):
    print('Inicia procesamiento de la peticion:')

    return {'estado': 200, 'msg': 'procesado'}


@view_config(route_name='getlogopixel', request_method='GET')
def get_logo(request):
    esquema = 'fusay'
    request.dbsession.execute("SET search_path TO {0}".format(esquema))
    pixeldao = MiPixelDao(request.dbsession)
    pxid = request.params['pxid']
    pixel = pixeldao.buscar(px_id=pxid)
    if pixel is not None:
        pixel['px_id']
        px_pathlogo = pixel['px_pathlogo']
        px_tipo = pixel['px_tipo']

        # fileutil = CargaArchivosUtil()
        # base64 = fileutil.get_base64_from_file(px_pathlogo, px_tipo)
        response = FileResponse(px_pathlogo, content_type=px_tipo)
        return response


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for descriptions and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
