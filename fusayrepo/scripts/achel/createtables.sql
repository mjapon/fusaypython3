create table achel.tuser
(
    us_id          serial                                                not null
        constraint tuser_pkey
            primary key,
    us_name        varchar(50)                                           not null,
    us_pass        varchar(50)                                           not null,
    us_datecreated timestamp                                             not null,
    us_status      integer                                               not null,
    us_statusclave integer      default 0                                not null,
    us_nomapel     varchar(100) default 'setusername'::character varying not null,
    us_superuser   integer      default 0
);

comment on column achel.tuser.us_status is '0-activo
1-inactivo';

comment on column achel.tuser.us_statusclave is 'Estado de la clave 0:temporal, 1:definitivo';

comment on column achel.tuser.us_nomapel is 'Nombres y apellidos del usuario';

comment on column achel.tuser.us_superuser is 'Indica si la cuenta de usuario es de tipo superusuario';

alter table achel.tuser
    owner to postgres;

create table achel.trol
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

comment on table achel.trol is 'Tabla para registro de roles en el sistema';

alter table achel.trol
    owner to postgres;

create unique index trol_rl_abreviacion_uindex
    on achel.trol (rl_abreviacion);

create table achel.tuserrol
(
    usrl_id serial  not null
        constraint tuserrol_pkey
            primary key,
    us_id   integer not null
        constraint tuserrol_tuser_us_id_fk
            references achel.tuser,
    rl_id   integer not null
        constraint tuserrol_trol_rl_id_fk
            references achel.trol
);

alter table achel.tuserrol
    owner to postgres;

create table achel.tcontribuyente
(
    cnt_id              serial            not null
        constraint tcontribuyente_pkey
            primary key,
    cnt_ruc             varchar(13)       not null,
    cnt_razonsocial     varchar(80)       not null,
    cnt_telf            varchar(40),
    cnt_email           varchar(40),
    cnt_dirmatriz       varchar(100)      not null,
    cnt_clase           integer           not null,
    cnt_nrocntespecial  varchar(40),
    cnt_oblcontab       integer default 0 not null,
    cnt_nombrecomercial varchar(80)       not null
);

comment on column achel.tcontribuyente.cnt_clase is '0-persona natural, 1-especial, 2-rise, 3-regimen simplificado';

comment on column achel.tcontribuyente.cnt_oblcontab is '0-NO, 1-Si';

alter table achel.tcontribuyente
    owner to postgres;

create table achel.tautorizacion
(
    aut_id                serial      not null
        constraint tautorizacion_pkey
            primary key,
    aut_numero            numeric(10) not null,
    aut_fechaautorizacion date        not null,
    aut_fechacaducidad    date        not null,
    aut_tipodoc           integer     not null,
    aut_estab             varchar(3)  not null,
    aut_ptoemi            varchar(3)  not null,
    aut_secuencia_ini     numeric(9)  not null,
    cnt_id                integer     not null
        constraint tautorizacion_tcontribuyente_cnt_id_fk
            references achel.tcontribuyente,
    aut_secuencia_fin     numeric(9)  not null
);

alter table achel.tautorizacion
    owner to postgres;

create table achel.ttiposdoc
(
    td_id     integer not null
        constraint tiposdoc_pkey
            primary key,
    td_nombre varchar(40)
);

alter table achel.ttiposdoc
    owner to postgres;

create table achel.tclasecontrib
(
    cls_id     serial      not null
        constraint tclasecontrib_pkey
            primary key,
    cls_nombre varchar(80) not null
);

alter table achel.tclasecontrib
    owner to postgres;

create table achel.tjob
(
    job_id                 serial                                      not null
        constraint jobs_pkey
            primary key,
    aut_id                 integer                                     not null
        constraint jobs_tautorizacion_aut_id_fk
            references achel.tautorizacion,
    job_fechacreacion      timestamp                                   not null,
    job_estado             integer                                     not null,
    job_fechaactualizacion timestamp,
    job_nrocopias          integer    default 1                        not null,
    cnt_id                 integer                                     not null
        constraint jobs_tcontribuyente_cnt_id_fk
            references achel.tcontribuyente,
    user_crea              integer                                     not null,
    user_actualiza         integer,
    temp_id                integer,
    job_ptoemi             varchar(3) default '001'::character varying not null,
    job_secuencia_ini      numeric(9) default 0                        not null,
    job_secuencia_fin      numeric(9) default 0                        not null,
    job_tipodoc            integer    default 1                        not null
);

comment on column tjob.job_ptoemi is 'Numero del punto de emision';

comment on column tjob.job_secuencia_ini is 'Secuacia inicial del documento';

comment on column tjob.job_tipodoc is 'Tipo de documento a imprimir';

