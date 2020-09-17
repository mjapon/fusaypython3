UPDATE fusay.titemconfig set ic_nombre = 'TICKETS RODRIGO' where ic_code = 'VENTTK_ROD';
UPDATE fusay.titemconfig set ic_nombre = 'TICKETS JAIME' where ic_code = 'VENTTK_JAI';
UPDATE fusay.titemconfig set ic_nombre = 'TICKETS DIANA' where ic_code = 'VENTTK_DIA';

INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('KAMBO RODRIGO', 'VENTKAM_ROD', null, 4, current_date, null, 1, null, 1, null, null, null);
INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('MEDICAMENTOS SARAGURO', 'VENTMED_SARA', null, 4, current_date, null, 1, null, 1, null, null, null);
INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('KAMBÓ SARAGURO', 'VENKAMB_SARA', null, 4, current_date, null, 1, null, 1, null, null, null);
INSERT INTO fusay.titemconfig ( ic_nombre, ic_code, ic_padre, tipic_id, ic_fechacrea, ic_usercrea, ic_estado, ic_nota, catic_id, clsic_id, ic_useractualiza, ic_fechaactualiza) VALUES ('TICKETS SARAGURO', 'VENTICK_SARA', null, 4, current_date, null, 1, null, 1, null, null, null);


