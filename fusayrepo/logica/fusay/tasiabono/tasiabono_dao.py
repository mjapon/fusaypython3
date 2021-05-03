# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging
from functools import reduce

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiabono.tasiabono_model import TAsiAbono
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao

log = logging.getLogger(__name__)


class TAsiAbonoDao(BaseDao):

    def crear(self, dt_codigo, dt_codcre, monto_abono):
        tasiabono = TAsiAbono()
        tasiabono.dt_codigo = dt_codigo
        tasiabono.dt_codcre = dt_codcre

        self.dbsession.add(tasiabono)
        tasicreditodao = TAsicreditoDao(self.dbsession)
        saldpend = tasicreditodao.abonar_credito(dt_codcred=dt_codcre, monto_abono=monto_abono)
        return saldpend

    def get_modelo_contable(self, tra_codigo, sec_codigo):
        sql = """
        select cta_codigo, tmc_signo from ttransaccmc where tra_codigo = {0} and sec_codigo = {1} and tmc_valido = 0
        """.format(tra_codigo, sec_codigo)

        tupla_desc = ('cta_codigo', 'tmc_signo')
        return self.first(sql, tupla_desc)

    def get_form_abono(self, tra_codigo, sec_codigo):
        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)
        form_cab = tasientodao.get_form_cabecera(tra_codigo, alm_codigo=0, sec_codigo=0, tdv_codigo=0, tra_tipdoc=1)
        form_cab['sec_codigo'] = sec_codigo
        ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)
        form_det = tasientodao.get_form_detalle_asiento()

        modelocont = self.get_modelo_contable(tra_codigo, sec_codigo)
        if modelocont is None:
            raise ErrorValidacionExc(
                'No ha sido definido un modelo contable para la transaccion ({0}), seccion:{1}'.format(tra_codigo,
                                                                                                       sec_codigo))

        form_det['cta_codigo'] = modelocont['cta_codigo']
        form_det['dt_debito'] = modelocont['tmc_signo']

        return {'formcab': form_cab, 'ttransacc': ttransacc, 'formdet': form_det}

    def listar_abonos(self, trn_codigo, trn_valido=0):
        # Se debe listar todos los abonos registrados para una factura específica:

        sql = """
                select  abo.abo_codigo,
                        detcred.dt_valor as dt_valor_cred,
                        detabo.dt_valor,
                        detcred.trn_codigo as trn_codigo_fact,
                        tasiabo.trn_compro as trn_compro_abo,
                        tasiabo.trn_codigo as trn_codigo_abo,
                        tasiabo.trn_valido,                                                                     
                        tasiabo.trn_observ,
                        tasiabo.trn_fecha,
                        tasiabo.trn_fecreg,
                        per.per_id,
                        per.per_nombres||' '||per.per_apellidos as referente,
                        per.per_ciruc
                       from tasiabono abo 
                       join tasidetalle detabo on detabo.dt_codigo = abo.dt_codigo
                       join tasiento tasiabo on tasiabo.trn_codigo = detabo.trn_codigo and tasiabo.trn_docpen = 'F' and tasiabo.trn_valido = {trn_valido}  
                       join tasidetalle detcred on abo.dt_codcre = detcred.dt_codigo                
                       join tasiento tasifact on detcred.trn_codigo = tasifact.trn_codigo and tasifact.trn_codigo = {trn_codigo}
                       join tpersona per on tasifact.per_codigo = per.per_id
                order by tasiabo.trn_fecha      
                """.format(trn_codigo=trn_codigo, trn_valido=trn_valido)

        tupla_desc = (
            'abo_codigo', 'dt_valor_cred', 'dt_valor', 'trn_codigo_fact', 'trn_compro_abo', 'trn_codigo_abo',
            'trn_valido', 'trn_observ', 'trn_fecha', 'trn_fecreg', 'per_id', 'referente', 'per_ciruc'
        )
        abonos = self.all(sql, tupla_desc)
        totalabonos = 0.0
        if len(abonos) > 0:
            totalabonos = reduce(lambda x, y: x + y,
                                 map(lambda x: x['dt_valor'], filter(lambda x: x['trn_valido'] == 0, abonos)))
        return abonos, totalabonos

    def anular(self, abo_codigo, user_anula, obs_anula):
        sql = """
        select abo.abo_codigo, abo.dt_codigo, abo.dt_codcre, 
        asiabo.trn_codigo as trn_cod_abo,
        detcred.dt_valor as dt_valor_cred,
         detabo.dt_valor as dt_valor_abo from tasiabono abo
        join tasidetalle detabo on abo.dt_codigo = detabo.dt_codigo
        join tasidetalle detcred on abo.dt_codcre = detcred.dt_codigo 
        join tasiento asiabo on asiabo.trn_codigo =  detabo.trn_codigo
         where abo.abo_codigo = {0}        
        
        """.format(abo_codigo)

        tupla_desc = ('abo_codigo', 'dt_codigo', 'dt_codcre', 'trn_cod_abo', 'dt_valor_cred', 'dt_valor_abo')

        res = self.first(sql, tupla_desc)
        trn_cod_abo = res['trn_cod_abo']
        dt_valorcred = res['dt_valor_cred']
        dt_codcre = res['dt_codcre']
        dt_valor_abo = res['dt_valor_abo']

        tasicreditodao = TAsicreditoDao(self.dbsession)
        tasicreditodao.anular_abono(dt_codcred=dt_codcre, monto_abono_anular=dt_valor_abo,
                                    monto_total_cred=dt_valorcred)

        from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
        tasientodao = TasientoDao(self.dbsession)
        tasientodao.anular(trn_codigo=trn_cod_abo, user_anula=user_anula, obs_anula=obs_anula)

    def is_transacc_with_abonos(self, dtcodcred):
        sql = """
        select abo.dt_codcre, count(*) as cuenta from tasiabono abo
        join tasidetalle det on abo.dt_codigo = det.dt_codigo
        join tasiento asi on asi.trn_codigo = det.trn_codigo
        where abo.dt_codcre = {0} and asi.trn_valido = 0 and asi.trn_docpen = 'F'
        group by abo.dt_codcre
        """.format(dtcodcred)

        tupla_desc = ('dt_codcre', 'cuenta')
        auxres = self.first(sql, tupla_desc)
        return auxres is not None and auxres['cuenta'] > 0

    def get_total_abonos(self, dt_codcre):
        sql = """
        select coalesce(sum(det.dt_valor), 0.0) as suma from tasiabono abo
        join tasidetalle det on abo.dt_codigo = det.dt_codigo
        join tasiento asi on det.trn_codigo = asi.trn_codigo and asi.trn_valido = 0 
        and asi.trn_docpen = 'F' and asi.trn_pagpen = 'F'
        where abo.dt_codcre = {0}        
        """.format(dt_codcre)

        suma = self.first_col(sql, 'suma')
        return suma

    def get_abonos_entity(self, dt_codcre):
        return self.dbsession.query(TAsiAbono).filter(TAsiAbono.dt_codcre == dt_codcre).all()
