drop view vasientosgen;
create view vasientosgen
            (trn_codigo, tra_codigo, trn_fecreg, trn_compro, trn_fecha, trn_valido, trn_docpen, per_codigo, us_id,
             trn_observ, dt_debito, cta_codigo, ic_code, ic_nombre, dt_valor)
as
SELECT a.trn_codigo,
       a.tra_codigo,
       a.trn_fecreg,
       a.trn_compro_rel          AS trn_compro,
       a.trn_fecha,
       a.trn_valido,
       a.trn_docpen,
       a.per_codigo,
       a.us_id,
       a.trn_observ,
       b.dt_debito,
       b.cta_codigo,
       c.ic_code,
       c.ic_nombre,
       round(sum(b.dt_valor), 2) AS dt_valor
FROM fusay.tasiento a
         JOIN fusay.tasidetalle b ON b.trn_codigo = a.trn_codigo
         JOIN fusay.titemconfig c ON b.cta_codigo = c.ic_id
WHERE a.trn_compro_rel IS NOT NULL
  AND (a.tra_codigo = ANY (ARRAY [1, 2, 7]))
  AND a.trn_valido = 0
GROUP BY b.cta_codigo, c.ic_code, c.ic_nombre, a.trn_codigo, a.tra_codigo, a.trn_fecreg, a.trn_compro_rel, a.trn_fecha,
         a.trn_valido, a.trn_docpen, a.per_codigo, a.us_id, a.trn_observ, b.dt_debito
ORDER BY a.trn_fecreg DESC, a.trn_compro_rel DESC, b.dt_debito DESC;

alter table vasientosgen
    owner to postgres;

