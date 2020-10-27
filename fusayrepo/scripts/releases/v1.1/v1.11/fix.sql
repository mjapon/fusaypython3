UPDATE fusay.tgrid SET grid_basesql = 'select  historia.cosm_id,
                historia.cosm_fechacrea,
                extract(month from historia.cosm_fechacrea)           as mescrea,
                to_char(historia.cosm_fechacrea, ''TMMonth'')           as mescreastr,
                to_char(historia.cosm_fechacrea, ''HH24:MI'')           as horacreastr,
                extract(day from historia.cosm_fechacrea)             as diacrea,
                coalesce(paciente.per_genero, 1)                      as genero,
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
        {swhere} order by historia.cosm_fechaproxcita asc', grid_columnas = '[
    {"label":"Dia", "field":"cosm_fechaproxcita"},
    {"label":"Paciente", "field":"paciente"},
    {"label":"Num CI", "field":"per_ciruc"},
    {"label":"Celular", "field":"per_movil"},
    {"label":"Última cita", "field":"cosm_fechacrea"},
    {"label":"Motivo", "field":"cosm_motivo"}
]', grid_tupladesc = '["cosm_id","cosm_fechacrea","mescrea","mescreastr","horacreastr","diacrea","genero","per_ciruc","per_movil","paciente","cosm_motivo","cosm_estado","cosm_fechaproxcita", "per_lugresidencia","lugresidencia"]' WHERE grid_id = 8;