create table demo.tuser
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

comment on column demo.tuser.us_status is '0-activo
1-inactivo';

comment on column demo.tuser.us_statusclave is 'Estado de la clave 0:temporal, 1:definitivo';

comment on column demo.tuser.us_nomapel is 'Nombres y apellidos del usuario';

comment on column demo.tuser.us_superuser is 'Indica si la cuenta de usuario es de tipo superusuario';

alter table demo.tuser
    owner to postgres;

create table demo.trol
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

comment on table demo.trol is 'Tabla para registro de roles en el sistema';

alter table demo.trol
    owner to postgres;

create unique index trol_rl_abreviacion_uindex
    on demo.trol (rl_abreviacion);

create table demo.tuserrol
(
    usrl_id serial  not null
        constraint tuserrol_pkey
            primary key,
    us_id   integer not null
        constraint tuserrol_tuser_us_id_fk
            references demo.tuser,
    rl_id   integer not null
        constraint tuserrol_trol_rl_id_fk
            references demo.trol
);

alter table demo.tuserrol
    owner to postgres;

create table demo.tcontribuyente
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

comment on column demo.tcontribuyente.cnt_clase is '0-persona natural, 1-especial, 2-rise, 3-regimen simplificado';

comment on column demo.tcontribuyente.cnt_oblcontab is '0-NO, 1-Si';

alter table demo.tcontribuyente
    owner to postgres;

create table demo.tautorizacion
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
            references demo.tcontribuyente,
    aut_secuencia_fin     numeric(9)  not null
);

alter table demo.tautorizacion
    owner to postgres;

create table demo.ttiposdoc
(
    td_id     integer not null
        constraint tiposdoc_pkey
            primary key,
    td_nombre varchar(40)
);

alter table demo.ttiposdoc
    owner to postgres;

create table demo.tclasecontrib
(
    cls_id     serial      not null
        constraint tclasecontrib_pkey
            primary key,
    cls_nombre varchar(80) not null
);

alter table demo.tclasecontrib
    owner to postgres;