alter table achel.tjob
    owner to postgres;

create table achel.tstatusjob
(
    sjb_id     serial      not null
        constraint tstatusjob_pkey
            primary key,
    sjb_nombre varchar(50) not null
);

alter table achel.tstatusjob
    owner to postgres;

create table achel.tplantilla
(
    temp_id     serial            not null
        constraint treporte_pk
            primary key,
    temp_name   varchar(80)       not null,
    temp_jrxml  text              not null,
    temp_tipo   integer default 1 not null,
    temp_desc   text,
    temp_params text
);

comment on table achel.tplantilla is 'Registra plantillas de reportes de jasperreports';

comment on column achel.tplantilla.temp_tipo is '1:plantilla para factura
2:reporte del sistema';

comment on column achel.tplantilla.temp_params is 'Parametros para la generacion de reportes';

alter table achel.tplantilla
    owner to postgres;

create table achel.taudit
(
    aud_id        serial            not null
        constraint taudit_pk
            primary key,
    tbl_id        integer           not null,
    aud_accion    smallint,
    aud_userid    integer,
    aud_fechahora timestamp,
    aud_valorant  text,
    aud_valordesp text,
    aud_obs       varchar(800),
    aud_campo     varchar(100),
    aud_codreg    integer default 0 not null
);

comment on table achel.taudit is 'Registra auditoria de las acciones realizadas en el sistema';

comment on column achel.taudit.aud_accion is '0:insert
1:update
2:delete
';

comment on column achel.taudit.aud_userid is 'usuario que realiza la accion';

comment on column achel.taudit.aud_codreg is 'Codigo del registro de la tabla relacionada a la auditoria';

alter table achel.taudit
    owner to postgres;

create unique index taudit_aud_id_uindex
    on achel.taudit (aud_id);

create table achel.ttabla
(
    tbl_id     serial      not null
        constraint ttablas_pk
            primary key,
    tbl_nombre varchar(80) not null
);

comment on table ttabla is 'Registra tablas usadas en el sistema por tema de auditorias';

alter table achel.ttabla
    owner to postgres;

create unique index ttablas_tbl_id_uindex
    on achel.ttabla (tbl_id);

create table achel.tlogos
(
    lg_id serial not null
        constraint tlogos_pk
            primary key,
    logo  bytea
);

alter table achel.tlogos
    owner to postgres;

create unique index tlogos_lg_id_uindex
    on achel.tlogos (lg_id);

create table achel.tjobreprint
(
    jobrp_id        serial    not null
        constraint tjobreprint_pk
            primary key,
    job_id          integer   not null,
    jobrp_secini    integer   not null,
    jobrp_secfin    integer   not null,
    jobrp_obs       text,
    user_crea       integer   not null,
    jobrp_fechacrea timestamp not null
);

comment on column tjobreprint.jobrp_id is 'Clave primaria';

comment on column tjobreprint.job_id is 'Trabajo de impresion que se realiza la reimpresion';

comment on column tjobreprint.jobrp_secini is 'Secuencia inicial que se realiza la reimpresion';

comment on column tjobreprint.jobrp_secfin is 'Secuencia final que se realiza la reimpresion';

comment on column tjobreprint.jobrp_obs is 'Motivo de la reimpresion';

comment on column tjobreprint.user_crea is 'Usuario que realiza la reimpresion';

comment on column tjobreprint.jobrp_fechacrea is 'Fecha en la que se realiza la reimpresion';

alter table achel.tjobreprint
    owner to postgres;

create unique index tjobreprint_jobrp_id_uindex
    on achel.tjobreprint (jobrp_id);

create table achel.tjobdoc
(
    tjd_id        serial       not null
        constraint tjobdoc_pk
            primary key,
    tjob_id       integer      not null,
    tjd_ruta      varchar(100) not null,
    tjd_fechacrea timestamp    not null,
    tjd_usercrea  integer      not null
);

comment on table tjobdoc is 'Registra el trabajo de impresion generado ruta de los archivos PDF';

comment on column tjobdoc.tjd_id is 'Clave primaria de la tabla';

comment on column tjobdoc.tjob_id is 'Trabajo de impresion asociado';

comment on column tjobdoc.tjd_ruta is 'ruta del archivo registrado';

comment on column tjobdoc.tjd_fechacrea is 'Fecha y hora de creacion del registro';

comment on column tjobdoc.tjd_usercrea is 'Usuario que crea el registro';

alter table achel.tjobdoc
    owner to postgres;

create unique index tjobdoc_tjd_id_uindex
    on achel.tjobdoc (tjd_id);

create table achel.tparams
(
    tprm_id        serial      not null
        constraint tparams_pk
            primary key,
    tprm_abrev     varchar(20) not null,
    tprm_nombre    varchar(80) not null,
    tprm_val       text        not null,
    tprm_fechacrea timestamp default now()
);

