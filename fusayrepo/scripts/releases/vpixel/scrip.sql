INSERT INTO fusay.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea)
VALUES (4, 'rutaPixelLogos', 'rutaPixelLogos', '/opt/mipixel/fileupload', '2020-10-30 07:34:37.000000');

create table fusay.tpixel
(
    px_id            serial        not null,
    px_email         varchar(80)   not null,
    px_fecharegistro timestamp     not null,
    px_row           int           not null,
    px_col           int           not null,
    px_row_end       int           not null,
    px_col_end       int           not null,
    px_costo         numeric(10, 3),
    px_pathlogo      varchar(200),
    px_estado        int default 0 not null,
    px_fechanula    timestamp,
    px_obsanula      text,
    px_fechaconfirma timestamp,
    px_obsconfirma  text,
    px_numpx    int

);
comment on table fusay.tpixel is 'Registra los pixeles comprados';
comment on column fusay.tpixel.px_estado is '0-creado
1-comprado
2-caducado';
create unique index tpixel_px_id_uindex
    on fusay.tpixel (px_id);
alter table fusay.tpixel
    add constraint tpixel_pk
        primary key (px_id);