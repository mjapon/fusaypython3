-- auto-generated definition
create table fusay.todantecedentes
(
    od_antid           serial             not null
        constraint tod_antecedentes_pk
            primary key,
    od_antfechacrea    timestamp          not null,
    od_antusercrea     integer            not null,
    od_tipo            smallint default 1 not null,
    pac_id             integer            not null,
    od_antestado       integer  default 1,
    od_fechanula       timestamp,
    od_useranula       integer,
    od_hallazgoexamfis text
);

comment on table fusay.todantecedentes is 'Registra antecedentes y examen fisico de un paciente que requiere citas odontologica';

comment on column fusay.todantecedentes.od_tipo is '1-antecedentes
2-examen fisico';

comment on column fusay.todantecedentes.pac_id is 'Codigo del paciente';

comment on column fusay.todantecedentes.od_antestado is '1-valido
2-anulado';

alter table fusay.todantecedentes
    owner to postgres;

create unique index tod_antecedentes_od_antid_uindex
    on fusay.todantecedentes (od_antid);

create unique index tod_antecedentes_od_antid_uindex_2
    on fusay.todantecedentes (od_antid);


-- auto-generated definition
create table fusay.todantecedentesval
(
    od_antvid  serial  not null
        constraint todantecedentesval_pk
            primary key,
    od_antid   integer not null
        constraint todantecedentesval_todantecedentes_od_antid_fk
            references fusay.todantecedentes,
    cmtv_id    integer not null,
    od_antvval text
);

comment on table fusay.todantecedentesval is 'Registra valores para antecedentes odonto';

alter table fusay.todantecedentesval
    owner to postgres;

create unique index todantecedentesval_od_antvid_uindex
    on fusay.todantecedentesval (od_antvid);


-- auto-generated definition
create table fusay.todatenciones
(
    ate_id             serial             not null
        constraint tod_atenciones_pk
            primary key,
    ate_fechacrea      timestamp          not null,
    user_crea          integer            not null,
    pac_id             integer            not null
        constraint todatenciones_tpersona_per_id_fk
            references fusay.tpersona,
    med_id             integer            not null,
    ate_diagnostico    text,
    ate_procedimiento  text,
    ate_estado         smallint default 1 not null,
    cta_id             integer,
    pnt_id             integer,
    ate_nro            integer  default 1 not null,
    ate_fechanula      timestamp,
    user_anula         integer,
    ate_obsanula       text,
    ate_odontograma    text,
    ate_odontograma_sm text
);

comment on table fusay.todatenciones is 'Registra las atenciones realizadas a un paciente';

comment on column fusay.todatenciones.ate_estado is '1-Valido
2-Anulado';

comment on column fusay.todatenciones.cta_id is 'Codigo de la cita asociada a esta atencion';

comment on column fusay.todatenciones.pnt_id is 'Codigo del plan de tratamiento asociado a esta atencion';

alter table fusay.todatenciones
    owner to postgres;

create unique index tod_atenciones_ate_id_uindex
    on fusay.todatenciones (ate_id);

alter table fusay.tconsultam_valores
    add od_antid int;

comment on column fusay.tconsultam_valores.od_antid is 'Se usa para relacionar con la tabla todantecedentes';

INSERT INTO fusay.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor) VALUES (5, 'ANTECEDENTES_OD', 'ANTECEDENTES');

INSERT INTO fusay.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_PERSONALES', 'PERSONALES', 2, 1, null);
INSERT INTO fusay.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_FAMILIAREAS', 'FAMILIARES', 2, 2, null);
INSERT INTO fusay.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_ALERGICOS', 'ALÉRGICOS', 2, 3, null);


create table fusay.tcita
(
    ct_id serial not null
        constraint tcita_pk
            primary key,
    ct_fecha date not null,
    pac_id integer not null,
    ct_obs text,
    med_id integer,
    ct_serv integer,
    ct_hora numeric(4,2) not null,
    ct_hora_fin numeric(4,2) not null,
    ct_estado integer default 0 not null,
    user_crea integer default 0 not null,
    ct_fechacrea timestamp,
    ct_td boolean default false not null,
    ct_color varchar(50),
    ct_titulo varchar(80)
);

comment on table fusay.tcita is 'Tabla para registro de citas medicas';

comment on column fusay.tcita.pac_id is 'codigo del paciente';

comment on column fusay.tcita.ct_estado is '0-pendiente
1-atendido
2-anulado';

alter table fusay.tcita owner to postgres;

create unique index tcita_cita_id_uindex
    on fusay.tcita (ct_id);

create unique index tcita_cita_id_uindex_2
    on fusay.tcita (ct_id);

INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (9, 'proxcitasod', 'select  cita.ct_id,
        cita.ct_fecha,
       parse_hora(cita.ct_hora)||'' - ''||parse_hora(cita.ct_hora_fin) as hora,
        paciente.per_ciruc,
        paciente.per_movil,
        paciente.per_nombres || '' '' || paciente.per_apellidos as paciente,
        cita.ct_titulo,
        paciente.per_lugresidencia,
        coalesce(tlugar.lug_nombre,'''') as lugresidencia,
        atencion.ate_fechacrea,
        coalesce(atencion.ate_id,0) as ate_id,
        coalesce(atencion.ate_diagnostico) as motivo
from tcita cita
        join tpersona paciente on cita.pac_id = paciente.per_id
        left join tlugar on paciente.per_lugresidencia = tlugar.lug_id
        left join todatenciones atencion on atencion.pac_id = paciente.per_id
        and atencion.ate_id = (select max(ate_id) from todatenciones at where at.pac_id = paciente.per_id and at.ate_estado = 1 )
where cita.ct_estado <> 2 and date(cita.ct_fecha) >= date(  current_date)
{swhere} order by cita.ct_fecha asc', '[
    {"label":"Dia", "field":"ct_fecha"},
    {"label":"Hora", "field":"hora"},
    {"label":"Paciente", "field":"paciente"},    
    {"label":"Motivo", "field":"ct_titulo"},
    {"label":"Celular", "field":"per_movil"} 
]', '2020-10-13 17:26:43.000000', '["ct_id","ct_fecha","hora","per_ciruc","per_movil","paciente","ct_titulo","per_lugresidencia","lugresidencia","ate_fechacrea","ate_id","motivo"]');


create or replace function fusay.parse_hora(val numeric ) returns varchar
    language plpgsql
as
$$
declare decimales numeric;
BEGIN
    decimales:= val%1;
    return lpad(trunc(val)::varchar,2,'0')||':'|| lpad( trunc(decimales*60)::varchar,2,'0');
END;
$$;

alter function fusay.parse_hora(numeric) owner to postgres;