comment on table tparams is 'Registra parametros del sistema';

comment on column tparams.tprm_id is 'Clave primaria de la tabla';

comment on column tparams.tprm_abrev is 'Abreviacion del parametro';

comment on column tparams.tprm_nombre is 'Nombre del parametro';

alter table achel.tparams
    owner to postgres;

create unique index tparams_tprm_id_uindex
    on tparams (tprm_id);

create unique index tparams_tprm_abrev_uindex
    on tparams (tprm_abrev);

create table achel.tauditaccion
(
    taa_id     integer     not null
        constraint tauditaccion_pk
            primary key,
    taa_accion varchar(20) not null
);

comment on table achel.tauditaccion is 'Acciones realizadas en auditorias';

comment on column achel.tauditaccion.taa_id is 'Clave primaria de la tabla
';

alter table achel.tauditaccion
    owner to postgres;

create unique index tauditaccion_taa_id_uindex
    on tauditaccion (taa_id);

create table achel.ttablacol
(
    ttc_id    serial  not null
        constraint ttablacol_pk
            primary key,
    tbl_id    integer not null,
    ttc_name  text,
    ttc_label text
);

comment on table achel.ttablacol is 'Tabla para registro de columnas por tabla';

comment on column achel.ttablacol.ttc_id is 'clave primaria';

comment on column achel.ttablacol.tbl_id is 'codigo de la tabla';

alter table achel.ttablacol
    owner to postgres;

create unique index ttablacol_ttc_id_uindex
    on achel.ttablacol (ttc_id);

create table achel.tevents
(
    ev_id             serial                    not null
        constraint tevents_pk
            primary key,
    ev_fecha          date                      not null,
    ev_fechacrea      timestamp                 not null,
    ev_creadopor      integer,
    ev_lugar          integer,
    ev_horainicio     time,
    ev_horafin        time,
    ev_nota           text,
    ev_publicidad     text,
    ev_tipo           integer                   not null,
    ev_precionormal   numeric(8, 3) default 0.0 not null,
    ev_precioespecial numeric(8, 3) default 0.0 not null,
    ev_img            text,
    ev_estado         integer       default 0   not null,
    ev_url            varchar(40)
);

comment on table achel.tevents is 'Registra los eventos de la fundacion';

comment on column achel.tevents.ev_estado is '0-valido
1-anulado';

alter table achel.tevents
    owner to postgres;

create unique index tevents_ev_id_uindex
    on achel.tevents (ev_id);

create table achel.ttipoev
(
    tiev_id     serial      not null
        constraint ttipoev_pk
            primary key,
    tiev_nombre varchar(80) not null,
    tiev_img    varchar(50)
);

comment on table achel.ttipoev is 'Registra tipos de evento';

alter table achel.ttipoev
    owner to postgres;

create unique index ttipoev_tiev_id_uindex
    on achel.ttipoev (tiev_id);

create table achel.tlugarev
(
    lugc_id     serial not null
        constraint tlugarev_pk
            primary key,
    lugc_nombre text   not null
);

alter table achel.tlugarev
    owner to postgres;

create unique index tlugarev_lugc_id_uindex
    on achel.tlugarev (lugc_id);

create table achel.tmbmdir
(
    idm      serial      not null
        constraint tmbmdir_pk
            primary key,
    tipo     varchar(15) not null,
    nombre   varchar(80) not null,
    img      varchar(50) not null,
    longdet  text,
    shortdet text
);

alter table achel.tmbmdir
    owner to postgres;

create unique index tmbmdir_idm_uindex
    on achel.tmbmdir (idm);

create table achel.tpersonaevents
(
    pev_id     serial  not null
        constraint tpersonaevents_pk
            primary key,
    per_id     integer not null,
    ev_id      integer not null,
    pev_fecreg timestamp
);

alter table achel.tpersonaevents
    owner to postgres;

create unique index tpersonaevents_pev_id_uindex
    on achel.tpersonaevents (pev_id);

create table tlugar
(
    lug_id     serial            not null
        constraint tlugar_pk
            primary key,
    lug_nombre varchar(250)      not null,
    lug_parent integer,
    lug_status integer default 1 not null
);

comment on column achel.tlugar.lug_status is '1-activo
2-inactivo';

alter table achel.tlugar
    owner to postgres;

create unique index tlugar_lug_id_uindex
    on achel.tlugar (lug_id);

