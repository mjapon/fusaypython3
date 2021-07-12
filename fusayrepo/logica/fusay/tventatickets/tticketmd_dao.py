# coding: utf-8
"""
Fecha de creacion 9/14/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTicketMcDao(BaseDao):

    def get_datos_mc(self, sec_codigo):
        sql = "select tkm_cta_debe, tkm_cta_haber, tkm_artcod from tticketmc where tkm_sec_codigo = {0}".format(
            sec_codigo)

        tupla_desc = ('tkm_cta_debe', 'tkm_cta_haber', 'tkm_artcod')
        return self.first(sql, tupla_desc)
