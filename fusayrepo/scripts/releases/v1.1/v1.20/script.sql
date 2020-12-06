--Version registro de asientos

create table fusay.todontograma
(
   od_id serial not null,
   od_fechacrea timestamp not null,
   od_fechaupd timestamp,
   user_upd int,
   user_crea int,
   od_odontograma text,
   od_obsodonto text,
   pac_id int not null,
   od_tipo int default 1 not null,
   od_protesis text
);
comment on table fusay.todontograma is 'Registra los detalles del odontograma';
comment on column fusay.todontograma.user_upd is 'Usuario que actualiza';
create unique index todontograma_od_id_uindex
   on fusay.todontograma (od_id);
alter table fusay.todontograma
   add constraint todontograma_pk
      primary key (od_id);