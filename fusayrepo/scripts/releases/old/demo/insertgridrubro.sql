create or replace function demo.parse_hora(val numeric ) returns varchar
    language plpgsql
as
$$
declare decimales numeric;
BEGIN
    decimales:= val%1;
    return lpad(trunc(val)::varchar,2,'0')||':'|| lpad( trunc(decimales*60)::varchar,2,'0');
END;
$$;

alter function demo.parse_hora(numeric) owner to postgres;


INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (1, 'productos', 'select ic.ic_id,
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
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (2, 'tickets', ' select
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
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (3, 'ventatickets', 'select vt_id, vt_fechareg, vt_monto, vt_tipo, ic.ic_nombre, vt_estado,
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
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (5, 'roles', 'select rl_id, rl_name, rl_desc, rl_abreviacion, rl_grupo from trol where rl_estado =0 order by rl_name', '[
    {"label":"Código", "field":"rl_id"},
    {"label":"Abreviación", "field":"rl_abreviacion"},
    {"label":"Nombre", "field":"rl_name"},
    {"label":"Descripción", "field":"rl_desc"}
]', '2020-10-10 09:52:31.000000', '["rl_id", "rl_name", "rl_desc", "rl_abreviacion", "rl_grupo"]');
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (6, 'usuarios', 'select a.us_id, a.us_cuenta, p.per_ciruc, coalesce(p.per_nombres,'''')||'' ''||coalesce(p.per_apellidos,'''') as nomapel,
            case when a.us_estado = 0 then ''ACTIVO'' else ''INACTIVO'' end as estado
            from tfuser a join tpersona p on a.per_id = p.per_id order by 5 asc', '[
    {"label":"Código", "field":"us_id"},
    {"label":"Cuenta", "field":"us_cuenta"},
    {"label":"Nombre", "field":"nomapel"},
    {"label":"Estado", "field":"estado"}
]', '2020-10-12 02:10:03.364110', '["us_id", "us_cuenta", "per_ciruc", "nomapel", "estado"]');
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (7, 'trubros', 'select ic_id, ic_code, ic_nombre, clsic_id, case when clsic_id=1 then ''Ingreso''
    when clsic_id=2 then ''Gasto''
    when clsic_id=3 then ''Patrimonio''
    else ''Desconocido'' end as tipo from titemconfig where
tipic_id = 4 order by clsic_id, ic_nombre asc', '[
    {"label":"Código", "field":"ic_code"},
    {"label":"Nombre", "field":"ic_nombre"},
    {"label":"Tipo", "field":"tipo"}
]', '2020-10-13 17:26:43.000000', '["ic_id", "ic_code", "ic_nombre", "clsic_id", "tipo"]');
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (8, 'proxcitas', 'select  historia.cosm_id,
                historia.cosm_fechacrea,
                extract(month from historia.cosm_fechacrea)           as mescrea,
                to_char(historia.cosm_fechacrea, ''TMMonth'')           as mescreastr,
                to_char(historia.cosm_fechacrea, ''HH24:MI'')           as horacreastr,
                extract(day from historia.cosm_fechacrea)             as diacrea,
                coalesce(paciente.per_genero, 1)                      as genero,
                paciente.per_id,
                paciente.per_ciruc,
                paciente.per_movil,
                paciente.per_nombres || '' '' || paciente.per_apellidos as paciente,
                historia.cosm_motivo,
                historia.cosm_estado,
                historia.cosm_fechaproxcita,
                paciente.per_lugresidencia,
                coalesce(tlugar.lug_nombre,'''') as lugresidencia
        from tconsultamedica historia
                join tpersona paciente on historia.pac_id = paciente.per_id
                left join tlugar on paciente.per_lugresidencia = tlugar.lug_id
        where historia.cosm_estado = 1 and date(historia.cosm_fechaproxcita) >= date(current_date)
        {swhere} order by historia.cosm_fechaproxcita asc', '[
    {"label":"Dia", "field":"cosm_fechaproxcita"},
    {"label":"Paciente", "field":"paciente"},
    {"label":"Num CI", "field":"per_ciruc"},
    {"label":"Celular", "field":"per_movil"},
    {"label":"Última cita", "field":"cosm_fechacrea"},
    {"label":"Motivo", "field":"cosm_motivo"}
]', '2020-10-13 17:26:43.000000', '["cosm_id","cosm_fechacrea","mescrea","mescreastr","horacreastr","diacrea","genero","per_id","per_ciruc","per_movil","paciente","cosm_motivo","cosm_estado","cosm_fechaproxcita", "per_lugresidencia","lugresidencia"]');
INSERT INTO demo.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (9, 'proxcitasod', 'select  cita.ct_id,
        cita.ct_fecha,
       parse_hora(cita.ct_hora)||'' - ''||parse_hora(cita.ct_hora_fin) as hora,
        paciente.per_ciruc,
        paciente.per_movil,
        paciente.per_nombres || '' '' || paciente.per_apellidos as paciente,
        cita.ct_titulo,
        paciente.per_lugresidencia,
        coalesce(tlugar.lug_nombre,'''') as lugresidencia,
        atencion.ate_fechacrea,
        coalesce(atencion.ate_id,0) as ate_id,
        coalesce(atencion.ate_diagnostico) as motivo
from tcita cita
        join tpersona paciente on cita.pac_id = paciente.per_id
        left join tlugar on paciente.per_lugresidencia = tlugar.lug_id
        left join todatenciones atencion on atencion.pac_id = paciente.per_id
        and atencion.ate_id = (select max(ate_id) from todatenciones at where at.pac_id = paciente.per_id and at.ate_estado = 1 )
where cita.ct_estado <> 2 and date(cita.ct_fecha) >= date(  current_date)
{swhere} order by cita.ct_fecha asc', '[
    {"label":"Dia", "field":"ct_fecha"},
    {"label":"Hora", "field":"hora"},
    {"label":"Paciente", "field":"paciente"},
    {"label":"Motivo", "field":"ct_titulo"},
    {"label":"Celular", "field":"per_movil"}
]', '2020-10-13 17:26:43.000000', '["ct_id","ct_fecha","hora","per_ciruc","per_movil","paciente","ct_titulo","per_lugresidencia","lugresidencia","ate_fechacrea","ate_id","motivo"]');