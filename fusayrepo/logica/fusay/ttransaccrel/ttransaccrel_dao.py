import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.ttransaccrel.ttransaccrel_model import TTransaccRel
from fusayrepo.utils import ctes


class TTransaccRelDao(BaseDao):

    def crear_nota_credito(self, trn_cod_notacred, trn_cod_factura, usercrea):
        ttransaccrel = TTransaccRel()
        ttransaccrel.trn_codorigen = trn_cod_factura
        ttransaccrel.trn_coddestino = trn_cod_notacred
        ttransaccrel.trel_tracoddestino = ctes.TRA_COD_NOTA_CREDITO
        ttransaccrel.trel_fechacrea = datetime.datetime.now()
        ttransaccrel.trel_usercrea = usercrea
        ttransaccrel.trel_activo = True

        self.dbsession.add(ttransaccrel)

    def get_datos_notacred_for_factura(self, trn_codfact):
        sql = ("select rel.trn_coddestino, asinota.trn_compro, asinota.trn_fecreg from ttransaccrel rel "
               "join tasiento asinota on rel.trn_coddestino = asinota.trn_codigo and rel.trel_tracoddestino  = 4 "
               "and asinota.trn_valido = 0 "
               "where rel.trn_codorigen = {0} ").format(trn_codfact)
        tupla_desc = ('trn_coddestino', 'trn_compro', 'trn_fecreg')
        return self.first(sql, tupla_desc)

    def get_datos_factura_for_nota_credito(self, trn_notacred):
        sql = ("select fac.trn_compro, fac.trn_fecreg from tasiento fac "
               "join ttransaccrel rel on rel.trn_codorigen  = fac.trn_codigo and rel.trel_tracoddestino  = 4 "
               "and rel.trel_activo  = true where rel.trn_coddestino  = {0}").format(trn_notacred)

        tupla_desc = ('trn_compro', 'trn_fecreg')
        return self.first(sql, tupla_desc)
