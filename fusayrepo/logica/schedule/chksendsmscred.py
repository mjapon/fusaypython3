# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fusayrepo.logica.financiero.tfin_pagoscred.tfin_pagoscred_dao import TFinPagosCredDao
from fusayrepo.logica.financiero.tsms.tsms_dao import TSmsDao
from fusayrepo.logica.schedule import sms_util
from fusayrepo.utils import fechas, ctes

ruta_logs = "/var/log/chkcredsms.log"
# ruta_logs = "/Users/manueljapon/Documents/dev/logs/chkcredsms.log"

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

    log.info('Inicia proceso envio sms creditos--------->')

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
            'cajaruna','cajainti'
        ]

        smsdao = TSmsDao(dbsession)

        for esquema in esquemas_procesar:
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))

            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                fecha_actual = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
                log.info('Fecha proceso:{0}'.format(fecha_actual))

                pagoscreddao = TFinPagosCredDao(dbsession)
                sms = pagoscreddao.get_smss_pago_credito(ndaydelta=2)
                if len(sms) > 0:
                    log.info('Se van a enviar :{0} sms'.format(len(sms)))
                    for sms_info in sms:
                        try:
                            result = sms_util.send_sms(sms_info['phone'], sms_info['message'])
                            if result is not None:
                                smsdao.crear(form=result)
                        except Exception as exss:
                            log.error("Error al enviar sms:{0}".format(exss), exss)
                else:
                    log.info('No hay sms por enviar')

                dbsession.commit()
            except Exception as exs:
                log.error('Error al procesar esquema:{0}'.format(exs))

    except Exception as ex:
        log.error('Ucurrio un error al enviar sms {0}'.format(ex))
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<--------------------Termina proceso check envio sms creditos')
