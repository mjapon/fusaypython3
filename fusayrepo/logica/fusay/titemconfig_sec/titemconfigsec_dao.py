# coding: utf-8
"""
Fecha de creacion 1/17/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.titemconfig_sec.titemconfigsec_model import TItemConfigSec

log = logging.getLogger(__name__)


class TItemConfigSecDao(BaseDao):

    def existe(self, ic_id, sec_id):
        sql = "select count(*) as cuenta from titemconfig_sec where ic_id = {0} and sec_id={1}".format(ic_id, sec_id)
        return self.first_col(sql, 'cuenta') > 0

    def find_byid(self, ics_id):
        return self.dbsession.query(TItemConfigSec).filter(TItemConfigSec.ics_id == ics_id).first()

    def clear_all(self, ic_id):
        sql = "select ics_id from titemconfig_sec where ic_id = {0}".format(ic_id)
        items = self.all(sql, ('ics_id',))
        for item in items:
            dbentity = self.find_byid(item['ics_id'])
            if dbentity is not None:
                self.dbsession.delete(dbentity)

    def crear(self, ic_id, sec_id):
        if not self.existe(ic_id, sec_id):
            titemconfigsec = TItemConfigSec()
            titemconfigsec.ic_id = ic_id
            titemconfigsec.sec_id = sec_id
            self.dbsession.add(titemconfigsec)

    def list_for_edit(self, ic_id):
        sql = """
        select a.sec_id, a.sec_nombre, b.alm_codigo, b.alm_nomcomercial, b.alm_razsoc,
                coalesce(ics.ics_id, 0) as ics_id 
        from tseccion a join talmacen b on a.alm_codigo = b.alm_codigo
        left join titemconfig_sec ics on ics.sec_id = a.sec_id and ics.ic_id ={0} 
          where  sec_estado = 1 order by sec_id
        """.format(ic_id)

        tupla_desc = ('sec_id', 'sec_nombre', 'alm_codigo', 'alm_nomcomercial', 'alm_razsoc', 'ics_id')
        secsforedit = self.all(sql, tupla_desc)

        for itsec in secsforedit:
            itsec['marca'] = itsec['ics_id'] > 0

        return secsforedit

    def create_from_list(self, ic_id, secs_list):
        self.clear_all(ic_id=ic_id)
        for item in secs_list:
            self.crear(ic_id, item['sec_id'])
