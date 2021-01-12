# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.talmacen.talmacen_dao import TAlmacenDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_model import TTransaccPdv

log = logging.getLogger(__name__)


class TTransaccPdvDao(BaseDao):

    def aux_get_secuencia(self, tra_codigo, tdv_codigo, sec_codigo):
        sql = """select tps_codigo,
                        tps_numsec from ttransaccpdv where
                          tra_codigo = {tra_codigo} and
                          tdv_codigo = {tdv_codigo} and
                          sec_codigo = {sec_codigo}""".format(tra_codigo=tra_codigo,
                                                              tdv_codigo=tdv_codigo,
                                                              sec_codigo=sec_codigo)

        tupla_desc = ("tps_codigo",
                      "tps_numsec")

        return self.first(sql, tupla_desc)

    def gen_secuencia(self, tps_codigo, secuencia):
        ttransaccpdv = self.dbsession.query(TTransaccPdv).filter(TTransaccPdv.tps_codigo == tps_codigo).first()
        if ttransaccpdv is None:
            raise ErrorValidacionExc(u"No existe registro en ttransaccpdv con código igual a {0}".format(tps_codigo))

        ttransaccpdv.tps_numsec = int(secuencia) + 1

    def get_estabptoemi_secuencia(self, alm_codigo, tra_codigo, tdv_codigo, sec_codigo):

        resseq = self.aux_get_secuencia(tra_codigo=tra_codigo,
                                        tdv_codigo=tdv_codigo,
                                        sec_codigo=sec_codigo)
        tdv_codigo_is_cero = False
        sec_codigo_is_cero = False
        if resseq is None:
            # Buscar con seccion igual a tdv_codigo = 0
            tdv_codigo_is_cero = True
            resseq = self.aux_get_secuencia(tra_codigo=tra_codigo,
                                            tdv_codigo=0,
                                            sec_codigo=sec_codigo)

            if resseq is None:
                # buscar solo por transaccion
                sec_codigo_is_cero = True
                resseq = self.aux_get_secuencia(tra_codigo=tra_codigo,
                                                tdv_codigo=0,
                                                sec_codigo=0)
                if resseq is None:
                    raise ErrorValidacionExc(
                        u"No esta definido registro de secuencia en ttransaccpdv para tra_codigo={0}, tdv_codigo={1}, sec_codigo={2}".format(
                            tra_codigo, tdv_codigo, sec_codigo))

        if resseq is None:
            raise ErrorValidacionExc(
                "No pude obtener el valor de la secuencia para la configuración de transacción ({0}), establecimiento({1}) y punto de emisión actual ({2})".format(
                    tra_codigo,
                    alm_codigo, tdv_codigo))

        alm_nroest = TAlmacenDao(self.dbsession).get_alm_numest(alm_codigo)

        if tdv_codigo_is_cero or sec_codigo_is_cero:
            tdv_numero = "000"
        else:
            tdv_numero = TtpdvDao(self.dbsession).get_tdv_numero(tdv_codigo)

        estab_ptoemi = "{0}{1}".format(alm_nroest, tdv_numero)

        return {
            'estabptoemi': estab_ptoemi,
            'secuencia': resseq['tps_numsec'],
            'tps_codigo': resseq['tps_codigo']
        }

    def existe_trn_compro_valido(self, tra_codigo, trn_compro):
        sql = """select count(*) as cuenta from tasiento
                  where   tra_codigo={0}
                          and trn_compro = '{1}'
                          and trn_valido = 0
                          and trn_docpen='F'""".format(tra_codigo, trn_compro)
        tupla_res = self.dbsession.query("cuenta").from_statement(sql).first()
        return tupla_res[0] > 0 if tupla_res is not None and tupla_res[0] is not None else False
