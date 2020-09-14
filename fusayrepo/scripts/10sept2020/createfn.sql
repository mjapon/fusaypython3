create or replace function get_diagnosticos(cosm_diagnosticos text) returns varchar
    language plpgsql
as
$$
    declare
        diagnosticos text;
BEGIN
    SELECT string_agg(diagnostico::text, ',') into diagnosticos from (
                                                   select '(' || cie_key || ')' || cie_valor as diagnostico
                                                   from fusay.tcie10
                                                   where cie_id in (
                                                       with the_data(str) as (
                                                           select cosm_diagnosticos::text
                                                       )
                                                       select elem::int
                                                       from the_data, unnest(string_to_array(str, ',')) elem
                                                   )
                                               ) as tabla;

    return diagnosticos;
END;
$$;