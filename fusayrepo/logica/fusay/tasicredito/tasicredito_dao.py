# coding: utf-8
"""
Fecha de creacion 1/8/21
@autor: mjapon
"""
import decimal
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasicredito.tasicredito_model import TAsicredito
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.utils import ctes, fechas, numeros

log = logging.getLogger(__name__)


class TAsicreditoDao(BaseDao):

    def crear(self, form, tra_codigo_cred):
        tasicredito = TAsicredito()

        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
        resestabsec = ttransacc_pdv.get_estabptoemi_secuencia(alm_codigo=0, tra_codigo=tra_codigo_cred,
                                                              tdv_codigo=0, sec_codigo=0)
        secuencia = resestabsec['secuencia']
        len_compro = ctes.LEN_DOC_TRANSACC
        cre_compro = "{0}".format(str(secuencia)).zfill(len_compro)

        tasicredito.dt_codigo = form['dt_codigo']
        if form['cre_fecini'] is not None:
            tasicredito.cre_fecini = fechas.parse_cadena(form['cre_fecini'])
        if form['cre_fecven'] is not None:
            tasicredito.cre_fecven = fechas.parse_cadena(form['cre_fecven'])
        tasicredito.cre_intere = form['cre_intere']
        tasicredito.cre_intmor = form['cre_intmor']
        tasicredito.cre_compro = cre_compro
        tasicredito.cre_codban = form['cre_codban']
        tasicredito.cre_saldopen = form['cre_saldopen']

        self.dbsession.add(tasicredito)
        ttransacc_pdv.gen_secuencia(tps_codigo=resestabsec['tps_codigo'], secuencia=secuencia)

    def abonar_credito(self, dt_codcred, monto_abono):
        montoabodec = decimal.Decimal(monto_abono)
        if montoabodec is None or montoabodec <= 0:
            raise ErrorValidacionExc('Monto de abono incorrecto ({0}), no puede ser valores negativos o cero',
                                     format(monto_abono))

        tasicredito = self.dbsession.query(TAsicredito).filter(TAsicredito.dt_codigo == dt_codcred).first()
        if tasicredito is not None:
            cre_saldopen = tasicredito.cre_saldopen
            if cre_saldopen > 0:
                rmontoabo = numeros.roundm2(monto_abono)
                rsaldpen = numeros.roundm2(cre_saldopen)

                if rmontoabo > rsaldpen:
                    raise ErrorValidacionExc(
                        'El monto a abonar ({0}) es mayor al saldo pendiente ({1}), no es posible registrar'.format(
                            rmontoabo, rsaldpen))
                else:
                    newsaldopen = decimal.Decimal(tasicredito.cre_saldopen) - decimal.Decimal(monto_abono)
                    tasicredito.cre_saldopen = numeros.roundm2(newsaldopen)
                    self.dbsession.add(tasicredito)

        return tasicredito.cre_saldopen

    def anular_abono(self, dt_codcred, monto_abono_anular, monto_total_cred):
        tasicredito = self.dbsession.query(TAsicredito).filter(TAsicredito.dt_codigo == dt_codcred).first()
        if tasicredito is not None:
            cre_saldopen = tasicredito.cre_saldopen
            new_saldopen = cre_saldopen + decimal.Decimal(monto_abono_anular)
            new_saldopen_round = numeros.roundm2(new_saldopen)
            montototal_round = numeros.roundm2(monto_total_cred)
            if new_saldopen_round > montototal_round:
                raise ErrorValidacionExc(
                    'No es posible anular el abono para este crédito, el nuevo saldo({0}) supera el monto total del crédito ({1})'.format(
                        new_saldopen_round, montototal_round))
            tasicredito.cre_saldopen = new_saldopen
            self.dbsession.add(tasicredito)

    def get_datos_credito(self, cre_codigo):
        sql = """
        select cred.cre_codigo,
               cred.dt_codigo,
               cred.cre_fecini,
            cred.cre_fecven,
            cred.cre_intere,
            cred.cre_intmor,
            cred.cre_compro,
            cred.cre_codban,
            cred.cre_saldopen,
            detcred.dt_valor,
            detcred.cta_codigo,
            detcred.trn_codigo,                        
            ic.ic_clasecc,
               tasi.trn_compro,
               tasi.trn_fecha,
               tasi.trn_fecreg,
               tasi.trn_observ,
               per.per_id,
               per.per_nombres||' '||per.per_apellidos as referente,
               per.per_ciruc
               from tasicredito cred
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo 
        join tpersona per on tasi.per_codigo = per.per_id
        join titemconfig ic on detcred.cta_codigo = ic.ic_id 
        where cred.cre_codigo = {0}
        """.format(cre_codigo)

        tupla_desc = (
            'cre_codigo', 'dt_codigo', 'cre_fecini', 'cre_fecven', 'cre_intere', 'cre_intmor', 'cre_compro',
            'cre_codban', 'cre_saldopen', 'dt_valor', 'cta_codigo', 'trn_codigo', 'ic_clasecc', 'trn_compro',
            'trn_fecha', 'trn_fecreg', 'trn_observ', 'per_id', 'referente', 'per_ciruc')

        return self.first(sql, tupla_desc)

    def get_total_deudas(self, per_codigo, tra_codigo):
        sql = """
                select 
                    sum(cred.cre_saldopen) as totaldeuda
                       from tasicredito cred
                join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
                join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo and tasi.tra_codigo = {tra_codigo} and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
                join tpersona per on tasi.per_codigo = per.per_id and per.per_id = {per_codigo}
                """.format(tra_codigo=tra_codigo, per_codigo=per_codigo)
        totaldeuda = self.first_col(sql, 'totaldeuda')
        return self.type_json(totaldeuda)

    def listar_creditos(self, per_codigo, tra_codigo, solo_pendientes=True):
        """
        Retorna listado de creditos de un referente y de una transaccion especificada
        :param per_codigo:
        :param tra_codigo:
        :param solo_pendientes:
        :return: ['cre_codigo', 'dt_codigo', 'cre_fecini', 'cre_fecven', 'cre_intere', 'cre_intmor', 'cre_compro',
            'cre_codban',
            'cre_saldopen', 'trn_compro', 'trn_fecha', 'trn_fecreg', 'per_id', 'referente', 'per_ciruc']
        """

        sqlpendientes = " "
        if solo_pendientes:
            sqlpendientes = "where cred.cre_saldopen>0"

        sql = """
        select cred.cre_codigo,
               cred.dt_codigo,
               cred.cre_fecini,
            cred.cre_fecven,
            cred.cre_intere,
            cred.cre_intmor,
            cred.cre_compro,
            cred.cre_codban,
            cred.cre_saldopen,
            detcred.dt_valor,
            detcred.trn_codigo,
               tasi.trn_compro,
               tasi.trn_fecha,
               tasi.trn_fecreg,
               tasi.trn_observ,
               per.per_id,
               per.per_nombres||' '||per.per_apellidos as referente,
               per.per_ciruc
               from tasicredito cred
        join tasidetalle detcred on cred.dt_codigo = detcred.dt_codigo
        join tasiento tasi on detcred.trn_codigo = tasi.trn_codigo and tasi.tra_codigo = {tra_codigo} and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
        join tpersona per on tasi.per_codigo = per.per_id and per.per_id = {per_codigo}
        {sqlpend}
        order by tasi.trn_fecreg desc      
        """.format(tra_codigo=tra_codigo, per_codigo=per_codigo, sqlpend=sqlpendientes)

        tupla_desc = (
            'cre_codigo', 'dt_codigo', 'cre_fecini', 'cre_fecven', 'cre_intere', 'cre_intmor', 'cre_compro',
            'cre_codban', 'cre_saldopen', 'dt_valor', 'trn_codigo', 'trn_compro', 'trn_fecha', 'trn_fecreg',
            'trn_observ', 'per_id', 'referente', 'per_ciruc')

        sumas = {
            'totalcred': 0.0,
            'totalsalpend': 0.0
        }

        items = self.all(sql, tupla_desc)

        if items is not None and len(items) > 0:
            for item in items:
                sumas['totalcred'] += item['dt_valor']
                sumas['totalsalpend'] += item['cre_saldopen']

        return items, sumas