create table achel.tpersona
(
    per_id            serial            not null
        constraint tperrsona_pk
            primary key,
    per_ciruc         varchar(15),
    per_nombres       varchar(100)      not null,
    per_apellidos     varchar(100),
    per_direccion     varchar(100),
    per_telf          varchar(40),
    per_movil         varchar(20),
    per_email         varchar(40),
    per_fecreg        timestamp,
    per_tipo          integer default 1 not null,
    per_lugnac        integer,
    per_nota          text,
    per_fechanac      date,
    per_genero        integer,
    per_estadocivil   integer,
    per_lugresidencia integer
        constraint tpersona_tlugar_lug_id_fk
            references achel.tlugar,
    per_ocupacion     integer
);

alter table achel.tpersona
    owner to postgres;

create unique index tpersona_per_id_uindex
    on achel.tpersona (per_id);

create unique index tpersona_perciruc_uindex
    on achel.tpersona (per_ciruc);

create unique index tpersona_peremail_uindex
    on achel.tpersona (per_email);

create table achel.tfuser
(
    us_id        serial            not null
        constraint tfuser_pk
            primary key,
    us_cuenta    varchar(20)       not null,
    us_clave     varchar(20)       not null,
    per_id       integer           not null,
    us_fechacrea timestamp,
    us_estado    integer default 0 not null
);

alter table achel.tfuser
    owner to postgres;

create unique index tfuser_us_id_uindex
    on achel.tfuser (us_id);

create table achel.ttickets
(
    tk_id          serial                    not null
        constraint ttickets_pk
            primary key,
    tk_nro         integer                   not null,
    tk_fechahora   timestamp                 not null,
    tk_perid       integer                   not null,
    tk_observacion text,
    tk_usercrea    integer                   not null,
    tk_costo       numeric(4, 2) default 0.0 not null,
    tk_dia         date                      not null,
    tk_estado      integer       default 1   not null,
    tk_servicios   text,
    sec_id         integer       default 1   not null
);

comment on table achel.ttickets is 'Tabla para registro de tickets';

alter table achel.ttickets
    owner to postgres;

create unique index ttickets_tk_id_uindex
    on achel.ttickets (tk_id);

create table achel.tclaseitemconfig
(
    clsic_id          serial            not null
        constraint tclaseitemconfig_pk
            primary key,
    clsic_abreviacion varchar(2)        not null,
    clsic_nombre      varchar(40)       not null,
    clsic_estado      integer default 1 not null
);

comment on table achel.tclaseitemconfig is 'Clase  de item de configuracion esto es activo, pasivo , ingreso, gasto';

alter table achel.tclaseitemconfig
    owner to postgres;

create unique index tclaseitemconfig_cic_id_uindex
    on achel.tclaseitemconfig (clsic_id);

create table achel.tcatitemconfig
(
    catic_id     serial            not null
        constraint tcatitemconfig_pk
            primary key,
    catic_nombre varchar(60)       not null,
    catic_estado integer default 1 not null
);

comment on column achel.tcatitemconfig.catic_nombre is 'Nombre de la categoria del item de configuracion';

comment on column achel.tcatitemconfig.catic_estado is '1-activo
2-inactivo';

alter table achel.tcatitemconfig
    owner to postgres;

create unique index tcatitemconfig_catic_id_uindex
    on achel.tcatitemconfig (catic_id);

create unique index tcatitemconfig_catic_id_uindex_2
    on achel.tcatitemconfig (catic_id);

create table achel.ttipoitemconfig
(
    tipic_id     serial            not null
        constraint ttipoitemconfig_pk
            primary key,
    tipic_nombre varchar(80)       not null,
    tipic_estado integer default 1 not null
);

comment on column achel.ttipoitemconfig.tipic_nombre is 'Nombre del tipo de item de configuracion';

comment on column achel.ttipoitemconfig.tipic_estado is 'Estado del tipo de item de configuracion';

alter table achel.ttipoitemconfig
    owner to postgres;

create unique index ttipoitemconfig_tipic_id_uindex
    on achel.ttipoitemconfig (tipic_id);

create table achel.titemconfig
(
    ic_id             serial                                not null
        constraint titemconfig_pk
            primary key,
    ic_nombre         text                                  not null,
    ic_code           text                                  not null,
    ic_padre          integer,
    tipic_id          integer   default 1                   not null
        constraint titemconfig_ttipoitemconfig_tipic_id_fk
            references achel.ttipoitemconfig,
    ic_fechacrea      timestamp default ('now'::text)::date not null,
    ic_usercrea       integer,
    ic_estado         integer   default 1                   not null,
    ic_nota           text,
    catic_id          integer   default 1                   not null
        constraint titemconfig_tcatitemconfig_catic_id_fk
            references achel.tcatitemconfig,
    clsic_id          integer,
    ic_useractualiza  integer,
    ic_fechaactualiza timestamp
);

comment on table achel.titemconfig is 'Representa un articulo un servicio o una cuenta contable';

