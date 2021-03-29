# coding: utf-8
"""
Fecha de creacion 11/16/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class TTransaccDao(BaseDao):

    def get_ttransacc(self, tra_codigo):
        sql = """
        select tra_codigo,
        tra_nombre,
        tra_obs, 
        tra_xmlsav,
        tra_tipart,
        tra_edcomp,
        tra_tipdoc,
        tra_tipoprecio,
        tra_codrep,
        tra_dupite,
        tra_preiva,
        tra_vietot,
        tra_contab,
        tra_inv,
        tra_seccion from ttransacc where tra_codigo = {0}
        """.format(tra_codigo)

        tupla_desc = ('tra_codigo',
                      'tra_nombre',
                      'tra_obs',
                      'tra_xmlsav',
                      'tra_tipart',
                      'tra_edcomp',
                      'tra_tipdoc',
                      'tra_tipoprecio',
                      'tra_codrep',
                      'tra_dupite',
                      'tra_preiva',
                      'tra_vietot',
                      'tra_contab',
                      'tra_inv',
                      'tra_seccion')

        return self.first(sql, tupla_desc)

    def listar_min(self, tra_codigos_in):
        sql = """
        select tra_codigo, tra_nombre from ttransacc where tra_codigo in ({0})
        """.format(tra_codigos_in)

        tupla_desc = ('tra_codigo', 'tra_nombre')
        return self.all(sql, tupla_desc)
