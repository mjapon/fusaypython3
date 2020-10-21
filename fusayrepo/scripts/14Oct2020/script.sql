SELECT setval(pg_get_serial_sequence('fusay.tfuser', 'us_id'), coalesce(max(us_id),0) + 1, false) FROM fusay.tfuser;
SELECT setval(pg_get_serial_sequence('fusay.tpersona', 'per_id'), coalesce(max(per_id),0) + 1, false) FROM fusay.tpersona;

--Agregar el script para insertar el grid de tiposrubros
INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (7, 'trubros', 'select ic_id, ic_code, ic_nombre, clsic_id, case when clsic_id=1 then ''Ingreso''
    when clsic_id=2 then ''Gasto''
    when clsic_id=3 then ''Patrimonio''
    else ''Desconocido'' end as tipo from titemconfig where
tipic_id = 4 order by clsic_id, ic_nombre asc', '[
    {"label":"Código", "field":"ic_code"},
    {"label":"Nombre", "field":"ic_nombre"},
    {"label":"Tipo", "field":"tipo"}
]', '2020-10-13 17:26:43.000000', '["ic_id", "ic_code", "ic_nombre", "clsic_id", "tipo"]');

