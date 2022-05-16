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

logging.basicConfig(handlers=[RotatingFileHandler(filename="/var/log/mayorizamavil.log",
                                                  mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')

log = logging.getLogger('my_logger')


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


if __name__ == "__main__":
    log.info('Inicia Procesio mayorizacion--------->')

    dbsession = None
    engine = None
    try:
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/imprentadb')
        session_factory = get_session_factory(engine)
        dbsession = session_factory()

        esquemas_procesar = [
            'cajademo', 'cajaruna'
        ]

        for esquema in esquemas_procesar:
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))

            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                fecha_actual = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
                log.info('Fecha proceso:{0}'.format(fecha_actual))

                sqlcount = """select count(*) as cuenta from tasiento where trn_valido = 0 
                and date(trn_fecha) = '{0}' and trn_mayorizado = false""".format(fecha_actual)
                tupla_res = dbsession.query('cuenta').from_statement(text(sqlcount)).first()

                tot_pendientes = 0
                if tupla_res is not None:
                    tot_pendientes = int(tupla_res[0])

                if tot_pendientes > 0:
                    log.info('Se procesaran {0} registros pendientes de mayorizacion'.format(tot_pendientes))
                    sql = """
                    select trn_codigo, trn_mayorizado, public.fn_mayorizar_asiento(trn_codigo) as mayor_res from tasiento
                    where trn_valido = 0 and date(trn_fecha) = '{0}' order by trn_fecha asc;
                    """.format(fecha_actual)

                    tupla_desc = ('trn_codigo', 'trn_mayorizado', 'mayor_res')
                    result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                    for item in result:
                        log.info('trn_codigo {0} trn_mayorizado:{1} mayor_res:{2}'.format(item[0], item[1], item[2]))

                    dbsession.commit()
                else:
                    log.info('No hay asientos pendientes de mayorizacion')
            except Exception as exs:
                log.error('Error al procesar esquema:{0}'.format(exs))

    except Exception as ex:
        log.error('Ucurrio un error al mayorizar {0}'.format(ex))
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<--------------------Termina proceso mayorizacion')