create table demo.tjob
(
    job_id                 serial                                      not null
        constraint jobs_pkey
            primary key,
    aut_id                 integer                                     not null
        constraint jobs_tautorizacion_aut_id_fk
            references demo.tautorizacion,
    job_fechacreacion      timestamp                                   not null,
    job_estado             integer                                     not null,
    job_fechaactualizacion timestamp,
    job_nrocopias          integer    default 1                        not null,
    cnt_id                 integer                                     not null
        constraint jobs_tcontribuyente_cnt_id_fk
            references demo.tcontribuyente,
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

alter table demo.tjob
    owner to postgres;

create table demo.tstatusjob
(
    sjb_id     serial      not null
        constraint tstatusjob_pkey
            primary key,
    sjb_nombre varchar(50) not null
);

alter table demo.tstatusjob
    owner to postgres;

create table demo.tplantilla
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

comment on table demo.tplantilla is 'Registra plantillas de reportes de jasperreports';

comment on column demo.tplantilla.temp_tipo is '1:plantilla para factura
2:reporte del sistema';

comment on column demo.tplantilla.temp_params is 'Parametros para la generacion de reportes';

alter table demo.tplantilla
    owner to postgres;

create table demo.taudit
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

comment on table demo.taudit is 'Registra auditoria de las acciones realizadas en el sistema';

comment on column demo.taudit.aud_accion is '0:insert
1:update
2:delete
';

comment on column demo.taudit.aud_userid is 'usuario que realiza la accion';

comment on column demo.taudit.aud_codreg is 'Codigo del registro de la tabla relacionada a la auditoria';

alter table demo.taudit
    owner to postgres;

create unique index taudit_aud_id_uindex
    on demo.taudit (aud_id);

create table demo.ttabla
(
    tbl_id     serial      not null
        constraint ttablas_pk
            primary key,
    tbl_nombre varchar(80) not null
);

comment on table ttabla is 'Registra tablas usadas en el sistema por tema de auditorias';

alter table demo.ttabla
    owner to postgres;

create unique index ttablas_tbl_id_uindex
    on demo.ttabla (tbl_id);

create table demo.tlogos
(
    lg_id serial not null
        constraint tlogos_pk
            primary key,
    logo  bytea
);

alter table demo.tlogos
    owner to postgres;

create unique index tlogos_lg_id_uindex
    on demo.tlogos (lg_id);

create table demo.tjobreprint
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

alter table demo.tjobreprint
    owner to postgres;

create unique index tjobreprint_jobrp_id_uindex
    on demo.tjobreprint (jobrp_id);

create table demo.tjobdoc
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

alter table demo.tjobdoc
    owner to postgres;

create unique index tjobdoc_tjd_id_uindex
    on demo.tjobdoc (tjd_id);

create table demo.tparams
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

alter table demo.tparams
    owner to postgres;

create unique index tparams_tprm_id_uindex
    on tparams (tprm_id);

create unique index tparams_tprm_abrev_uindex
    on tparams (tprm_abrev);

create table demo.tauditaccion
(
    taa_id     integer     not null
        constraint tauditaccion_pk
            primary key,
    taa_accion varchar(20) not null
);

comment on table demo.tauditaccion is 'Acciones realizadas en auditorias';

comment on column demo.tauditaccion.taa_id is 'Clave primaria de la tabla
';

alter table demo.tauditaccion
    owner to postgres;

create unique index tauditaccion_taa_id_uindex
    on tauditaccion (taa_id);

create table demo.ttablacol
(
    ttc_id    serial  not null
        constraint ttablacol_pk
            primary key,
    tbl_id    integer not null,
    ttc_name  text,
    ttc_label text
);

comment on table demo.ttablacol is 'Tabla para registro de columnas por tabla';

comment on column demo.ttablacol.ttc_id is 'clave primaria';

comment on column demo.ttablacol.tbl_id is 'codigo de la tabla';

alter table demo.ttablacol
    owner to postgres;

create unique index ttablacol_ttc_id_uindex
    on demo.ttablacol (ttc_id);

create table demo.tevents
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

comment on table demo.tevents is 'Registra los eventos de la fundacion';

comment on column demo.tevents.ev_estado is '0-valido
1-anulado';

alter table demo.tevents
    owner to postgres;

create unique index tevents_ev_id_uindex
    on demo.tevents (ev_id);

create table demo.ttipoev
(
    tiev_id     serial      not null
        constraint ttipoev_pk
            primary key,
    tiev_nombre varchar(80) not null,
    tiev_img    varchar(50)
);

comment on table demo.ttipoev is 'Registra tipos de evento';

alter table demo.ttipoev
    owner to postgres;

create unique index ttipoev_tiev_id_uindex
    on demo.ttipoev (tiev_id);

create table demo.tlugarev
(
    lugc_id     serial not null
        constraint tlugarev_pk
            primary key,
    lugc_nombre text   not null
);

alter table demo.tlugarev
    owner to postgres;

create unique index tlugarev_lugc_id_uindex
    on demo.tlugarev (lugc_id);

create table demo.tmbmdir
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

alter table demo.tmbmdir
    owner to postgres;

create unique index tmbmdir_idm_uindex
    on demo.tmbmdir (idm);

create table demo.tpersonaevents
(
    pev_id     serial  not null
        constraint tpersonaevents_pk
            primary key,
    per_id     integer not null,
    ev_id      integer not null,
    pev_fecreg timestamp
);

alter table demo.tpersonaevents
    owner to postgres;

create unique index tpersonaevents_pev_id_uindex
    on demo.tpersonaevents (pev_id);

create table demo.tlugar
(
    lug_id     serial            not null
        constraint tlugar_pk
            primary key,
    lug_nombre varchar(250)      not null,
    lug_parent integer,
    lug_status integer default 1 not null
);

comment on column demo.tlugar.lug_status is '1-activo
2-inactivo';

alter table demo.tlugar
    owner to postgres;

create unique index tlugar_lug_id_uindex
    on demo.tlugar (lug_id);

create table demo.tpersona
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
            references demo.tlugar,
    per_ocupacion     integer
);

alter table demo.tpersona
    owner to postgres;

create unique index tpersona_per_id_uindex
    on demo.tpersona (per_id);

create unique index tpersona_perciruc_uindex
    on demo.tpersona (per_ciruc);

create unique index tpersona_peremail_uindex
    on demo.tpersona (per_email);

create table demo.tfuser
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

