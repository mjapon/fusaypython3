INSERT INTO fusay.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (4, 'RUBRO', 1);

INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('VENTA DE TICKETS RODRIGO', 'VENTTK_ROD', null, 4, current_date, null, 1, null, 1, null, null, null);
INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('VENTA DE TICKETS JAIME', 'VENTTK_JAI', null, 4, current_date, null, 1, null, 1, null, null, null);
INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('VENTA DE TICKETS DIANA', 'VENTTK_DIA', null, 4, current_date, null, 1, null, 1, null, null, null);


create table fusay.tventatickets
(
	vt_id serial not null,
	vt_fechareg timestamp default now() not null,
	vt_monto numeric(6,2) default 0.0 not null,
	vt_tipo int not null,
	vt_estado int default 0 not null,
	vt_obs text
);

comment on column fusay.tventatickets.vt_tipo is '1- Venta saraguro
2- Venta cuenca
3- Venta diana
4- Venta jaime';

comment on column fusay.tventatickets.vt_estado is '0- borrador
1- confirmado
2- anulado';

comment on column fusay.tventatickets.vt_obs is 'observacion';

create unique index tventatickets_vt_id_uindex
	on fusay.tventatickets (vt_id);

alter table fusay.tventatickets
	add constraint tventatickets_pk
		primary key (vt_id);

INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (3, 'ventatickets', ' select vt_id, vt_fechareg, vt_monto, vt_tipo, ic.ic_nombre, vt_estado,
       case when vt_estado = 0 then ''Pendiente''
            when vt_estado = 1  then ''Confirmado''
            when vt_estado = 2  then ''Anulado'' else ''desc'' end as estadodesc,
       vt_obs from tventatickets vt
        join titemconfig ic on vt.vt_tipo = ic.ic_id where vt.vt_estado in (0,1)  order by vt_fechareg desc', '[
    {"label":"Fecha", "field":"vt_fechareg"},
    {"label":"Rubro", "field":"ic_nombre"},
    {"label":"Monto", "field":"vt_monto"},
    {"label":"Estado", "field":"estadodesc"},
    {"label":"Observación", "field":"vt_obs"}
]', current_timestamp, '["vt_id", "vt_fechareg", "vt_monto", "vt_tipo", "ic_nombre", "vt_estado", "estadodesc", "vt_obs"]');

