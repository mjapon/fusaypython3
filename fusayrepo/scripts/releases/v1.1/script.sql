INSERT INTO fusay.tgrid (grid_id, grid_nombre, grid_basesql, grid_columnas, grid_fechacrea, grid_tupladesc) VALUES (8, 'proxcitas', 'select  historia.cosm_id,
                historia.cosm_fechacrea,
                extract(month from historia.cosm_fechacrea)           as mescrea,
                to_char(historia.cosm_fechacrea, ''TMMonth'')           as mescreastr,
                to_char(historia.cosm_fechacrea, ''HH24:MI'')           as horacreastr,
                extract(day from historia.cosm_fechacrea)             as diacrea,
                coalesce(paciente.per_genero, 1)                      as genero,
                paciente.per_ciruc,
                paciente.per_nombres || '' '' || paciente.per_apellidos as paciente,
                historia.cosm_motivo,
                historia.cosm_estado,
                historia.cosm_fechaproxcita,
                paciente.per_lugresidencia,
                coalesce(tlugar.lug_nombre,'''') as lugresidencia
        from tconsultamedica historia
                join tpersona paciente on historia.pac_id = paciente.per_id
                left join tlugar on paciente.per_lugresidencia = tlugar.lug_id
        where historia.cosm_estado = 1 and historia.cosm_fechaproxcita > current_date
        {swhere} order by historia.cosm_fechaproxcita asc', '[
    {"label":"Dia", "field":"cosm_fechaproxcita"},
    {"label":"Paciente", "field":"paciente"},
    {"label":"Ci/ruc", "field":"per_ciruc"},
    {"label":"Última cita", "field":"cosm_fechacrea"},
    {"label":"Motivo", "field":"cosm_motivo"}
]', '2020-10-13 17:26:43.000000', '["cosm_id","cosm_fechacrea","mescrea","mescreastr","horacreastr","diacrea","genero","per_ciruc","paciente","cosm_motivo","cosm_estado","cosm_fechaproxcita", "per_lugresidencia","lugresidencia"]');





