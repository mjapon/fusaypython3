# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todontograma.todontograma_model import TOdontograma

log = logging.getLogger(__name__)


class TOdontogramaDao(BaseDao):

    def get_form(self):
        return {
            'od_id': 0,
            'od_tipo': 1,
            'od_protesis': '',
            'od_odontograma': '',
            'od_obsodonto': '',
            'pac_id': 0
        }

    def crear(self, user_crea, pac_id, od_tipo, od_odontograma, od_obs, od_protesis):
        todontograma = TOdontograma()
        todontograma.od_fechacrea = datetime.datetime.now()
        todontograma.user_crea = user_crea
        todontograma.od_odontograma = od_odontograma
        todontograma.od_obsodonto = od_obs
        todontograma.od_tipo = od_tipo
        todontograma.od_protesis = od_protesis
        todontograma.pac_id = pac_id
        self.dbsession.add(todontograma)
        self.dbsession.flush()
        return todontograma.od_id

    def actualizar(self, od_id, user_upd, od_odontograma, od_obs, od_protesis):
        todontograma = self.dbsession.query(TOdontograma).filter(TOdontograma.od_id == od_id).first()
        if todontograma is not None:
            todontograma.user_upd = user_upd
            todontograma.od_fechaupd = datetime.datetime.now()
            todontograma.od_protesis = od_protesis
            todontograma.od_odontograma = od_odontograma
            todontograma.od_obsodonto = od_obs
            self.dbsession.add(todontograma)

    def get_odontograma(self, od_id):
        sql = """select od_id, od_fechacrea, od_fechaupd, user_crea, od_odontograma, 
        od_obsodonto, od_tipo, od_protesis, pac_id from todontograma where od_id = {0}""".format(od_id)
        tupla_desc = ('od_id', 'od_fechacrea', 'od_fechaupd', 'user_crea', 'od_odontograma',
                      'od_obsodonto', 'od_tipo', 'od_protesis', 'pac_id')
        return self.first(sql, tupla_desc)

    def get_odontograma(self, pac_id, tipo):
        sql = """select od_id, od_fechacrea, od_fechaupd, user_crea, od_odontograma, 
                od_obsodonto, od_tipo, od_protesis, pac_id from todontograma where pac_id = {0} and od_tipo = {1}""".format(
            pac_id, tipo)
        tupla_desc = ('od_id', 'od_fechacrea', 'od_fechaupd', 'user_crea', 'od_odontograma',
                      'od_obsodonto', 'od_tipo', 'od_protesis', 'pac_id')
        return self.first(sql, tupla_desc)

    def get_last_odontograma(self, pac_id):
        sql = "select od_odontograma, od_tipo from todontograma where pac_id={0} and od_tipo in (1,2) order by od_id desc limit 2".format(
            pac_id)
        res = self.all(sql, ('od_odontograma', 'od_tipo'))
        resdict = {}
        for item in res:
            resdict[item['od_tipo']] = item['od_odontograma']

        return resdict
