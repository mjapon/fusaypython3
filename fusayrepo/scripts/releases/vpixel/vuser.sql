create table fusay.tpxuser
(
    pxus_id        serial            not null
        constraint tpxuser_pk
            primary key,
    pxus_cuenta    varchar(20)       not null,
    pxus_clave     varchar(20)       not null,
    pxus_nombre    varchar(100)      not null,
    pxus_email     varchar(80)       not null,
    pxus_fechacrea timestamp,
    pxus_estado    integer default 0 not null
);
alter table fusay.tpxuser
    owner to postgres;
create unique index tpxuser_pxus_id_uindex
    on fusay.tpxuser (pxus_id);

alter table fusay.tpixel
    add px_texto varchar(50);


INSERT INTO fusay.tpxuser (pxus_id, pxus_cuenta, pxus_clave, pxus_nombre, pxus_email, pxus_fechacrea, pxus_estado) VALUES (1, 'admin', 'admin', 'MANUEL JAPON', 'efrain.japon@gmail.com', '2020-11-12 15:58:10.000000', 0);