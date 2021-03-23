# coding: utf-8
"""
Fecha de creacion 2/17/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tcatitemconfig.tcatitemconfig_model import TCatItemConfig
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TCatItemConfigDao(BaseDao):

    def listar(self):
        sql = """
        select c.catic_id, c.catic_nombre, coalesce(mc.mc_nombre,'') caja, coalesce(c.catic_mc, 0) catic_mc
        from tcatitemconfig c
        left join tmodelocontab mc on c.catic_mc = mc.mc_id 
        where catic_estado = 1 order by catic_id
        """
        tupla = ('catic_id', 'catic_nombre', 'caja', 'catic_mc')
        return self.all(sql, tupla)

    def get_form_crea(self):
        return {
            'catic_id': 0,
            'catic_nombre': '',
            'catic_mc': 0
        }

    def existe(self, nombre_cat):
        sql = u"select count(*) as cuenta from tcatitemconfig where catic_nombre = '{0}' and catic_estado = 1 ".format(
            cadenas.strip_upper(nombre_cat))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, nombre, caja):
        if not cadenas.es_nonulo_novacio(nombre):
            raise ErrorValidacionExc(u'Debe ingresar el nombre de la categoría')

        if self.existe(nombre):
            raise ErrorValidacionExc(u'Ya existe una categoría con el nombre {0}, ingrese otra'.format(nombre))

        tcategoria = TCatItemConfig()
        tcategoria.catic_nombre = cadenas.strip_upper(nombre)
        tcategoria.catic_estado = 1
        tcategoria.catic_mc = caja

        self.dbsession.add(tcategoria)

    def actualizar(self, catic_id, nombre, caja):
        tcatitem = self.dbsession.query(TCatItemConfig).filter(TCatItemConfig.catic_id == catic_id).first()
        if tcatitem is not None:
            catic_nombre = cadenas.strip_upper(tcatitem.catic_nombre)
            nombre_upper = cadenas.strip_upper(nombre)
            if catic_nombre != nombre_upper:
                if self.existe(nombre):
                    raise ErrorValidacionExc(u'Ya existe una categoría con el nombre {0}, ingrese otra'.format(nombre))
                else:
                    tcatitem.catic_nombre = nombre_upper
            tcatitem.catic_mc = caja
            self.dbsession.add(tcatitem)

    def anular(self, catic_id):
        tcatitem = self.dbsession.query(TCatItemConfig).filter(TCatItemConfig.catic_id == catic_id).first()
        if tcatitem is not None:
            tcatitem.catic_estado = 2
            self.dbsession.add(tcatitem)