alter table demo.tfuser
    owner to postgres;

create unique index tfuser_us_id_uindex
    on demo.tfuser (us_id);

create table demo.ttickets
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

comment on table demo.ttickets is 'Tabla para registro de tickets';

alter table demo.ttickets
    owner to postgres;

create unique index ttickets_tk_id_uindex
    on demo.ttickets (tk_id);

create table demo.tclaseitemconfig
(
    clsic_id          serial            not null
        constraint tclaseitemconfig_pk
            primary key,
    clsic_abreviacion varchar(2)        not null,
    clsic_nombre      varchar(40)       not null,
    clsic_estado      integer default 1 not null
);

comment on table demo.tclaseitemconfig is 'Clase  de item de configuracion esto es activo, pasivo , ingreso, gasto';

alter table demo.tclaseitemconfig
    owner to postgres;

create unique index tclaseitemconfig_cic_id_uindex
    on demo.tclaseitemconfig (clsic_id);

create table demo.tcatitemconfig
(
    catic_id     serial            not null
        constraint tcatitemconfig_pk
            primary key,
    catic_nombre varchar(60)       not null,
    catic_estado integer default 1 not null
);

comment on column demo.tcatitemconfig.catic_nombre is 'Nombre de la categoria del item de configuracion';

comment on column demo.tcatitemconfig.catic_estado is '1-activo
2-inactivo';

alter table demo.tcatitemconfig
    owner to postgres;

create unique index tcatitemconfig_catic_id_uindex
    on demo.tcatitemconfig (catic_id);

create unique index tcatitemconfig_catic_id_uindex_2
    on demo.tcatitemconfig (catic_id);

create table demo.ttipoitemconfig
(
    tipic_id     serial            not null
        constraint ttipoitemconfig_pk
            primary key,
    tipic_nombre varchar(80)       not null,
    tipic_estado integer default 1 not null
);

comment on column demo.ttipoitemconfig.tipic_nombre is 'Nombre del tipo de item de configuracion';

comment on column demo.ttipoitemconfig.tipic_estado is 'Estado del tipo de item de configuracion';

alter table demo.ttipoitemconfig
    owner to postgres;

create unique index ttipoitemconfig_tipic_id_uindex
    on demo.ttipoitemconfig (tipic_id);

create table demo.titemconfig
(
    ic_id             serial                                not null
        constraint titemconfig_pk
            primary key,
    ic_nombre         text                                  not null,
    ic_code           text                                  not null,
    ic_padre          integer,
    tipic_id          integer   default 1                   not null
        constraint titemconfig_ttipoitemconfig_tipic_id_fk
            references demo.ttipoitemconfig,
    ic_fechacrea      timestamp default ('now'::text)::date not null,
    ic_usercrea       integer,
    ic_estado         integer   default 1                   not null,
    ic_nota           text,
    catic_id          integer   default 1                   not null
        constraint titemconfig_tcatitemconfig_catic_id_fk
            references demo.tcatitemconfig,
    clsic_id          integer,
    ic_useractualiza  integer,
    ic_fechaactualiza timestamp
);

comment on table demo.titemconfig is 'Representa un articulo un servicio o una cuenta contable';

comment on column demo.titemconfig.ic_nombre is 'Nombre del item de configuracion';

comment on column demo.titemconfig.ic_code is 'Codigo de barra o codigo de la cuenta contable';

comment on column demo.titemconfig.tipic_id is '1-articulo
2-servicio
3-cuenta contable';

comment on column demo.titemconfig.ic_usercrea is 'Usuario que registra este item de configuracion';

comment on column demo.titemconfig.ic_estado is 'Estado del item de configuracion
1-Activo
2-Inactivo';

comment on column demo.titemconfig.ic_nota is 'Nota para al producto, servicio o cuenta contable';

comment on column demo.titemconfig.catic_id is 'Codigo de la categoria del item de configuracion';

comment on column demo.titemconfig.clsic_id is 'Clase del item de configuracion para el caso de cuentas contables';

alter table demo.titemconfig
    owner to postgres;

create unique index titemconfig_ic_code_uindex
    on demo.titemconfig (ic_code);

create unique index titemconfig_ic_id_uindex
    on demo.titemconfig (ic_id);