comment on column achel.titemconfig.ic_nombre is 'Nombre del item de configuracion';

comment on column achel.titemconfig.ic_code is 'Codigo de barra o codigo de la cuenta contable';

comment on column achel.titemconfig.tipic_id is '1-articulo
2-servicio
3-cuenta contable';

comment on column achel.titemconfig.ic_usercrea is 'Usuario que registra este item de configuracion';

comment on column achel.titemconfig.ic_estado is 'Estado del item de configuracion
1-Activo
2-Inactivo';

comment on column achel.titemconfig.ic_nota is 'Nota para al producto, servicio o cuenta contable';

comment on column achel.titemconfig.catic_id is 'Codigo de la categoria del item de configuracion';

comment on column achel.titemconfig.clsic_id is 'Clase del item de configuracion para el caso de cuentas contables';

alter table achel.titemconfig
    owner to postgres;

create unique index titemconfig_ic_code_uindex
    on achel.titemconfig (ic_code);

create unique index titemconfig_ic_id_uindex
    on achel.titemconfig (ic_id);

create table achel.titemconfig_stock
(
    ice_id          serial                   not null
        constraint tpreciosart_pk
            primary key,
    ic_id           integer                  not null
        constraint tpreciosart_titemconfig_ic_id_fk
            references achel.titemconfig,
    sec_id          integer        default 1 not null,
    ice_stock       numeric(10, 2) default 0 not null,
    user_crea       integer                  not null,
    fecha_crea      timestamp                not null,
    user_actualiza  integer,
    fecha_actualiza timestamp
);

alter table achel.titemconfig_stock
    owner to postgres;

create unique index tpreciosart_part_id_uindex
    on achel.titemconfig_stock (ice_id);

create table achel.titemconfig_datosprod
(
    icdp_id             serial                               not null
        constraint tdatosproducto_pk
            primary key,
    ic_id               integer                              not null
        constraint tdatosproducto_titemconfig_ic_id_fk
            references achel.titemconfig,
    icdp_fechacaducidad date,
    icdp_proveedor      integer        default '-2'::integer not null,
    icdp_modcontab      integer
        constraint tdatosproductomodcontablefk
            references achel.titemconfig,
    icdp_preciocompra   numeric(10, 4) default 0.0           not null,
    icdp_precioventa    numeric(10, 4) default 0.0           not null,
    icdp_precioventamin numeric(10, 4) default 0.0           not null,
    icdp_grabaiva       boolean        default false         not null
);

comment on column achel.titemconfig_datosprod.icdp_fechacaducidad is 'Fecha de caducidad del articulo';

alter table achel.titemconfig_datosprod
    owner to postgres;

create unique index tdatosproducto_dprod_id_uindex
    on achel.titemconfig_datosprod (icdp_id);

create table achel.tgrid
(
    grid_id        serial                     not null
        constraint tgrid_pk
            primary key,
    grid_nombre    varchar(40)                not null,
    grid_basesql   text                       not null,
    grid_columnas  text                       not null,
    grid_fechacrea timestamp default now()    not null,
    grid_tupladesc text      default ''::text not null
);

comment on table achel.tgrid is 'Registra los grids del sistema';

alter table achel.tgrid
    owner to postgres;

create unique index tgrid_grid_id_uindex
    on achel.tgrid (grid_id);

create table achel.tblog
(
    blg_id        serial    not null
        constraint tblog_pk
            primary key,
    blg_fecha     date      not null,
    blg_autor     text      not null,
    blg_titulo    text      not null,
    blg_img       text,
    blg_fechacrea timestamp not null,
    blg_contenido text      not null
);

alter table achel.tblog
    owner to postgres;

create unique index tblog_blg_id_uindex
    on achel.tblog (blg_id);

create table achel.tseccion
(
    sec_id     serial            not null
        constraint tseccion_pk
            primary key,
    sec_nombre varchar(100)      not null,
    sec_estado integer default 1 not null
);

comment on table achel.tseccion is 'Registra las secciones de una empresa';

comment on column achel.tseccion.sec_estado is '1-activo
2-inactivo';

alter table achel.tseccion
    owner to postgres;

create unique index tseccion_sec_id_uindex
    on achel.tseccion (sec_id);

create table achel.titemconfig_audit
(
    ica_id         serial         not null
        constraint titemconfig_audit_pk
            primary key,
    ic_id          integer        not null,
    user_crea      integer        not null,
    fecha_crea     timestamp      not null,
    ica_tipo       char           not null,
    ica_valantes   numeric(10, 4) not null,
    ica_valdespues numeric(10, 4) not null,
    sec_id         integer        not null
);

comment on table achel.titemconfig_audit is 'Registra los cambios realizados en precios y stock de un producto';

