# coding: utf-8
"""
Fecha de creacion 18/06/2024
@autor: Manuel Japon
"""
import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy import create_engine, text

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.schedule import dbutils
from fusayrepo.logica.schedule.dbutils import get_session_factory
from fusayrepo.utils import fechas, ctes

ruta_logs = '/var/log/totalizabilletaras.log'
#ruta_logs = 'C:\\dev\\mavil\\logs\\totalizabilletaras.log'


def get_fecha_inicio_contab(sec_id):
    sql = f"select tprm_val from tparams where tprm_abrev = 'fecha_ini_contab' and tprm_seccion = {sec_id} "
    result = dbsession.execute(text(sql)).fetchone()
    fec_ini_contabdb = ''
    if result is not None and len(result) > 0:
        fec_ini_contabdb = " and date(asi.trn_fecha)>='{0}' ".format(fechas.format_cadena_db(result[0]))
    return fec_ini_contabdb


def get_bills():
    sql = """
    select bil.ic_id, sec.sec_id from tbilletera bil  join titemconfig_sec sec 
        on bil.ic_id  = sec.ic_id where bil.bil_estado  = 1
    """
    resultados = dbsession.execute(text(sql))
    bills = resultados.fetchall()
    bills_map = {}
    for bilrow in bills:
        bil_cta = bilrow[0]
        bil_sec = bilrow[1]
        if bil_cta not in bills_map:
            bills_map[bil_cta] = []
        bills_map[bil_cta].append(bil_sec)

    return bills_map


def load_movs_bills(cta_codigo, fechainicial):
    sql = f"""
      with data as (
    select det.dt_codigo, asi.trn_fecha, det.dt_debito, 
    case when det.dt_debito = 1 then round(det.dt_valor,2) else null end as credito,
    case when det.dt_debito = -1 then round(det.dt_valor,2) else null end as debito,
    det.cta_codigo from tasidetalle det join tasiento asi on det.trn_codigo = asi.trn_codigo
    where coalesce(det.cta_codigo, 0)> 0 and asi.trn_valido = 0 and asi.trn_docpen = 'F'
      and det.cta_codigo ={cta_codigo} {fechainicial}  order by asi.trn_fecha
    )
    select dt_codigo, trn_fecha, debito, credito, 
       coalesce(sum(abs(credito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  -
       coalesce(sum(abs(debito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  as saldo,
       cta_codigo
    from data order by trn_fecha asc
    """
    dao = BaseDao(dbsession)
    results = dao.all_raw(sql)
    for result in results:
        debito = result[2] if result[2] else 'null'
        credito = result[3] if result[3] else 'null'

        sql_in = f"""insert into tbillhist(dt_codigo,
                                           bh_debito,
                                           bh_credito,
                                           bh_saldo,
                                           bh_fechacrea,
                                           bh_fechaactualiza,
                                           bh_usercrea,
                                           bh_useractualiza,
                                           bh_valido,
                                           bh_fechatransacc,
                                           cta_codigo) 
                     values({result[0]},{debito},{credito},{result[4]},now(),null,0,null,0,'{result[1]}',{result[5]})"""
        dbsession.execute(sql_in)


if __name__ == "__main__":
    logging.basicConfig(handlers=[RotatingFileHandler(filename=ruta_logs, mode='w', maxBytes=512000, backupCount=4)],
                        level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y%I:%M:%S %p')
    log = logging.getLogger('my_logger')

    log.info('Inicia proceso de totalizacion de billeteras---->')

    esquemas = ['fusay']

    dbsession = None
    try:
        engine = create_engine(dbutils.URL_DB)
        session_factory = get_session_factory(engine)
        dbsession = session_factory()
        process_date = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)

        for esquema in esquemas:
            log.info(f'Se procesa el esquema:{esquema}, en la fecha: {process_date}')
            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))
                billeteras = get_bills()
                for bil in billeteras:
                    cta_id = bil
                    secs = billeteras[bil]
                    fecha_ini_contab = ''
                    if len(secs) == 1:
                        fecha_ini_contab = get_fecha_inicio_contab(secs[0])

                    load_movs_bills(cta_codigo=cta_id, fechainicial=fecha_ini_contab)
                    dbsession.commit()

            except Exception as exs:
                log.error('Error al procesar esquema:{0}'.format(exs))
    except Exception as ex:
        log.error('Ucurrio un error {0}'.format(ex))
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<----Termina proceso totalizacion de billeteras')
