# coding: utf-8
"""
Fecha de creacion 3/18/21
@autor: mjapon
"""
from fusayrepo.logica.dao.base import BaseDao


class TBilleteraHistoDao(BaseDao):

    def _get_bills_in_transacc(self, trn_codigo):
        sqlbills = (
            "select det.dt_codigo, det.dt_debito, round(det.dt_valor,2) as dt_valor, det.cta_codigo, asi.trn_fecha "
            "from tasidetalle det "
            "join tbilletera bil on bil.ic_id = det.cta_codigo "
            "join tasiento asi on det.trn_codigo = asi.trn_codigo "
            "where bil.bil_estado = 1 and asi.trn_valido = 0 and asi.trn_docpen = 'F' and det.trn_codigo =:trncod")

        return self.all_raw(sqlbills, trncod=trn_codigo)

    def destroy_mov(self, trn_codigo):
        """
        Verifica si un asiento anulado corresponde a una billetera
        """
        results = self._get_bills_in_transacc(trn_codigo)
        if results is not None and len(results) > 0:
            for result in results:
                dt_codigo_it = result[0]
                cta_codigo_it = result[3]
                self._remove_history_mov(dt_codigo=dt_codigo_it, cta_codigo=cta_codigo_it)

    def _remove_history_mov(self, dt_codigo, cta_codigo):
        sql = (
            "update tbillhist set bh_valido=1, bh_fechaactualiza=now(),bh_useractualiza=0 where cta_codigo = :ctacod "
            "and dt_codigo>=:dtcod and bh_valido = 0")
        self.execute(sql, ctacod=cta_codigo, dtcod=dt_codigo)

        sqltotalizar = f"""with data as (
                select det.dt_codigo, asi.trn_fecha, det.dt_debito, 
                case when det.dt_debito = 1 then round(det.dt_valor,2) else null end as credito,
                case when det.dt_debito = -1 then round(det.dt_valor,2) else null end as debito,
                det.cta_codigo from tasidetalle det join tasiento asi on det.trn_codigo = asi.trn_codigo
                where coalesce(det.cta_codigo, 0)> 0 and asi.trn_valido = 0 and asi.trn_docpen = 'F'
                  and det.cta_codigo ={cta_codigo} and det.dt_codigo>{dt_codigo} order by asi.trn_fecha
                )
                select dt_codigo, trn_fecha, debito, credito, 
                   coalesce(sum(abs(credito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  -
                   coalesce(sum(abs(debito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  as saldo,
                   cta_codigo
                from data order by trn_fecha asc
            """
        results = self.all_raw(sqltotalizar)

        if results is not None:
            result_saldo = self._get_last_saldo_hist(cta_codigo, dt_codigo)
            current_saldo = 0
            if result_saldo is not None:
                current_saldo = result_saldo[0]

            for result in results:
                it_saldo = result[4] + current_saldo
                sqlinsert = ("insert into tbillhist(dt_codigo,bh_debito,bh_credito,bh_saldo,bh_fechacrea,"
                             "bh_usercrea, bh_valido, bh_fechatransacc,cta_codigo) values ("
                             ":dtcod,:debito, :credito,:saldo,now(),0,0,:fechatrn, :ctacod)")
                self.execute(sqlinsert, dtcod=result[0], debito=result[2], credito=result[3],
                             saldo=it_saldo, fechatrn=result[1], ctacod=cta_codigo)

    def generate_history_mov(self, trn_codigo):
        """
        Crea un registro en la tabla tbillhist
        """

        results = self._get_bills_in_transacc(trn_codigo)

        if results is not None and len(results) > 0:
            for result in results:
                dt_codigo_it = result[0]
                dt_debito_it = result[1]
                dt_valor_it = result[2]
                cta_codigo_it = result[3]
                trn_fecha_it = result[4]
                self._summarize_account(tasidet_row={
                    'cta_codigo': cta_codigo_it,
                    'dt_debito': dt_debito_it,
                    'dt_valor': dt_valor_it,
                    'dt_codigo': dt_codigo_it,
                    'trn_fecha': trn_fecha_it
                })

    def _get_last_saldo_hist(self, cta_codigo, dt_codigo=None):
        sql = "select bh_saldo from tbillhist where cta_codigo = :ctacod and bh_valido = 0 order by dt_codigo desc limit 1"
        if dt_codigo is not None:
            sql = "select bh_saldo from tbillhist where cta_codigo = :ctacod and bh_valido = 0 and dt_codigo<:dtcod order by dt_codigo desc limit 1"
            return self.first_raw(sql, ctacod=cta_codigo, dtcod=dt_codigo)
        return self.first_raw(sql, ctacod=cta_codigo)

    def _summarize_account(self, tasidet_row):
        cta_codigo = tasidet_row['cta_codigo']

        # Traemos la ultima fila registrada para esta cta_codigo
        result = self._get_last_saldo_hist(cta_codigo)
        current_saldo = 0
        if result is not None:
            current_saldo = result[0]

        debito = None
        credito = None
        dt_debito = tasidet_row['dt_debito']
        if dt_debito == -1:
            debito = tasidet_row['dt_valor']
        else:
            credito = tasidet_row['dt_valor']
        saldo = current_saldo + (tasidet_row['dt_valor'] * dt_debito)
        sqlinsert = ("insert into tbillhist(dt_codigo,bh_debito,bh_credito,bh_saldo,bh_fechacrea,"
                     "bh_usercrea, bh_valido, bh_fechatransacc,cta_codigo) values ("
                     ":dtcod,:debito, :credito,:saldo,now(),0,0,:fechatrn, :ctacod)")

        self.execute(sqlinsert, dtcod=tasidet_row['dt_codigo'], debito=debito, credito=credito,
                     saldo=saldo, fechatrn=tasidet_row['trn_fecha'], ctacod=cta_codigo)