comment on column achel.titemconfig_audit.ica_tipo is 'P-precio
S-stock';

comment on column achel.titemconfig_audit.ica_valantes is 'Valor que tuvo el articulo(stock o precio) antes de relizar el cambio';

comment on column achel.titemconfig_audit.ica_valdespues is 'Valor que tiene el articulo(stock o precio) despues de realizar el cambio';

comment on column achel.titemconfig_audit.sec_id is 'Seccion donde se encuentra el usuario';

alter table achel.titemconfig_audit
    owner to postgres;

create unique index titemconfig_audit_ica_id_uindex
    on achel.titemconfig_audit (ica_id);

create table achel.tuserpaciente
(
    up_id        serial            not null
        constraint tuserpaciente_pk
            primary key,
    up_email     varchar(50)       not null,
    up_tipo      integer default 1 not null,
    up_pasword   text,
    up_estado    integer default 0 not null,
    up_fechacrea timestamp         not null,
    up_nombres   text              not null,
    up_celular   text,
    up_photourl  text
);

comment on column achel.tuserpaciente.up_tipo is '1 - Facebook
2- Google
3- Email';

comment on column achel.tuserpaciente.up_estado is '0 - activo
1 - inactivo';

alter table achel.tuserpaciente
    owner to postgres;

create unique index tuserpaciente_up_id_uindex
    on achel.tuserpaciente (up_id);

create table achel.tcita
(
    cita_id       serial            not null
        constraint tcita_pk
            primary key,
    cita_fecha    date              not null,
    paciente_id   integer           not null,
    cita_obs      text,
    medico_id     integer,
    cita_serv     integer           not null,
    cita_hora     numeric(4, 2)     not null,
    cita_hora_fin numeric(4, 2)     not null,
    cita_estado   integer default 0 not null
);

comment on table achel.tcita is 'Tabla que registra citas para telemedicina';

comment on column achel.tcita.paciente_id is 'codigo del paciente';

comment on column achel.tcita.cita_estado is '0-pendiente
1-atendido
2-anulado';

alter table achel.tcita
    owner to postgres;

create unique index tcita_cita_id_uindex
    on achel.tcita (cita_id);

create unique index tcita_cita_id_uindex_2
    on achel.tcita (cita_id);

create table achel.thorariomedico
(
    hm_id      serial        not null
        constraint thorariomedico_pk
            primary key,
    med_id     integer       not null,
    hm_dia     integer       not null,
    hm_horaini numeric(4, 2) not null,
    hm_horafin numeric(4, 2) not null
);

alter table achel.thorariomedico
    owner to postgres;

create unique index thorariomedico_hm_id_uindex
    on achel.thorariomedico (hm_id);

create table achel.tserviciomedico
(
    tsm_id  serial  not null
        constraint tserviciomedico_pk
            primary key,
    med_id  integer not null,
    serv_id integer not null
);

alter table achel.tserviciomedico
    owner to postgres;

create unique index tserviciomedico_tsm_id_uindex
    on achel.tserviciomedico (tsm_id);

create table achel.tlistavalores
(
    lval_id       serial            not null
        constraint tlistavalores_pk
            primary key,
    lval_cat      integer           not null,
    lval_abrev    varchar(20)       not null,
    lval_nombre   varchar(120)      not null,
    lval_valor    text              not null,
    lval_valoradc text,
    lval_estado   integer default 1 not null
);

comment on table achel.tlistavalores is 'Registra catalogos';

comment on column achel.tlistavalores.lval_estado is '1-activo
2-inactivo';

alter table achel.tlistavalores
    owner to postgres;

create unique index tlistavalores_lval_abrev_uindex
    on achel.tlistavalores (lval_abrev);

create unique index tlistavalores_lval_id_uindex
    on achel.tlistavalores (lval_id);

create table achel.tlistavalores_cat
(
    lvcat_id          serial       not null,
    lvcat_nombre      varchar(100) not null,
    lvcat_abrev       varchar(80)  not null,
    lvcat_descripcion text
);

comment on table achel.tlistavalores_cat is 'Categorias para catalogos';

alter table achel.tlistavalores_cat
    owner to postgres;

create unique index tlistavalores_cat_lvcat_abrev_uindex
    on achel.tlistavalores_cat (lvcat_abrev);

create unique index tlistavalores_cat_lvcat_id_uindex
    on achel.tlistavalores_cat (lvcat_id);

