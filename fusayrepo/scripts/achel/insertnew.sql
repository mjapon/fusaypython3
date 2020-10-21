INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (2, 'tickets', ' select
                a.tk_id,
                a.tk_nro,
                a.tk_dia,
                   p.per_nombres||'' ''||p.per_apellidos as per_nomapel,
                   p.per_ciruc,
                   p.per_email,
                   a.tk_costo,
                   a.tk_estado
            from ttickets a
            join tpersona p on a.tk_perid = p.per_id
            where a.tk_dia = ''{tk_dia}'' and a.sec_id={sec_id} and a.tk_estado=1 order by  a.tk_nro', '[
    {"label":"Nro", "field":"tk_nro"},
    {"label":"Nombres y Apellidos", "field":"per_nomapel"},
    {"label":"#Cedula", "field":"per_ciruc"},
    {"label":"Email", "field":"per_email"},
    {"label":"Costo", "field":"tk_costo"}
]', '2020-03-06 20:38:17.000000', '["tk_id", "tk_nro", "tk_dia", "per_nomapel", "per_ciruc", "per_email", "tk_costo", "tk_estado"]');
INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (1, 'productos', 'select ic.ic_id,
       ic.ic_nombre,
       ic.ic_code,
       ic_nota,
       t.tipic_nombre,
       dp.icdp_grabaiva,
       case dp.icdp_grabaiva when true then ''SI'' else ''NO'' end AS grabaiva,
       dp.icdp_preciocompra,
       case dp.icdp_grabaiva when true then round(PONER_IVA(dp.icdp_preciocompra),2)
        else dp.icdp_preciocompra end as preciocompraiva,
       dp.icdp_precioventa,
       case dp.icdp_grabaiva when true then round(PONER_IVA(dp.icdp_precioventa),2)
        else dp.icdp_precioventa end as precioventaiva,
       dp.icdp_precioventamin,
       dp.icdp_fechacaducidad,
       coalesce(ice.ice_stock, 0) as ice_stock
       from titemconfig ic
join titemconfig_datosprod dp on dp.ic_id = ic.ic_id
join ttipoitemconfig t on ic.tipic_id = t.tipic_id
left join titemconfig_stock ice on ic.ic_id = ice.ic_id and ice.sec_id = {sec_id}
where ic.ic_estado = 1 and ({where}) order by {order}', '[
    {"label":"Código Barra", "field":"ic_code"},
    {"label":"Iva", "field":"grabaiva"},
    {"label":"Pr Compra(Iva)", "field":"preciocompraiva"},
    {"label":"Pr Venta(Iva)", "field":"precioventaiva"},
    {"label":"Fecha caducidad", "field":"icdp_fechacaducidad"},
    {"label":"Stock", "field":"ice_stock"}
]', '2020-02-15 21:24:49.000000', '["ic_id", "ic_nombre", "ic_code", "ic_nota", "tipic_nombre", "icdp_grabaiva", "grabaiva", "icdp_preciocompra","preciocompraiva", "icdp_precioventa","precioventaiva", "icdp_precioventamin", "icdp_fechacaducidad", "ice_stock"]');
INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (3, 'ventatickets', 'select vt_id, vt_fechareg, vt_monto, vt_tipo, ic.ic_nombre, vt_estado,
       case when vt_estado = 0 then ''Pendiente''
            when vt_estado = 1  then ''Confirmado''
            when vt_estado = 2  then ''Anulado'' else ''desc'' end as estadodesc,
       vt_obs, vt_fecha from tventatickets vt
        join titemconfig ic on vt.vt_tipo = ic.ic_id where vt.vt_estado in (0,1) {andwhere}  order by vt_fecha desc', '[
    {"label":"Fecha", "field":"vt_fecha"},
    {"label":"Rubro", "field":"ic_nombre"},
    {"label":"Monto", "field":"vt_monto"},
    {"label":"Estado", "field":"estadodesc"},
    {"label":"Observación", "field":"vt_obs"},
    {"label":"Registro", "field":"vt_fechareg"}
]', '2020-09-14 18:28:47.358814', '["vt_id", "vt_fechareg", "vt_monto", "vt_tipo", "ic_nombre", "vt_estado", "estadodesc", "vt_obs", "vt_fecha"]');
INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (6, 'usuarios', 'select a.us_id, a.us_cuenta, p.per_ciruc, coalesce(p.per_nombres,'''')||'' ''||coalesce(p.per_apellidos,'''') as nomapel,
            case when a.us_estado = 0 then ''ACTIVO'' else ''INACTIVO'' end as estado            
            from tfuser a join tpersona p on a.per_id = p.per_id order by 5 asc', '[
    {"label":"Código", "field":"us_id"},
    {"label":"Cuenta", "field":"us_cuenta"},
    {"label":"Nombre", "field":"nomapel"},
    {"label":"Estado", "field":"estado"}    
]', '2020-10-12 02:10:03.364110', '["us_id", "us_cuenta", "per_ciruc", "nomapel", "estado"]');
INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (5, 'roles', 'select rl_id, rl_name, rl_desc, rl_abreviacion, rl_grupo from trol where rl_estado =0 order by rl_name', '[
    {"label":"Código", "field":"rl_id"},
    {"label":"Abreviación", "field":"rl_abreviacion"},
    {"label":"Nombre", "field":"rl_name"},
    {"label":"Descripción", "field":"rl_desc"}    
]', '2020-10-10 09:52:31.000000', '["rl_id", "rl_name", "rl_desc", "rl_abreviacion", "rl_grupo"]');
INSERT INTO achel.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (7, 'trubros', 'select ic_id, ic_code, ic_nombre, clsic_id, case when clsic_id=1 then ''Ingreso''
    when clsic_id=2 then ''Gasto''
    when clsic_id=3 then ''Patrimonio''
    else ''Desconocido'' end as tipo from titemconfig where
tipic_id = 4 order by clsic_id, ic_nombre asc', '[
    {"label":"Código", "field":"ic_code"},
    {"label":"Nombre", "field":"ic_nombre"},
    {"label":"Tipo", "field":"tipo"}    
]', '2020-10-13 17:26:43.000000', '["ic_id", "ic_code", "ic_nombre", "clsic_id", "tipo"]');





INSERT INTO achel.tpersona (per_id, per_ciruc, per_nombres, per_apellidos, per_direccion, per_telf, per_movil, per_email, per_fecreg, per_tipo, per_lugnac, per_nota, per_fechanac, per_genero, per_estadocivil, per_lugresidencia, per_ocupacion) VALUES (-2, '0000000000', 'SIN PROVEEDOR', null, null, null, '0000000000', null, null, 3, 0, null, null, null, null, null, null);
INSERT INTO achel.tpersona (per_id, per_ciruc, per_nombres, per_apellidos, per_direccion, per_telf, per_movil, per_email, per_fecreg, per_tipo, per_lugnac, per_nota, per_fechanac, per_genero, per_estadocivil, per_lugresidencia, per_ocupacion) VALUES (-1, '9999999999', 'CONSUMIDOR FINAL', null, null, null, '0000000000', null, null, 1, 0, null, null, null, null, null, null);


INSERT INTO achel.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (2, 'artsTickets', 'artsTickets', '6,7,8,9', '2020-09-14 17:53:42.014102');
INSERT INTO achel.tparams (tprm_id, tprm_abrev, tprm_nombre, tprm_val, tprm_fechacrea) VALUES (1, 'artsSeqCodBar', 'artsSeqCodBar', '6', '2020-09-14 12:50:47.000000');


INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (1, 'TK Listar Tickets', 'TK_LISTAR', 'Rol que permite ver y consultar listado de tickets', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (2, 'TK Crear Tickets', 'TK_CREAR', 'Rol que permite crear nuevos tickets', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (3, 'TK Anular Tickets', 'TK_ANULAR', 'Rol que permite anular tickets', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (4, 'PROD Listar Productos', 'PRODS_LISTAR', 'Rol que permite ver y consultar productos y servicios registrados', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (5, 'PROD Ver Detalles Producto', 'PRODS_DET_VIEW', 'Rol que permite ver los detalles de un producto', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (6, 'PROD Editar un producto', 'PRODS_EDIT', 'Rol que permite editar un producto o servicio', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (7, 'PROD Crear un producto', 'PRODS_CREATE', 'Rol que permite crear un producto o servicio', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (8, 'HC Módulo de historias clínicas ', 'HIST_LISTAR', 'Rol que permite acceder a la opcion de historias clinicas', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (9, 'HC Editar historia clínica', 'HIST_EDITAR', 'Rol que permite editar una historia clínica', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (10, 'HC Anular historia clínica', 'HIST_ANULAR', 'Rol que permite anular una historia clínica', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (11, 'HCO Módulo de historias clínicas odontológicas', 'HISTO_LISTAR', 'Rol que permite acceder a la opcionde historias clínicas odontológicas', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (12, 'HCO Editar historia clínica odontológica', 'HISTO_EDITAR', 'Rol que permite editar una historia clínica odontológica', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (13, 'HCO Anular historia clínica odontológica', 'HISTO_ANULAR', 'Rol que permite anular una historia clínica odontológica', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (14, 'RL Listado de roles', 'RL_LISTAR', 'Rol que permite acceder al listado de roles', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (15, 'RL Crear Roles', 'RL_CREAR', 'Rol que permite crear roles', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (16, 'RL Editar Roles', 'RL_EDITAR', 'Rol que permite editar un rol', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (17, 'US Listado de usuarios', 'US_LISTAR', 'Rol que permite acceder al listado de usuarios', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (18, 'US Editar usuario', 'US_EDITAR', 'Rol que permite editar un usuario', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (19, 'IG Listado de ingresos y gastos', 'IG_LISTAR', 'Rol que permite acceder al listado de ingresos y gastos', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (20, 'IG Crear ingreso y gasto', 'IG_CREAR', 'Rol que permite crear un ingreso o gasto', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (21, 'IG Editar ingreso y gasto', 'IG_EDITAR', 'Rol que permite editar un ingreso o gasto', 0);
INSERT INTO achel.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (22, 'IG Confirmar un ingreso y gasto', 'IG_CONFIRMAR', 'Rol que permite confirmar un ingreso o gasto', 0);

INSERT INTO achel.tseccion (sec_id, sec_nombre, sec_estado) VALUES (1, 'SARAGURO', 1);


INSERT INTO achel.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (1, 'PRODUCTO', 1);
INSERT INTO achel.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (2, 'SERVICIO', 1);
INSERT INTO achel.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (3, 'CUENTA CONTABLE', 1);
INSERT INTO achel.ttipoitemconfig (tipic_id, tipic_nombre, tipic_estado) VALUES (4, 'RUBRO', 1);

INSERT INTO achel.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (1, 'GENERO', 'GENERO', null);
INSERT INTO achel.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (2, 'ESTADO CIVIL', 'ESTCIVIL', null);
INSERT INTO achel.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (3, 'PROFESIÓN/OCUPACIÓN', 'PROFOCUP', null);
INSERT INTO achel.tlistavalores_cat (lvcat_id, lvcat_nombre, lvcat_abrev, lvcat_descripcion) VALUES (4, 'ESPECIDALIDAD', 'ESPMED', 'ESPECIALIDAD MEDICA');


INSERT INTO achel.tfuser (us_id, us_cuenta, us_clave, per_id, us_fechacrea, us_estado) VALUES (0, 'admin', 'admin', -1, null, 0);


INSERT INTO achel.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (1, 'ANTECEDENTES', 'ANTECEDENTES', 1);
INSERT INTO achel.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (3, 'EXAMFISICO', 'EXAMEN FÍSICO', 1);
INSERT INTO achel.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (4, 'DIAGNOSTICO', 'DIAGNÓSTICO', 1);
INSERT INTO achel.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (2, 'REVXSISTEMAS', 'REVISIÓN POR SISTEMAS', 1);
INSERT INTO achel.tconsultam_cats (catcm_id, catcm_nombre, catcm_valor, catcm_tipo) VALUES (5, 'ANTCDETS_ODNTO', 'ANTECEDENTES', 2);


INSERT INTO achel.tcatitemconfig (catic_id, catic_nombre, catic_estado) VALUES (1, 'SERVICIOS GENERALES', 1);
INSERT INTO achel.tcatitemconfig (catic_id, catic_nombre, catic_estado) VALUES (2, 'GENERAL', 1);



