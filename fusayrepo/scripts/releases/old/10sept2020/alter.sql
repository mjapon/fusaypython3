UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'FECHA ÚLTIMA MENSTRUACIÓN (dd/mm/aaaa)', cmtv_tinput=3 where cmtv_nombre = 'ANT_FUM';
UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'GESTAS' where cmtv_nombre ='ANT_G';
UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'PARTOS' where cmtv_nombre ='ANT_P';
UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'ABORTOS' where cmtv_nombre ='ANT_A';
UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'HIJOS VIVOS' where cmtv_nombre ='ANT_HV';
UPDATE fusay.tconsultam_tiposval SET cmtv_valor = 'HIJOS MUERTOS' where cmtv_nombre ='ANT_HM';

INSERT INTO fusay.tconsultam_tiposval (cmtv_id, cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (28, 1, 'ANT_C', 'CESÁREAS', 1, 7, null);

--cambios a la fecha 08 sept
alter table fusay.tconsultamedica add cosm_diagnosticos varchar(50);
update fusay.tconsultamedica set cosm_diagnosticos = cosm_diagnostico::varchar(50) where cosm_diagnostico is not null;

--Se cambia el orden para agregar el tipo CARDIO-RESPIRATORIO
UPDATE fusay.tconsultam_tiposval set cmtv_orden = cmtv_orden+1 where  cmtv_cat = 2 and cmtv_orden>=4;

--Se agrega el tipo CARDIO-RESPIRATORIO
INSERT INTO fusay.tconsultam_tiposval (cmtv_id, cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (29, 2, 'RS_CR', 'CARDIO-RESPIRATORIO', 2, 4, null);

UPDATE fusay.tlistavalores set lval_nombre = 'SOLTERO/A' WHERE lval_abrev = 'ESTCV_SOLT';
UPDATE fusay.tlistavalores set lval_nombre = 'CASADO/A' WHERE lval_abrev = 'ESTCV_CASAD';
UPDATE fusay.tlistavalores set lval_nombre = 'DIVORCIADO/A' WHERE lval_abrev = 'ESTCV_DIVC';
UPDATE fusay.tlistavalores set lval_nombre = 'VIUDO/A' WHERE lval_abrev = 'ESTCV_VIUD';