INSERT INTO demo.tpersona (per_id, per_ciruc, per_nombres, per_apellidos, per_direccion, per_telf, per_movil, per_email, per_fecreg, per_tipo, per_lugnac, per_nota, per_fechanac, per_genero, per_estadocivil, per_lugresidencia, per_ocupacion) VALUES (-2, '0000000000', 'SIN PROVEEDOR', null, null, null, '0000000000', null, null, 3, 0, null, null, null, null, null, null);
INSERT INTO demo.tpersona (per_id, per_ciruc, per_nombres, per_apellidos, per_direccion, per_telf, per_movil, per_email, per_fecreg, per_tipo, per_lugnac, per_nota, per_fechanac, per_genero, per_estadocivil, per_lugresidencia, per_ocupacion) VALUES (-1, '9999999999', 'CONSUMIDOR FINAL', null, null, null, '0000000000', null, null, 1, 0, null, null, null, null, null, null);


INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (2, 'porciva', 'porciva', '0.12', '2020-02-15 12:57:28.000000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (3, 'artsTickets', 'artsTickets', '1,2,3,4', '2020-03-06 20:26:39.000000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (4, 'artsSeqCodBar', 'Secuencial para codigo de producto o servicio', '5', '2020-03-18 20:27:35.808000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (7, 'rutaReceta', 'rutaReceta', '/opt/reportes/mavil/recetareport.jrxml', '2020-12-24 08:57:00.000000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (8, 'rutaRecetaOd', 'rutaRecetaOd', '/opt/reportes/mavil/recetaodreport.jrxml', '2020-12-24 08:58:07.000000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (9, 'pathFondoRec', 'pathFondoRec', '/opt/reportes/mavil/fondorecetario.png', '2020-12-24 09:36:37.000000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (10, 'pathFondoRecOd', 'pathFondoRecOd', '/opt/reportes/mavil/fondorecetariood.png', '2020-12-24 14:37:47.170000');
INSERT INTO demo.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (11, 'rutaRaizRxDocs', 'rutaRaizRxDocs', '/opt/mavildocs/demo', '2020-12-24 17:42:45.000000');


INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (1, 'TK Listar Tickets', 'TK_LISTAR', 'Rol que permite ver y consultar listado de tickets', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (2, 'TK Crear Tickets', 'TK_CREAR', 'Rol que permite crear nuevos tickets', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (3, 'TK Anular Tickets', 'TK_ANULAR', 'Rol que permite anular tickets', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (4, 'PROD Listar Productos', 'PRODS_LISTAR', 'Rol que permite ver y consultar productos y servicios registrados', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (5, 'PROD Ver Detalles Producto', 'PRODS_DET_VIEW', 'Rol que permite ver los detalles de un producto', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (6, 'PROD Editar un producto', 'PRODS_EDIT', 'Rol que permite editar un producto o servicio', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (7, 'PROD Crear un producto', 'PRODS_CREATE', 'Rol que permite crear un producto o servicio', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (8, 'HC Módulo de historias clínicas ', 'HIST_LISTAR', 'Rol que permite acceder a la opcion de historias clinicas', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (9, 'HC Editar historia clínica', 'HIST_EDITAR', 'Rol que permite editar una historia clínica', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (10, 'HC Anular historia clínica', 'HIST_ANULAR', 'Rol que permite anular una historia clínica', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (11, 'HCO Módulo de historias clínicas odontológicas', 'HISTO_LISTAR', 'Rol que permite acceder a la opcionde historias clínicas odontológicas', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (12, 'HCO Editar historia clínica odontológica', 'HISTO_EDITAR', 'Rol que permite editar una historia clínica odontológica', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (13, 'HCO Anular historia clínica odontológica', 'HISTO_ANULAR', 'Rol que permite anular una historia clínica odontológica', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (14, 'RL Listado de roles', 'RL_LISTAR', 'Rol que permite acceder al listado de roles', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (15, 'RL Crear Roles', 'RL_CREAR', 'Rol que permite crear roles', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (16, 'RL Editar Roles', 'RL_EDITAR', 'Rol que permite editar un rol', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (17, 'US Listado de usuarios', 'US_LISTAR', 'Rol que permite acceder al listado de usuarios', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (18, 'US Editar usuario', 'US_EDITAR', 'Rol que permite editar un usuario', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (19, 'IG Listado de ingresos y gastos', 'IG_LISTAR', 'Rol que permite acceder al listado de ingresos y gastos', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (20, 'IG Crear ingreso y gasto', 'IG_CREAR', 'Rol que permite crear un ingreso o gasto', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (21, 'IG Editar ingreso y gasto', 'IG_EDITAR', 'Rol que permite editar un ingreso o gasto', 0);
INSERT INTO demo.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (22, 'IG Confirmar un ingreso y gasto', 'IG_CONFIRMAR', 'Rol que permite confirmar un ingreso o gasto', 0);

INSERT INTO demo.tseccion (sec_id, sec_nombre, sec_estado) VALUES (1, 'PRINCIPAL', 1);

INSERT INTO demo.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (1, 'PRODUCTO', 1);
INSERT INTO demo.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (2, 'SERVICIO', 1);
INSERT INTO demo.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (3, 'CUENTA CONTABLE', 1);
INSERT INTO demo.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (4, 'RUBRO', 1);

INSERT INTO demo.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (1, 'GENERO', 'GENERO', null);
INSERT INTO demo.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (2, 'ESTADO CIVIL', 'ESTCIVIL', null);
INSERT INTO demo.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (3, 'PROFESIÓN/OCUPACIÓN', 'PROFOCUP', null);
INSERT INTO demo.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (4, 'TIPO DE SANGRE', 'TIPOSANGRE', null);

INSERT INTO demo.tfuser (us_id, us_cuenta, us_clave, per_id, us_fechacrea, us_estado) VALUES (0, 'admin', 'admin', -1, null, 0);

INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (1, 'ANTECEDENTES', 'ANTECEDENTES', 1);
INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (3, 'EXAMFISICO', 'EXAMEN FÍSICO', 1);
INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (4, 'DIAGNOSTICO', 'DIAGNÓSTICO', 1);
INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (2, 'REVXSISTEMAS', 'REVISIÓN POR SISTEMAS', 1);
INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (5, 'ANTECEDENTES_OD', 'ANTECEDENTES',2);
INSERT INTO demo.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (6, 'EXAMFISICO_OD', 'EXAMEN FÍSICO',2);

INSERT INTO demo.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_PERSONALES', 'PERSONALES', 2, 1, null);
INSERT INTO demo.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_FAMILIAREAS', 'FAMILIARES', 2, 2, null);
INSERT INTO demo.tconsultam_tiposval (cmtv_cat, cmtv_nombre, cmtv_valor, cmtv_tinput, cmtv_orden, cmtv_unidad) VALUES (5, 'ANTO_ALERGICOS', 'ALÉRGICOS', 2, 3, null);


INSERT INTO demo.tcatitemconfig (catic_id, catic_nombre, catic_estado) VALUES (1, 'NINGUNO', 1);
INSERT INTO demo.tcatitemconfig (catic_id, catic_nombre, catic_estado) VALUES (2, 'GENERAL', 1);