create table demo.titemconfig_stock
(
    ice_id          serial                   not null
        constraint tpreciosart_pk
            primary key,
    ic_id           integer                  not null
        constraint tpreciosart_titemconfig_ic_id_fk
            references demo.titemconfig,
    sec_id          integer        default 1 not null,
    ice_stock       numeric(10, 2) default 0 not null,
    user_crea       integer                  not null,
    fecha_crea      timestamp                not null,
    user_actualiza  integer,
    fecha_actualiza timestamp
);

alter table demo.titemconfig_stock
    owner to postgres;

create unique index tpreciosart_part_id_uindex
    on demo.titemconfig_stock (ice_id);

create table demo.titemconfig_datosprod
(
    icdp_id             serial                               not null
        constraint tdatosproducto_pk
            primary key,
    ic_id               integer                              not null
        constraint tdatosproducto_titemconfig_ic_id_fk
            references demo.titemconfig,
    icdp_fechacaducidad date,
    icdp_proveedor      integer        default '-2'::integer not null,
    icdp_modcontab      integer
        constraint tdatosproductomodcontablefk
            references demo.titemconfig,
    icdp_preciocompra   numeric(10, 4) default 0.0           not null,
    icdp_precioventa    numeric(10, 4) default 0.0           not null,
    icdp_precioventamin numeric(10, 4) default 0.0           not null,
    icdp_grabaiva       boolean        default false         not null
);

comment on column demo.titemconfig_datosprod.icdp_fechacaducidad is 'Fecha de caducidad del articulo';

alter table demo.titemconfig_datosprod
    owner to postgres;

create unique index tdatosproducto_dprod_id_uindex
    on demo.titemconfig_datosprod (icdp_id);

create table demo.tgrid
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

comment on table demo.tgrid is 'Registra los grids del sistema';

alter table demo.tgrid
    owner to postgres;

create unique index tgrid_grid_id_uindex
    on demo.tgrid (grid_id);

create table demo.tblog
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

alter table demo.tblog
    owner to postgres;

create unique index tblog_blg_id_uindex
    on demo.tblog (blg_id);

create table demo.tseccion
(
    sec_id     serial            not null
        constraint tseccion_pk
            primary key,
    sec_nombre varchar(100)      not null,
    sec_estado integer default 1 not null
);

comment on table demo.tseccion is 'Registra las secciones de una empresa';

comment on column demo.tseccion.sec_estado is '1-activo
2-inactivo';

alter table demo.tseccion
    owner to postgres;

create unique index tseccion_sec_id_uindex
    on demo.tseccion (sec_id);

create table demo.titemconfig_audit
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

comment on table demo.titemconfig_audit is 'Registra los cambios realizados en precios y stock de un producto';

comment on column demo.titemconfig_audit.ica_tipo is 'P-precio
S-stock';

comment on column demo.titemconfig_audit.ica_valantes is 'Valor que tuvo el articulo(stock o precio) antes de relizar el cambio';

comment on column demo.titemconfig_audit.ica_valdespues is 'Valor que tiene el articulo(stock o precio) despues de realizar el cambio';

comment on column demo.titemconfig_audit.sec_id is 'Seccion donde se encuentra el usuario';

alter table demo.titemconfig_audit
    owner to postgres;

create unique index titemconfig_audit_ica_id_uindex
    on demo.titemconfig_audit (ica_id);

create table demo.tuserpaciente
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

comment on column demo.tuserpaciente.up_tipo is '1 - Facebook
2- Google
3- Email';

comment on column demo.tuserpaciente.up_estado is '0 - activo
1 - inactivo';

alter table demo.tuserpaciente
    owner to postgres;

create unique index tuserpaciente_up_id_uindex
    on demo.tuserpaciente (up_id);

create table demo.thorariomedico
(
    hm_id      serial        not null
        constraint thorariomedico_pk
            primary key,
    med_id     integer       not null,
    hm_dia     integer       not null,
    hm_horaini numeric(4, 2) not null,
    hm_horafin numeric(4, 2) not null
);

alter table demo.thorariomedico
    owner to postgres;

create unique index thorariomedico_hm_id_uindex
    on demo.thorariomedico (hm_id);

create table demo.tserviciomedico
(
    tsm_id  serial  not null
        constraint tserviciomedico_pk
            primary key,
    med_id  integer not null,
    serv_id integer not null
);

