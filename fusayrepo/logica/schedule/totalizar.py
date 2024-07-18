# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from fusayrepo.utils import fechas, ctes


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def generar_sumatoria_dias(dbsess, last_saldo, fecha_ini_db, fecha_fn_db):
    sql_all_saldos = """                            
      select scd_dia,scd_id,
        coalesce(sum(scd_debe) over (order by scd_dia asc rows between unbounded preceding and current row), 0) as debe,
        coalesce(sum(scd_haber) over (order by scd_dia asc rows between unbounded preceding and current row), 0) as haber,
        coalesce(sum(scd_saldo) over (order by scd_dia asc rows between unbounded preceding and current row), 0) as saldo
        from tsaldos_ctas_diario where scd_mayorizado = false and scd_dia>='{0}' and cta_id = {1} order by scd_dia asc
                                """.format(fecha_ini_db, cta_id)

    tupla_desc = ('scd_dia', 'scd_id', 'debe', 'haber', 'saldo')

    saldos_for_cuenta = dbsess.query(*tupla_desc).from_statement(text(sql_all_saldos)).all()

    saldos_for_cuenta_map = {}
    for saldo_it in saldos_for_cuenta:
        debe = saldo_it[2] + last_saldo['debe']
        haber = saldo_it[3] + last_saldo['haber']
        saldo = saldo_it[4] + last_saldo['saldo']
        scd_id = saldo_it[1]

        saldos_for_cuenta_map[saldo_it[0]] = {'debe': debe, 'haber': haber, 'saldo': saldo, 'scd_id': scd_id}

    # Generamos un array de rango de fechas
    sql_range_dates = "SELECT date(generate_series('{0}'::date, '{1}'::date, '1 day')) as fecha".format(
        fecha_ini_db, fecha_fn_db)
    date_ranges = dbsess.query(*('fecha',)).from_statement(text(sql_range_dates)).all()

    # last_saldo= [0, 0, 0, 0, 0]
    for date_it_row in date_ranges:
        date_it = date_it_row[0]
        if date_it in saldos_for_cuenta_map:
            last_saldo = saldos_for_cuenta_map[date_it]

        sql_insert = """select public.fn_create_sumctasdiario({0},'{1}',{2},{3},{4},{5}) as mayor_res
                                                        """.format(cta_id, date_it,
                                                                   last_saldo['debe'],
                                                                   last_saldo['haber'],
                                                                   last_saldo['saldo'],
                                                                   last_saldo['scd_id']
                                                                   )
        tupla_desc = ('mayor_res',)
        result = dbsession.query(*tupla_desc).from_statement(text(sql_insert)).first()


if __name__ == "__main__":

    logging.basicConfig(handlers=[RotatingFileHandler(filename="/var/log/totalizamavil.log",
                                                      mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y%I:%M:%S %p')

    log = logging.getLogger('my_logger')

    log.info('Inicia Proceso totalizacion saldos diarios--------->')

    dbsession = None
    engine = None
    try:
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/imprentadb')
        session_factory = get_session_factory(engine)
        dbsession = session_factory()

        esquemas_procesar = [
            'cajaruna', 'cajainti', 'fusay', 'achel', 'cajademo'
        ]

        for esquema in esquemas_procesar:
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))

            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                fecha_fin_db = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
                # fecha_fin_db = "2023-12-31"

                log.info('Fecha ejecucion proceso:{0}'.format(fecha_fin_db))

                sql = "select distinct(cta_id) as cta_id from tsaldos_ctas_diario tcd order by 1"
                tupla_desc = ('cta_id',)
                ctas_res = dbsession.query(*tupla_desc).from_statement(text(sql)).all()

                # Obtener datos del periodo contable actual:
                sql = "select date(pc_desde) as pc_desde  from tperiodocontable where pc_activo = true limit 1"
                tupla_desc = ('pc_desde',)
                pc_desde_res = dbsession.query(*tupla_desc).from_statement(text(sql)).first()

                if pc_desde_res is not None and pc_desde_res[0] is not None:

                    for cta_id_row in ctas_res:
                        cta_id = cta_id_row[0]

                        log.info('Se procesa la cta_id:{0}'.format(cta_id))

                        sql_date_cta = "select max(mcd_dia) as mcd_dia from tsum_ctas_diario where cta_id  = {0}".format(
                            cta_id)
                        scd_max_dia_res = dbsession.query(*("mcd_dia",)).from_statement(text(sql_date_cta)).first()

                        fecha_inicio = pc_desde_res[0]
                        es_carga_inicial = True
                        if scd_max_dia_res is not None and scd_max_dia_res[0] is not None:
                            fecha_inicio = scd_max_dia_res[0]
                            es_carga_inicial = False

                        fecha_inicio_db = fechas.parse_fecha(fecha_inicio, formato=ctes.APP_FMT_FECHA_DB)
                        if es_carga_inicial:
                            generar_sumatoria_dias(dbsess=dbsession,
                                                   last_saldo={'scd_dia': 0, 'scd_id': 0, 'debe': 0, 'haber': 0,
                                                               'saldo': 0},
                                                   fecha_ini_db=fecha_inicio_db, fecha_fn_db=fecha_fin_db)

                        else:
                            # Verificamos si no exite registra para la fecha actual
                            sql_check_current_date = """select mcd_id from tsum_ctas_diario 
                            where cta_id = {0} and mcd_dia = '{1}'""".format(cta_id, fecha_fin_db)

                            row_current_date = dbsession.query(*('mcd_id',)).from_statement(
                                text(sql_check_current_date)).first()
                            if row_current_date is None or row_current_date[0] is None:

                                # No es carga inicial traer registro del ultimo dia
                                sql_sum_dia_anterior = """select mcd_dia, 
                                coalesce(mcd_debe,0) as mcd_debe, 
                                coalesce(mcd_haber,0) as mcd_haber,
                                coalesce(mcd_saldo,0) as mcd_saldo  
                                from tsum_ctas_diario where cta_id = {0} and mcd_dia ='{1}' order by mcd_dia desc limit 1
                                """.format(cta_id, fecha_inicio_db)

                                tupla_desc = ('mcd_dia', 'mcd_debe', 'mcd_haber', 'mcd_saldo')
                                row_dia_anterior = dbsession.query(*tupla_desc).from_statement(
                                    text(sql_sum_dia_anterior)).first()
                                if row_dia_anterior is not None and row_dia_anterior[0] is not None:
                                    mcd_debe = row_dia_anterior[1]
                                    mcd_haber = row_dia_anterior[2]
                                    mcd_saldo = row_dia_anterior[3]
                                    scd_id = row_dia_anterior[0]
                                    fecha_ini_sum = fechas.sumar_dias(fecha_inicio, 1)
                                    generar_sumatoria_dias(dbsess=dbsession,
                                                           last_saldo={'scd_dia': 0, 'scd_id': scd_id, 'debe': mcd_debe,
                                                                       'haber': mcd_haber, 'saldo': mcd_saldo},
                                                           fecha_ini_db=fechas.parse_fecha(fecha_ini_sum,
                                                                                           formato=ctes.APP_FMT_FECHA_DB),
                                                           fecha_fn_db=fecha_fin_db)

                        dbsession.commit()
                else:
                    log.info('No hay periodo contable activo, favor verificar')
            except Exception as exs:
                log.error('Error al procesar esquema:{0}'.format(exs))

    except Exception as ex:
        log.error('Ucurrio un error al totalizar {0}'.format(ex))
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<--------------------Termina proceso totalizacion')
