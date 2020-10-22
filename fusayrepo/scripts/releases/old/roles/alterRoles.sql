alter table fusay.tconsultamedica add cosm_odontograma text;

-- auto-generated definition
create table trol
(
    rl_id          serial                  not null
        constraint trol_pkey
            primary key,
    rl_name        varchar(50)             not null,
    rl_desc        varchar(100),
    rl_abreviacion varchar(50)             not null,
    rl_grupo       integer   default 0     not null,
    rl_estado      integer   default 0     not null,
    rl_fechacrea   timestamp default now() not null,
    rl_usercrea    integer,
    rl_fechaanula  timestamp,
    rl_fechaedita  timestamp
);

comment on table trol is 'Tabla para registro de roles en el sistema';

alter table trol
    owner to postgres;

create unique index trol_rl_abreviacion_uindex
    on trol (rl_abreviacion);

-- auto-generated definition
create table tfuserrol
(
    usrl_id        serial  not null
        constraint tfuserrol_pk
            primary key,
    us_id          integer not null,
    rl_id          integer not null,
    usrl_fechacrea timestamp
);

alter table tfuserrol
    owner to postgres;

create unique index tfuserrol_usrl_id_uindex
    on tfuserrol (usrl_id);

-- auto-generated definition
create table tpermiso
(
    prm_id          serial            not null
        constraint tpermisorol_pk
            primary key,
    prm_nombre      varchar(50)       not null,
    prm_abreviacion varchar(50)       not null,
    prm_detalle     varchar(200),
    prm_estado      integer default 0 not null
);

alter table tpermiso
    owner to postgres;

create unique index tpermisorol_prl_id_uindex
    on tpermiso (prm_id);

create unique index tpermisorol_prl_abreviacion_uindex
    on tpermiso (prm_abreviacion);



-- auto-generated definition
create table tpermisorol
(
    prl_id        serial  not null,
    prm_id        integer not null,
    rl_id         integer not null,
    prl_fechacrea timestamp
);

alter table tpermisorol
    owner to postgres;
