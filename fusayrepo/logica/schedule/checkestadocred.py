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


if __name__ == "__main__":

    logging.basicConfig(handlers=[RotatingFileHandler(filename="/var/log/checkestadocred.log",
                                                      mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y%I:%M:%S %p')

    log = logging.getLogger('my_logger')

    log.info('Inicia Proceso estadocred--------->')

    dbsession = None
    engine = None
    try:
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/imprentadb')
        session_factory = get_session_factory(engine)
        dbsession = session_factory()

        esquemas_procesar = [
            'cajademo', 'cajaruna', 'cajainti'
        ]

        for esquema in esquemas_procesar:
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))

            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                fecha_actual = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
                log.info('Fecha proceso:{0}'.format(fecha_actual))

                sqlcount = "select count(*) as cuenta from tfin_credito where cre_saldopend = 0 and cre_estado = 2"
                tupla_res = dbsession.query('cuenta').from_statement(text(sqlcount)).first()

                tot_pendientes = 0
                if tupla_res is not None:
                    tot_pendientes = int(tupla_res[0])

                if tot_pendientes > 0:
                    log.info('Se procesaran {0} creditos pendientes de cancelar'.format(tot_pendientes))
                    sql = """
                    select 1 as uno, public.fn_change_estadocred(5) as updated;
                    """
                    tupla_desc = ('uno', 'updated')
                    result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                    log.info('actualizado')
                    dbsession.commit()
                else:
                    log.info('No hay creditos pendientes de cambiar estado cred')
            except Exception as exs:
                log.error('Error al procesar esquema:{0}'.format(exs))

    except Exception as ex:
        log.error('Ucurrio un error al cambiar estadocred {0}'.format(ex))
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<--------------------Termina proceso estadocred')