alter table demo.tserviciomedico
    owner to postgres;

create unique index tserviciomedico_tsm_id_uindex
    on demo.tserviciomedico (tsm_id);

create table demo.tlistavalores
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

comment on table demo.tlistavalores is 'Registra catalogos';

comment on column demo.tlistavalores.lval_estado is '1-activo
2-inactivo';

alter table demo.tlistavalores
    owner to postgres;

create unique index tlistavalores_lval_abrev_uindex
    on demo.tlistavalores (lval_abrev);

create unique index tlistavalores_lval_id_uindex
    on demo.tlistavalores (lval_id);

create table demo.tlistavalores_cat
(
    lvcat_id          serial       not null,
    lvcat_nombre      varchar(100) not null,
    lvcat_abrev       varchar(80)  not null,
    lvcat_descripcion text
);

comment on table demo.tlistavalores_cat is 'Categorias para catalogos';

alter table demo.tlistavalores_cat
    owner to postgres;

create unique index tlistavalores_cat_lvcat_abrev_uindex
    on demo.tlistavalores_cat (lvcat_abrev);

create unique index tlistavalores_cat_lvcat_id_uindex
    on demo.tlistavalores_cat (lvcat_id);

create table demo.tconsultamedica
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
    cosm_odontograma     text,
    cosm_fechaanula      timestamp,
    cosm_obsanula        text,
    cosm_fechaedita      timestamp,
    cosm_useredita       integer,
    cosm_useranula       integer
);

comment on table demo.tconsultamedica is 'Registra consultas medicas';

comment on column demo.tconsultamedica.pac_id is 'Codigo del paciente';

comment on column demo.tconsultamedica.med_id is 'codigo del medico asignado';

comment on column demo.tconsultamedica.cosm_fechacita is 'Fecha de la cita medica';

comment on column demo.tconsultamedica.cosm_enfermactual is 'Enfermedad actual';

comment on column demo.tconsultamedica.cosm_hallazgoexamfis is 'Hallazgos en examenes fisicos';

comment on column demo.tconsultamedica.cosm_exmscompl is 'Examenes complementarios';

comment on column demo.tconsultamedica.cosm_diagnostico is 'Representa el codigo de la enfermedad en la tabla cie10';

comment on column demo.tconsultamedica.cosm_tipo is '1- medica
2- odontologica';

comment on column demo.tconsultamedica.cosm_estado is '1- valido
2- anulado';

alter table demo.tconsultamedica
    owner to postgres;

create unique index tconsultamedica_cosm_id_uindex
    on demo.tconsultamedica (cosm_id);

create table demo.tconsultam_valores
(
    cosm_id     integer not null,
    valcm_id    serial  not null
        constraint tcosm_valores_pk
            primary key,
    valcm_tipo  integer not null,
    valcm_valor text    not null,
    valcm_categ integer not null
);

comment on table demo.tconsultam_valores is 'Antecedentes de la consulta medica';

comment on column demo.tconsultam_valores.valcm_categ is 'antecedentes, revsistemas, diagnostico, examefisico';

alter table demo.tconsultam_valores
    owner to postgres;

create unique index tcosm_valores_valcm_id_uindex
    on demo.tconsultam_valores (valcm_id);

create table demo.tconsultam_cats
(
    catcm_id     serial            not null
        constraint tconsultam_cats_pk
            primary key,
    catcm_nombre varchar(80)       not null,
    catcm_valor  varchar(100)      not null,
    catcm_tipo   integer default 1 not null
);

comment on table demo.tconsultam_cats is 'Categorias para los valores que se registran en una consulta medica';

comment on column demo.tconsultam_cats.catcm_tipo is '1- Medico
2- Odontologo';

alter table demo.tconsultam_cats
    owner to postgres;

create unique index tconsultam_cats_catcm_id_uindex
    on demo.tconsultam_cats (catcm_id);

create table demo.tconsultam_tiposval
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

comment on table demo.tconsultam_tiposval is 'Tipos de valores registrados en consultas medicas';

comment on column demo.tconsultam_tiposval.cmtv_tinput is 'Representa el tipo de input 1: textbox: 2:textarea';

