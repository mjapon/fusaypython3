# coding: utf-8
"""
Fecha de creacion 
@autor: 
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tlugar.tlugar_model import TLugar
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TLugarDao(BaseDao):

    def listar(self):
        sql = u"""
        select lug_id, lug_nombre, lug_parent from public.tlugar order by lug_nombre asc
        """
        tupla_desc = ('lug_id', 'lug_nombre', 'lug_parent')
        return self.all(sql, tupla_desc)

    def existe_lug_nombre(self, lug_nombre):
        lug_nombre_upper = cadenas.strip_upper(lug_nombre)
        sql = u"select count(*) as cuenta from public.tlugar where lug_nombre =='{0}'".format(lug_nombre_upper)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, lug_nombre, lug_parent=None):
        if not cadenas.es_nonulo_novacio(lug_nombre) or len(cadenas.strip(lug_nombre)) <= 2:
            raise ErrorValidacionExc('Debe ingresar el nombre de la ubicación')
        if self.existe(lug_nombre):
            raise ErrorValidacionExc('La ubicación {0} ya esta registrado'.format(lug_nombre))

        tlugar = TLugar()
        tlugar.lug_nombre = cadenas.strip_upper(lug_nombre)
        tlugar.lug_parent = lug_parent
        tlugar.lug_status = 1

        self.dbsession.add(tlugar)

    def actualizar(self, lug_id, lug_nombre):
        if not cadenas.es_nonulo_novacio(lug_nombre) or len(cadenas.strip(lug_nombre)) <= 2:
            raise ErrorValidacionExc(u"Se debe ingresar el nombre del lugar que desea actualizar")
        tlugar = self.dbsession.query(TLugar).filter(TLugar.lug_id == lug_id).first()
        if tlugar is not None:
            lug_nombre_upper = cadenas.strip_upper(lug_nombre)
            if tlugar.lug_nombre != lug_nombre_upper:
                if self.existe_lug_nombre(lug_nombre_upper):
                    raise ErrorValidacionExc(
                        u"El lugar {0} ya esta registrado, no es actualizar este registro".format(lug_nombre_upper))
                else:
                    tlugar.lug_nombre = lug_nombre_upper
                    self.dbsession.add(tlugar)

    def dar_de_baja(self, lug_id):
        tlugar = self.dbsession.query(TLugar).filter(TLugar.lug_id == lug_id).first()
        if tlugar is not None:
            tlugar.lug_status = 2
            self.dbsession.add(tlugar)

    def listar_activos(self):
        sql = """
                select lug_id, lug_nombre from public.tlugar where lug_status = 1 order by lug_nombre asc
                """
        tupla_desc = ('lug_id', 'lug_nombre')
        return self.all(sql, tupla_desc)

    def existe(self, lug_nombre):
        sql = "select count(*) as cuenta from public.tlugar where lug_nombre = '{0}'".format(
            cadenas.strip_upper(lug_nombre))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def editar(self, lug_id, nlug_nombre):
        pass
