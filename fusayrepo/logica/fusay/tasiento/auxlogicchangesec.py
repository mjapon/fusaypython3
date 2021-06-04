from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasicredito import tasicredito_dao
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento
from fusayrepo.utils import ctes


class AuxLogigChangeSeccion(BaseDao):

    def get_datos_seccion(self, trn_codigo):
        sql = """
        select a.sec_codigo, b.sec_nombre from tasiento a 
        join tseccion b on a.sec_codigo = b.sec_id
        where a.trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('sec_codigo', 'sec_nombre')
        return self.first(sql, tupla_desc)

    def get_form_change_seccion(self, trn_codigo):
        datossec = self.get_datos_seccion(trn_codigo)
        sql = """
        select sec_id, sec_nombre from tseccion where sec_id != {0}  order by sec_nombre
        """.format(datossec['sec_codigo'])
        secciones = self.all(sql, ('sec_id', 'sec_nombre'))

        return {
            'currentsec': datossec,
            'secciones': secciones
        }

    def find_cta_codigo_prodserv(self, cta_codigo, tra_codigo, from_sec_codigo, to_sec_codigo):
        new_cta_codigo = None
        sql = """
        select mc_id, tra_codigo, cta_codigo, mcd_signo, sec_codigo from tmodelocontabdet where 
        cta_codigo = {0} and tra_codigo = {1} and sec_codigo = {2} 
        """.format(cta_codigo, tra_codigo, from_sec_codigo)

        tupla_desc = ('mc_id', 'tra_codigo', 'cta_codigo', 'mcd_signo', 'sec_codigo')
        datosctacontab = self.first(sql, tupla_desc)
        if datosctacontab is not None:
            # Modelto contable localizado para es producto, buscar si esta definido para la nueva seccion
            sql = """
            select cta_codigo from tmodelocontabdet where 
            mc_id = {0} and tra_codigo = {1} and mcd_signo = {2} and sec_codigo = {3} 
            """.format(datosctacontab['mc_id'], tra_codigo, datosctacontab['mcd_signo'], to_sec_codigo)

            new_cta_codigo = self.first_col(sql, 'cta_codigo')

        return new_cta_codigo

    def find_cta_codigo_abo(self, cta_codigo, tra_codigo, from_sec_codigo, to_sec_codigo):
        sql = """
        select tra_codigo, cta_codigo, tmc_signo from ttransaccmc where tra_codigo = {0} and cta_codigo = {1}
        and sec_codigo = {2}
        """.format(tra_codigo, cta_codigo, from_sec_codigo)

        new_cta_codigo = None
        tupla_desc = ('tra_codigo', 'cta_codigo', 'tmc_signo')
        res = self.first(sql, tupla_desc)
        if res is not None:
            tmc_signo = res['tmc_signo']
            sql = """
            select cta_codigo from ttransaccmc where tra_codigo = {0} and tmc_signo = {1} and sec_codigo = {2}
            """.format(tra_codigo, tmc_signo, to_sec_codigo)
            new_cta_codigo = self.first_col(sql, 'cta_codigo')

        return new_cta_codigo

    def find_cta_codigo_imp(self, cta_codigo, tra_codigo, from_sec_codigo, to_sec_codigo):
        sql = """
        select tra_impg, tra_signo from ttransaccimp where tra_codigo = {0} and tra_impg = {1} and sec_codigo = {2}
        """.format(tra_codigo, cta_codigo, from_sec_codigo)

        tupla = ('tra_impg', 'tra_signo')
        res = self.first(sql, tupla)
        cta_codigo_imp = None
        if res is not None:
            sql = """select tra_impg from ttransaccimp where 
            tra_codigo = {0} and tra_signo = {1} and sec_codigo = {2}""".format(tra_codigo, res['tra_signo'],
                                                                                to_sec_codigo)
            cta_codigo_imp = self.first_col(sql, 'tra_impg')

        return cta_codigo_imp

    def find_cta_codigo_pago(self, cta_codigo, tra_codigo, from_sec_codigo, to_sec_codigo):
        sql = """
        select a.ttp_signo, b.ic_clasecc from ttransaccpago a 
        join titemconfig b on a.cta_codigo = b.ic_id
        where a.tra_codigo = {0} and a.cta_codigo = {1} and a.sec_codigo = {2} 
        """.format(tra_codigo, cta_codigo, from_sec_codigo)

        tupla = ('ttp_signo', 'ic_clasecc')
        res = self.first(sql, tupla)

        cta_codigo_pago = None
        if res is not None:
            sql = """
            select a.cta_codigo, a.ttp_signo, b.ic_clasecc from ttransaccpago a 
                join titemconfig b on a.cta_codigo = b.ic_id and b.ic_clasecc = '{0}'
                where a.tra_codigo = {1} and sec_codigo = {2} and a.ttp_signo = {3}
            """.format(res['ic_clasecc'], tra_codigo, to_sec_codigo, res['ttp_signo'])

            tupla = ('cta_codigo', 'ttp_signo', 'ic_clasecc')
            resc = self.first(sql, tupla)
            if resc is not None:
                cta_codigo_pago = resc['cta_codigo']

        return cta_codigo_pago

    def change_seccion(self, trn_codigo, new_sec_codigo):
        tasiento = self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()
        changed = False
        if tasiento is not None:
            tra_codigo = tasiento.tra_codigo

            if tasiento.sec_codigo == new_sec_codigo:
                raise ErrorValidacionExc('Escoja otra sección, le sección escogida es la misma del documento actual')

            # is_abono = tra_codigo == 8 or tra_codigo == 9

            detalles = self.dbsession.query(TAsidetalle).filter(TAsidetalle.trn_codigo == trn_codigo).all()
            changed = False
            if detalles is not None:
                for detalle in detalles:
                    dt_tipoitem = detalle.dt_tipoitem
                    new_cta_cod = None
                    if dt_tipoitem == ctes.DT_TIPO_ITEM_DETALLE:
                        new_cta_cod = self.find_cta_codigo_prodserv(cta_codigo=detalle.cta_codigo,
                                                                    tra_codigo=tra_codigo,
                                                                    from_sec_codigo=tasiento.sec_codigo,
                                                                    to_sec_codigo=new_sec_codigo)
                    elif dt_tipoitem == ctes.DT_TIPO_ITEM_IMPUESTO:
                        new_cta_cod = self.find_cta_codigo_imp(cta_codigo=detalle.cta_codigo, tra_codigo=tra_codigo,
                                                               from_sec_codigo=tasiento.sec_codigo,
                                                               to_sec_codigo=new_sec_codigo)
                    elif dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
                        new_cta_cod = self.find_cta_codigo_pago(cta_codigo=detalle.cta_codigo, tra_codigo=tra_codigo,
                                                                from_sec_codigo=tasiento.sec_codigo,
                                                                to_sec_codigo=new_sec_codigo)
                    elif dt_tipoitem == ctes.DT_TIPO_ITEM_DETASIENTO:
                        new_cta_cod = self.find_cta_codigo_abo(cta_codigo=detalle.cta_codigo, tra_codigo=tra_codigo,
                                                               from_sec_codigo=tasiento.sec_codigo,
                                                               to_sec_codigo=new_sec_codigo)
                        if new_cta_cod is None:

                            tasiabodao = TAsiAbonoDao(self.dbsession)
                            datosabo = tasiabodao.get_datos_abono_by_dt_codigo(dt_codigo=detalle.dt_codigo)
                            if datosabo is not None:
                                new_cta_cod = self.find_cta_codigo_pago(cta_codigo=detalle.cta_codigo,
                                                                        tra_codigo=datosabo['tra_codigo'],
                                                                        from_sec_codigo=tasiento.sec_codigo,
                                                                        to_sec_codigo=new_sec_codigo)

                    if new_cta_cod is not None:
                        changed = True
                        detalle.cta_codigo = new_cta_cod
                        detalle.dt_codsec = new_sec_codigo
                        self.dbsession.add(detalle)

            if changed and tasiento is not None:
                tasiento.sec_codigo = new_sec_codigo
                self.dbsession.add(tasiento)

        return changed