alter table demo.tconsultam_tiposval
    owner to postgres;

create unique index tconsultam_tiposval_cmtv_id_uindex
    on demo.tconsultam_tiposval (cmtv_id);

create table demo.tcie10
(
    cie_id    serial       not null
        constraint cie10_pk
            primary key,
    cie_key   varchar(40)  not null,
    cie_valor varchar(300) not null
);

comment on table demo.tcie10 is 'Codigos de enfermedades';

alter table demo.tcie10
    owner to postgres;

create unique index cie10_cie_id_uindex
    on demo.tcie10 (cie_id);

create unique index cie10_cie_key_uindex
    on demo.tcie10 (cie_key);

create table demo.tconsultam_clasificaval
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

comment on table demo.tconsultam_clasificaval is 'Clasificacion para las lecturas de los examenes fisicos';

alter table demo.tconsultam_clasificaval
    owner to postgres;

create unique index tconsultam_clasificaval_cmcv_id_uindex
    on demo.tconsultam_clasificaval (cmcv_id);

create table demo.tmedico
(
    med_id     serial  not null
        constraint tmedico_pk
            primary key,
    per_id     integer not null,
    med_fecreg timestamp default now()
);

comment on table demo.tmedico is 'Se asocian las personas registradas como medicos';

alter table demo.tmedico
    owner to postgres;

create unique index tmedico_med_id_uindex
    on demo.tmedico (med_id);

create table demo.tmedicoespe
(
    medesp_id     serial            not null
        constraint tmedicoespe_pk
            primary key,
    med_id        integer           not null,
    esp_id        integer           not null,
    medesp_estado integer default 0 not null
);

comment on table demo.tmedicoespe is 'Registra las especialidades de un medico';

comment on column demo.tmedicoespe.medesp_estado is '0-activo
1-inactivo';

alter table demo.tmedicoespe
    owner to postgres;

create unique index tmedicoespe_medesp_id_uindex
    on demo.tmedicoespe (medesp_id);

create table demo.tventatickets
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

comment on column demo.tventatickets.vt_tipo is '1- Venta saraguro
2- Venta cuenca
3- Venta diana
4- Venta jaime';

comment on column demo.tventatickets.vt_estado is '0- borrador
1- confirmado
2- anulado';

comment on column demo.tventatickets.vt_obs is 'observacion';

comment on column demo.tventatickets.vt_clase is 'Clase del asiento ingreso o egreso
1-ingreso
2-gasto';

alter table demo.tventatickets
    owner to postgres;

create unique index tventatickets_vt_id_uindex
    on demo.tventatickets (vt_id);

create table demo.tpermiso
(
    prm_id          serial            not null
        constraint tpermisorol_pk
            primary key,
    prm_nombre      varchar(50)       not null,
    prm_abreviacion varchar(50)       not null,
    prm_detalle     varchar(200),
    prm_estado      integer default 0 not null
);

alter table demo.tpermiso
    owner to postgres;

create unique index tpermisorol_prl_id_uindex
    on demo.tpermiso (prm_id);

create unique index tpermisorol_prl_abreviacion_uindex
    on demo.tpermiso (prm_abreviacion);

create table demo.tpermisorol
(
    prl_id        serial  not null,
    prm_id        integer not null,
    rl_id         integer not null,
    prl_fechacrea timestamp
);

alter table demo.tpermisorol
    owner to postgres;

create table demo.tfuserrol
(
    usrl_id        serial  not null
        constraint tfuserrol_pk
            primary key,
    us_id          integer not null,
    rl_id          integer not null,
    usrl_fechacrea timestamp
);

alter table demo.tfuserrol
    owner to postgres;

create unique index tfuserrol_usrl_id_uindex
    on demo.tfuserrol (usrl_id);

create function demo.inc(val integer) returns integer
    language plpgsql
as
$$
BEGIN
    return val + 1;
END;
$$;

alter function demo.inc(integer) owner to postgres;

create function demo.poner_iva(val numeric) returns numeric
    language plpgsql
as
$$
BEGIN
    return 1.12 * val;
END;
$$;

alter function demo.poner_iva(numeric) owner to postgres;

create function demo.quitar_iva(val numeric) returns numeric
    language plpgsql
as
$$
BEGIN
    return (val + 0.0) / 1.12;
