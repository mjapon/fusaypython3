SELECT setval(pg_get_serial_sequence('fusay.tlistavalores_cat', 'lvcat_id'), coalesce(max(lvcat_id),0) + 1, false) FROM fusay.tlistavalores_cat;
insert into fusay.tlistavalores_cat values (nextval('fusay.tlistavalores_cat_lvcat_id_seq'),  'ESPECIDALIDAD', 'ESPMED','ESPECIALIDAD MEDICA');

SELECT setval(pg_get_serial_sequence('fusay.tlistavalores', 'lval_id'), coalesce(max(lval_id),0) + 1, false) FROM fusay.tlistavalores;

insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_RO',
                                        'Rehabilitación oral',
                                        1,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_PR',
                                        'Periodoncia',
                                        2,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_END',
                                        'Endodoncia',
                                        3,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_ODP',
                                        'Odontopediatría',
                                        4,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_ORT',
                                        'Ortodoncia',
                                        5,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_IMO',
                                        'Implantología oral',
                                        6,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_OEC',
                                        'Odontología estética o cosmética',
                                        7,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_OPR',
                                        'Odontología preventiva',
                                        8,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_PF',
                                        'Odontología forense',
                                        9,null,1);
insert into fusay.tlistavalores values (nextval('fusay.tlistavalores_lval_id_seq'),
                                        (select lvcat_id from fusay.tlistavalores_cat where lvcat_abrev = 'ESPMED'),
                                        'ESPMO_CM',
                                        'Cirugía maxilofacial',
                                        10,null,1);

--Creacion de nuevas tablas para registro de medicos:
create table fusay.tmedico
(
	med_id serial not null,
	per_id int not null,
	med_fecreg timestamp default now()
);

comment on table fusay.tmedico is 'Se asocian las personas registradas como medicos';

create unique index tmedico_med_id_uindex
	on fusay.tmedico (med_id);

alter table fusay.tmedico
	add constraint tmedico_pk
		primary key (med_id);


create table fusay.tmedicoespe
(
	medesp_id serial not null,
	med_id int not null,
	esp_id int not null,
	medesp_estado int default 0 not null
);

comment on table fusay.tmedicoespe is 'Registra las especialidades de un medico';

comment on column fusay.tmedicoespe.medesp_estado is '0-activo
1-inactivo';

create unique index tmedicoespe_medesp_id_uindex
	on fusay.tmedicoespe (medesp_id);

alter table fusay.tmedicoespe
	add constraint tmedicoespe_pk
		primary key (medesp_id);


alter table fusay.tconsultam_cats
	add catcm_tipo int default 1 not null;

comment on column fusay.tconsultam_cats.catcm_tipo is '1- Medico
2- Odontologo';

SELECT setval('fusay.tconsultam_cats_catcm_id_seq', COALESCE((SELECT MAX(catcm_id)+1 FROM fusay.tconsultam_cats), 1), false);

INSERT INTO fusay.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (nextval('fusay.tconsultam_cats_catcm_id_seq'), 'ANTCDETS_ODNTO', 'ANTECEDENTES', 2);
--INSERT INTO fusay.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (nextval('fusay.tconsultam_cats_catcm_id_seq'), 'REVXSISTEMAS_ODONTO', 'ANTECEDENTES', 2);

SELECT setval('fusay.tconsultam_tiposval_cmtv_id_seq', COALESCE((SELECT MAX(cmtv_id)+1 FROM fusay.tconsultam_tiposval), 1), false);

INSERT INTO fusay.tconsultam_tiposval (cmtv_id, cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) select nextval('fusay.tconsultam_tiposval_cmtv_id_seq'), catcm_id, 'ANT_PERSONALES', 'PERSONALES', 2, 1, null  from fusay.tconsultam_cats where catcm_nombre = 'ANTCDETS_ODNTO';
INSERT INTO fusay.tconsultam_tiposval (cmtv_id, cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) select nextval('fusay.tconsultam_tiposval_cmtv_id_seq'), catcm_id, 'ANT_FAMILIARES', 'FAMILIARES', 2, 1, null  from fusay.tconsultam_cats where catcm_nombre = 'ANTCDETS_ODNTO';


alter table fusay.tconsultamedica
	add cosm_tipo int default 1 not null;


alter table fusay.tconsultamedica
	add cosm_estado int default 1 not null;

comment on column fusay.tconsultamedica.cosm_estado is '1- valido
2- anulado';


comment on column fusay.tconsultamedica.cosm_tipo is '1- medica
2- odontologica';





