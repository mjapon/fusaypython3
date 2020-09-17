alter table fusay.tventatickets
	add vt_clase int default 1 not null;

comment on column fusay.tventatickets.vt_clase is 'Clase del asiento ingreso o egreso
1-ingreso
2-gasto';

alter table fusay.tventatickets
	add vt_fecha date default now() not null;

UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTTK_ROD';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTTK_JAI';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTTK_DIA';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTKAM_ROD';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTMED_SARA';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENKAMB_SARA';
UPDATE fusay.titemconfig set clsic_id=1 where ic_code='VENTICK_SARA';

INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('GASTOS EN GENERAL', 'GAST_GEN', null, 4, current_date, null, 1, null, 1, 2, null, null);


UPDATE fusay.tgrid set grid_basesql = 'select vt_id, vt_fechareg, vt_monto, vt_tipo, ic.ic_nombre, vt_estado,
       case when vt_estado = 0 then ''Pendiente''
            when vt_estado = 1  then ''Confirmado''
            when vt_estado = 2  then ''Anulado'' else ''desc'' end as estadodesc,
       vt_obs, vt_fecha from tventatickets vt
        join titemconfig ic on vt.vt_tipo = ic.ic_id where vt.vt_estado in (0,1) {andwhere}  order by vt_fecha desc' where grid_nombre = 'ventatickets';


UPDATE fusay.tgrid set grid_tupladesc = '["vt_id", "vt_fechareg", "vt_monto", "vt_tipo", "ic_nombre", "vt_estado", "estadodesc", "vt_obs", "vt_fecha"]' where grid_nombre = 'ventatickets';

UPDATE fusay.tgrid set grid_columnas = '[
    {"label":"Fecha", "field":"vt_fecha"},
    {"label":"Rubro", "field":"ic_nombre"},
    {"label":"Monto", "field":"vt_monto"},
    {"label":"Estado", "field":"estadodesc"},
    {"label":"Observación", "field":"vt_obs"},
    {"label":"Registro", "field":"vt_fechareg"}
]' where grid_nombre = 'ventatickets'