END;
$$;

alter function demo.quitar_iva(numeric) owner to postgres;

create function demo.get_diagnosticos(cosm_diagnosticos text) returns character varying
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
             from demo.tcie10
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

alter function demo.get_diagnosticos(text) owner to postgres;


-- auto-generated definition
create table demo.todantecedentes
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

comment on table demo.todantecedentes is 'Registra antecedentes y examen fisico de un paciente que requiere citas odontologica';

comment on column demo.todantecedentes.od_tipo is '1-antecedentes
2-examen fisico';

comment on column demo.todantecedentes.pac_id is 'Codigo del paciente';

comment on column demo.todantecedentes.od_antestado is '1-valido
2-anulado';

alter table demo.todantecedentes
    owner to postgres;

create unique index tod_antecedentes_od_antid_uindex
    on demo.todantecedentes (od_antid);

create unique index tod_antecedentes_od_antid_uindex_2
    on demo.todantecedentes (od_antid);


-- auto-generated definition
create table demo.todantecedentesval
(
    od_antvid  serial  not null
        constraint todantecedentesval_pk
            primary key,
    od_antid   integer not null
        constraint todantecedentesval_todantecedentes_od_antid_fk
            references demo.todantecedentes,
    cmtv_id    integer not null,
    od_antvval text
);

comment on table demo.todantecedentesval is 'Registra valores para antecedentes odonto';

alter table demo.todantecedentesval
    owner to postgres;

create unique index todantecedentesval_od_antvid_uindex
    on demo.todantecedentesval (od_antvid);


-- auto-generated definition
create table demo.todatenciones
(
    ate_id             serial             not null
        constraint tod_atenciones_pk
            primary key,
    ate_fechacrea      timestamp          not null,
    user_crea          integer            not null,
    pac_id             integer            not null
        constraint todatenciones_tpersona_per_id_fk
            references demo.tpersona,
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

comment on table demo.todatenciones is 'Registra las atenciones realizadas a un paciente';

comment on column demo.todatenciones.ate_estado is '1-Valido
2-Anulado';

comment on column demo.todatenciones.cta_id is 'Codigo de la cita asociada a esta atencion';

comment on column demo.todatenciones.pnt_id is 'Codigo del plan de tratamiento asociado a esta atencion';

alter table demo.todatenciones
    owner to postgres;

create unique index tod_atenciones_ate_id_uindex
    on demo.todatenciones (ate_id);

alter table demo.tconsultam_valores
    add od_antid int;

comment on column demo.tconsultam_valores.od_antid is 'Se usa para relacionar con la tabla todantecedentes';


create table demo.tcita
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

comment on table demo.tcita is 'Tabla para registro de citas medicas';

comment on column demo.tcita.pac_id is 'codigo del paciente';

comment on column demo.tcita.ct_estado is '0-pendiente
1-atendido
2-anulado';

alter table demo.tcita owner to postgres;

create unique index tcita_cita_id_uindex
    on demo.tcita (ct_id);

create unique index tcita_cita_id_uindex_2
    on demo.tcita (ct_id);


create table demo.todrxdocs
(
    rxd_id        serial             not null
        constraint todrxdocs_pk
            primary key,
    rxd_ruta      varchar(500)       not null,
    rxd_ext       varchar(80),
    rxd_nota      text,
    pac_id        integer            not null,
    user_crea     integer            not null,
    rxd_fechacrea timestamp          not null,
    rxd_nropieza  smallint,
    rxd_tipo      integer  default 1 not null,
    rxd_estado    smallint default 1 not null,
    rxd_nombre    varchar(100),
    rxd_filename  varchar(100)
);

comment on table demo.todrxdocs is 'Tabla para registro de rayos x y documentos';

comment on column demo.todrxdocs.rxd_ext is 'pdf, png, doc, e5tc';

comment on column demo.todrxdocs.rxd_nropieza is 'Para el caso de adjuntos asociados a una pieza dental';

comment on column demo.todrxdocs.rxd_tipo is '1-cita medica
2-odonto';

alter table demo.todrxdocs
    owner to postgres;

create unique index todrxdocs_rxd_id_uindex
    on demo.todrxdocs (rxd_id);


alter table demo.tpersona
	add per_tiposangre integer;