create table achel.tconsultamedica
(
    cosm_id              serial            not null
        constraint tconsultamedica_pk
            primary key,
    pac_id               integer,
    med_id               integer,
    cosm_fechacita       timestamp         not null,
    cosm_fechacrea       timestamp         not null,
    cosm_motivo          text,
    cosm_enfermactual    text,
    cosm_hallazgoexamfis text,
    cosm_exmscompl       text,
    cosm_tratamiento     text,
    cosm_receta          text,
    cosm_recomendaciones text,
    user_crea            integer,
    cosm_indicsreceta    text,
    cosm_diagnostico     integer,
    cosm_diagnosticoal   text,
    cosm_fechaproxcita   date,
    cosm_diagnosticos    varchar(50),
    cosm_tipo            integer default 1 not null,
    cosm_estado          integer default 1 not null,
    cosm_odontograma     text
);

comment on table achel.tconsultamedica is 'Registra consultas medicas';

comment on column achel.tconsultamedica.pac_id is 'Codigo del paciente';

comment on column achel.tconsultamedica.med_id is 'codigo del medico asignado';

comment on column achel.tconsultamedica.cosm_fechacita is 'Fecha de la cita medica';

comment on column achel.tconsultamedica.cosm_enfermactual is 'Enfermedad actual';

comment on column achel.tconsultamedica.cosm_hallazgoexamfis is 'Hallazgos en examenes fisicos';

comment on column achel.tconsultamedica.cosm_exmscompl is 'Examenes complementarios';

comment on column achel.tconsultamedica.cosm_diagnostico is 'Representa el codigo de la enfermedad en la tabla cie10';

comment on column achel.tconsultamedica.cosm_tipo is '1- medica
2- odontologica';

comment on column achel.tconsultamedica.cosm_estado is '1- valido
2- anulado';

alter table achel.tconsultamedica
    owner to postgres;

create unique index tconsultamedica_cosm_id_uindex
    on achel.tconsultamedica (cosm_id);

create table achel.tconsultam_valores
(
    cosm_id     integer not null,
    valcm_id    serial  not null
        constraint tcosm_valores_pk
            primary key,
    valcm_tipo  integer not null,
    valcm_valor text    not null,
    valcm_categ integer not null
);

comment on table achel.tconsultam_valores is 'Antecedentes de la consulta medica';

comment on column achel.tconsultam_valores.valcm_categ is 'antecedentes, revsistemas, diagnostico, examefisico';

alter table achel.tconsultam_valores
    owner to postgres;

create unique index tcosm_valores_valcm_id_uindex
    on achel.tconsultam_valores (valcm_id);

create table achel.tconsultam_cats
(
    catcm_id     serial            not null
        constraint tconsultam_cats_pk
            primary key,
    catcm_nombre varchar(80)       not null,
    catcm_valor  varchar(100)      not null,
    catcm_tipo   integer default 1 not null
);

comment on table achel.tconsultam_cats is 'Categorias para los valores que se registran en una consulta medica';

comment on column achel.tconsultam_cats.catcm_tipo is '1- Medico
2- Odontologo';

alter table achel.tconsultam_cats
    owner to postgres;

create unique index tconsultam_cats_catcm_id_uindex
    on achel.tconsultam_cats (catcm_id);

create table achel.tconsultam_tiposval
(
    cmtv_id     serial            not null
        constraint tconsultam_tiposval_pk
            primary key,
    cmtv_cat    integer           not null,
    cmtv_nombre varchar(80)       not null,
    cmtv_valor  varchar(80)       not null,
    cmtv_tinput integer default 1 not null,
    cmtv_orden  integer default 1 not null,
    cmtv_unidad varchar
);

comment on table achel.tconsultam_tiposval is 'Tipos de valores registrados en consultas medicas';

comment on column achel.tconsultam_tiposval.cmtv_tinput is 'Representa el tipo de input 1: textbox: 2:textarea';

alter table achel.tconsultam_tiposval
    owner to postgres;

create unique index tconsultam_tiposval_cmtv_id_uindex
    on achel.tconsultam_tiposval (cmtv_id);

create table achel.tcie10
(
    cie_id    serial       not null
        constraint cie10_pk
            primary key,
    cie_key   varchar(40)  not null,
    cie_valor varchar(300) not null
);

comment on table achel.tcie10 is 'Codigos de enfermedades';

alter table achel.tcie10
    owner to postgres;

create unique index cie10_cie_id_uindex
    on achel.tcie10 (cie_id);

create unique index cie10_cie_key_uindex
    on achel.tcie10 (cie_key);

create table achel.tconsultam_clasificaval
(
    cmcv_id        serial  not null
        constraint tconsultam_clasificaval_pk
            primary key,
    cmcv_nombrecat varchar(80),
    cmcv_cat       integer not null,
    cmcv_max       numeric(8, 2),
    cmcv_min       numeric(8, 2),
    cmcv_color     varchar(20),
    cmcv_minb      numeric(8, 2) default 0,
    cmcv_maxb      numeric(8, 2) default 0
);

