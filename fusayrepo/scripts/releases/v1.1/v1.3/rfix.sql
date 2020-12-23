-- auto-generated definition
create table fusay.tmedico
(
    med_id     serial            not null
        constraint tmedico_pk
            primary key,
    per_id     integer           not null,
    med_tipo   integer default 1 not null,
    med_espe   integer,
    med_estado integer default 1 not null
);
comment on column fusay.tmedico.med_tipo is '1-medicos
2-odontologo';
comment on column fusay.tmedico.med_espe is 'Codigo de la especialidad del medico
';
comment on column fusay.tmedico.med_estado is '1-activo
2-inactivo';
alter table fusay.tmedico
    owner to postgres;
create unique index tmedico_md_id_uindex
    on fusay.tmedico (med_id);



INSERT INTO fusay.tmedico (med_id, per_id, med_tipo, med_espe, med_estado) VALUES (1, 11, 2, null, 1);
INSERT INTO fusay.tmedico (med_id, per_id, med_tipo, med_espe, med_estado) VALUES (2, 12, 2, null, 1);