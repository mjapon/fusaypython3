alter table fusay.tconsultamedica
   add cosm_fechaanula timestamp;
comment on column fusay.tconsultamedica.cosm_fechaanula is 'fecha de anulacion de la historia clinica';
alter table fusay.tconsultamedica
   add cosm_obsanula text;

alter table fusay.tconsultamedica
   add cosm_fechaedita timestamp;

alter table fusay.tconsultamedica
   add cosm_useredita int;
alter table fusay.tconsultamedica
   add cosm_useranula int;