comment on table achel.tconsultam_clasificaval is 'Clasificacion para las lecturas de los examenes fisicos';

alter table achel.tconsultam_clasificaval
    owner to postgres;

create unique index tconsultam_clasificaval_cmcv_id_uindex
    on achel.tconsultam_clasificaval (cmcv_id);

create table achel.tmedico
(
    med_id     serial  not null
        constraint tmedico_pk
            primary key,
    per_id     integer not null,
    med_fecreg timestamp default now()
);

comment on table achel.tmedico is 'Se asocian las personas registradas como medicos';

alter table achel.tmedico
    owner to postgres;

create unique index tmedico_med_id_uindex
    on achel.tmedico (med_id);

create table achel.tmedicoespe
(
    medesp_id     serial            not null
        constraint tmedicoespe_pk
            primary key,
    med_id        integer           not null,
    esp_id        integer           not null,
    medesp_estado integer default 0 not null
);

comment on table achel.tmedicoespe is 'Registra las especialidades de un medico';

comment on column achel.tmedicoespe.medesp_estado is '0-activo
1-inactivo';

alter table achel.tmedicoespe
    owner to postgres;

create unique index tmedicoespe_medesp_id_uindex
    on achel.tmedicoespe (medesp_id);

create table achel.tventatickets
(
    vt_id       serial                      not null
        constraint tventatickets_pk
            primary key,
    vt_fechareg timestamp     default now() not null,
    vt_monto    numeric(6, 2) default 0.0   not null,
    vt_tipo     integer                     not null,
    vt_estado   integer       default 0     not null,
    vt_obs      text,
    vt_clase    integer       default 1     not null,
    vt_fecha    date          default now() not null
);

comment on column achel.tventatickets.vt_tipo is '1- Venta saraguro
2- Venta cuenca
3- Venta diana
4- Venta jaime';

comment on column achel.tventatickets.vt_estado is '0- borrador
1- confirmado
2- anulado';

comment on column achel.tventatickets.vt_obs is 'observacion';

comment on column achel.tventatickets.vt_clase is 'Clase del asiento ingreso o egreso
1-ingreso
2-gasto';

alter table achel.tventatickets
    owner to postgres;

create unique index tventatickets_vt_id_uindex
    on achel.tventatickets (vt_id);

create table achel.tpermiso
(
    prm_id          serial            not null
        constraint tpermisorol_pk
            primary key,
    prm_nombre      varchar(50)       not null,
    prm_abreviacion varchar(50)       not null,
    prm_detalle     varchar(200),
    prm_estado      integer default 0 not null
);

alter table achel.tpermiso
    owner to postgres;

create unique index tpermisorol_prl_id_uindex
    on achel.tpermiso (prm_id);

create unique index tpermisorol_prl_abreviacion_uindex
    on achel.tpermiso (prm_abreviacion);

create table achel.tpermisorol
(
    prl_id        serial  not null,
    prm_id        integer not null,
    rl_id         integer not null,
    prl_fechacrea timestamp
);

alter table achel.tpermisorol
    owner to postgres;

create table achel.tfuserrol
(
    usrl_id        serial  not null
        constraint tfuserrol_pk
            primary key,
    us_id          integer not null,
    rl_id          integer not null,
    usrl_fechacrea timestamp
);

alter table achel.tfuserrol
    owner to postgres;

create unique index tfuserrol_usrl_id_uindex
    on achel.tfuserrol (usrl_id);

create function achel.inc(val integer) returns integer
    language plpgsql
as
$$
BEGIN
    return val + 1;
END;
$$;

alter function achel.inc(integer) owner to postgres;

create function achel.poner_iva(val numeric) returns numeric
    language plpgsql
as
$$
BEGIN
    return 1.12 * val;
END;
$$;

alter function achel.poner_iva(numeric) owner to postgres;

create function achel.quitar_iva(val numeric) returns numeric
    language plpgsql
as
$$
BEGIN
    return (val + 0.0) / 1.12;
END;
$$;

alter function achel.quitar_iva(numeric) owner to postgres;

create function achel.get_diagnosticos(cosm_diagnosticos text) returns character varying
    language plpgsql
as
$$
declare
    diagnosticos text;
BEGIN
    SELECT string_agg(diagnostico::text, ',')
    into diagnosticos
    from (
             select '(' || cie_key || ')' || cie_valor as diagnostico
             from fusay.tcie10
             where cie_id in (
                 with the_data(str) as (
                     select cosm_diagnosticos::text
                 )
                 select elem::int
                 from the_data,
                      unnest(string_to_array(str, ',')) elem
             )
         ) as tabla;

    return diagnosticos;
END;
$$;

alter function achel.get_diagnosticos(text) owner to postgres;
