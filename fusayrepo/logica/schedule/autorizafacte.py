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

from fusayrepo.logica.compele.compele_util import CompeleUtilDao

ruta_logs = "/var/log/chkfacte.log"


# ruta_logs = "/Users/manueljapon/Documents/dev/logs/chkfacte.log"


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


if __name__ == "__main__":
    logging.basicConfig(handlers=[RotatingFileHandler(filename=ruta_logs,
                                                      mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y%I:%M:%S %p')

    log = logging.getLogger('my_logger')

    log.info('Inicia proceso check facturas electronicas--------->')

    """
    Para el caso del estado 0, 4, se deberia enviar el comprobante nuevamente
    para el resto de casos distintos de 1 o 2 se debe realizar la consulta de autorizacion
    """
    dbsession = None
    engine = None
    try:
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/imprentadb')
        session_factory = get_session_factory(engine)
        dbsession = session_factory()

        esquemas_procesar = [
            'fusay', 'achel', 'vguaman', 'yolanda'
        ]

        compeleutildao = CompeleUtilDao(dbsession)

        for esquema in esquemas_procesar:
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))
            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                sql = """
                select distinct asifacte.trn_codigo, asi.trn_fecha, asifacte.tfe_estado from tasifacte asifacte 
                join tasiento asi on asi.trn_codigo =asifacte.trn_codigo and asi.trn_valido =0 and asi.trn_docpen ='F'
                where asifacte.tfe_estado in (3,5) order by asi.trn_fecha asc
                """

                tupla_desc = ('trn_codigo', 'trn_fecha', 'tfe_estado')
                result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                for item in result:
                    log.info('trn_codigo {0} tfe_estado:{1} emp_codigo:{2}'.format(item[0], item[2], ''))

                    compeleutildao.autorizar(trn_codigo=item[0],
                                             emp_codigo=0,
                                             emp_esquema=esquema)

                # TODO: Agregar casos cuando no se ha enviado aun el comprobante
                """
                Estados:
                1: aprobado
                2: rechazado
                3: enviado sin autorizacion
                0: sin transmitir
                4: sin transmitir
                5: recibido
                """
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

    log.info('<--------------------Termina proceso check facturas electronicas')
