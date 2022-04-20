# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_model import TFinAdjunto
from fusayrepo.logica.fusay.tadjunto.tadjunto_dao import TAdjuntoDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TFinAdjuntoCredDao(BaseDao):

    def get_form(self, cre_id):
        return {
            'nombre': '',
            'obs': '',
            'adj_filename': '',
            'cre_id': cre_id
        }

    def crear(self, form, user_crea):
        adjunto = TFinAdjunto()

        archivo = form['archivo']
        if archivo is None:
            raise ErrorValidacionExc("Debe cargar el adjunto")

        if not cadenas.es_nonulo_novacio(form['nombre']):
            raise ErrorValidacionExc("Debe ingresar el nombre del adjunto")

        adjunto.cre_id = form['cre_id']
        adjunto.user_crea = user_crea
        adjunto.fadj_nombre = form['nombre']
        adjunto.fadj_obs = form['obs']
        adjunto.fadj_fechacrea = datetime.datetime.now()

        adjuntodao = TAdjuntoDao(self.dbsession)
        formfile = {'adj_filename': form['adj_filename']}
        adj_id = adjuntodao.crear(formfile, user_crea, archivo)
        adjunto.adj_id = adj_id

        self.dbsession.add(adjunto)

    def listar(self, cre_id):
        sql = """
        select fadj.fadj_fechacrea, fadj.fadj_id, fadj.adj_id, fadj.cre_id, fadj.fadj_nombre, fadj.fadj_obs,
        adj.adj_filename 
        from tfin_adjuntos fadj
        join tadjunto adj on fadj.adj_id = adj.adj_id
        where fadj.cre_id = {0} order by fadj.fadj_nombre
        """.format(cre_id)

        tupla_desc = ('fadj_fechacrea', 'fadj_id', 'adj_id', 'cre_id', 'fadj_nombre', 'fadj_obs', 'adj_filename')

        return self.all(sql, tupla_desc)

