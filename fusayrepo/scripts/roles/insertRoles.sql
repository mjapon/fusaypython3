INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (10, 'HC Anular historia clínica', 'HIST_ANULAR', 'Rol que permite anular una historia clínica', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (9, 'HC Editar historia clínica', 'HIST_EDITAR', 'Rol que permite editar una historia clínica', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (8, 'HC Módulo de historias clínicas ', 'HIST_LISTAR', 'Rol que permite acceder a la opcion de historias clinicas', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (13, 'HCO Anular historia clínica odontológica', 'HISTO_ANULAR', 'Rol que permite anular una historia clínica odontológica', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (12, 'HCO Editar historia clínica odontológica', 'HISTO_EDITAR', 'Rol que permite editar una historia clínica odontológica', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (11, 'HCO Módulo de historias clínicas odontológicas', 'HISTO_LISTAR', 'Rol que permite acceder a la opcionde historias clínicas odontológicas', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (22, 'IG Confirmar un ingreso y gasto', 'IG_CONFIRMAR', 'Rol que permite confirmar un ingreso o gasto', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (20, 'IG Crear ingreso y gasto', 'IG_CREAR', 'Rol que permite crear un ingreso o gasto', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (21, 'IG Editar ingreso y gasto', 'IG_EDITAR', 'Rol que permite editar un ingreso o gasto', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (19, 'IG Listado de ingresos y gastos', 'IG_LISTAR', 'Rol que permite acceder al listado de ingresos y gastos', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (7, 'PROD Crear un producto', 'PRODS_CREATE', 'Rol que permite crear un producto o servicio', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (5, 'PROD Ver Detalles Producto', 'PRODS_DET_VIEW', 'Rol que permite ver los detalles de un producto', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (6, 'PROD Editar un producto', 'PRODS_EDIT', 'Rol que permite editar un producto o servicio', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (4, 'PROD Listar Productos', 'PRODS_LISTAR', 'Rol que permite ver y consultar productos y servicios registrados', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (15, 'RL Crear Roles', 'RL_CREAR', 'Rol que permite crear roles', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (16, 'RL Editar Roles', 'RL_EDITAR', 'Rol que permite editar un rol', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (14, 'RL Listado de roles', 'RL_LISTAR', 'Rol que permite acceder al listado de roles', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (3, 'TK Anular Tickets', 'TK_ANULAR', 'Rol que permite anular tickets', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (2, 'TK Crear Tickets', 'TK_CREAR', 'Rol que permite crear nuevos tickets', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (1, 'TK Listar Tickets', 'TK_LISTAR', 'Rol que permite ver y consultar listado de tickets', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (18, 'US Editar usuario', 'US_EDITAR', 'Rol que permite editar un usuario', 0);
INSERT INTO fusay.tpermiso (prm_id, prm_nombre, prm_abreviacion, prm_detalle, prm_estado) VALUES (17, 'US Listado de usuarios', 'US_LISTAR', 'Rol que permite acceder al listado de usuarios', 0);

INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (5, 'roles', 'select rl_id, rl_name, rl_desc, rl_abreviacion, rl_grupo from trol where rl_estado =0 order by rl_name', '[
    {"label":"Código", "field":"rl_id"},
    {"label":"Abreviación", "field":"rl_abreviacion"},
    {"label":"Nombre", "field":"rl_name"},
    {"label":"Descripción", "field":"rl_desc"}    
]', '2020-10-10 09:52:31.000000', '["rl_id", "rl_name", "rl_desc", "rl_abreviacion", "rl_grupo"]');
INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (6, 'usuarios', 'select a.us_id, a.us_cuenta, p.per_ciruc, coalesce(p.per_nombres,'''')||'' ''||coalesce(p.per_apellidos,'''') as nomapel,
            case when a.us_estado = 0 then ''ACTIVO'' else ''INACTIVO'' end as estado            
            from tfuser a join tpersona p on a.per_id = p.per_id order by 5 asc', '[
    {"label":"Código", "field":"us_id"},
    {"label":"Cuenta", "field":"us_cuenta"},
    {"label":"Nombre", "field":"nomapel"},
    {"label":"Estado", "field":"estado"}    
]', '2020-10-12 02:10:03.364110', '["us_id", "us_cuenta", "per_ciruc", "nomapel", "estado"]');