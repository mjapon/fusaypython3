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
from fusayrepo.logica.compele.gen_data import GenDataForFacte
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasifacte.tasifacte_dao import TasiFacteDao

ruta_logs = "/var/log/chkfacte.log"

#ruta_logs = "C:\dev\mavil\logs\chkfacte.log"

def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def reopen_db_connection(current_db_session):
    try:
        log.info('Reabriendo conexion-->')
        current_db_session.close()
        log.info('Conexion cerrada')
    except:
        log.info('Error al cerrar conexion')
    _engine = create_engine(url_data_base)
    _session_factory = get_session_factory(engine)
    _dbsession = session_factory()
    return dbsession


def message_is_clave_acceso_registrada(message):
    if message is not None:
        msg = str(message)
        if "CLAVE ACCESO REGISTRADA" in msg and "identificador = \"43\"" in msg:
            return True
    return False


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
        #url_data_base = "postgresql://pgadmin:43sEMgDkgu9ALAof@localhost:5432/imprentadb"
        url_data_base = "postgresql://postgres:postgres@localhost:5432/imprentadb"
        engine = create_engine(url_data_base)
        session_factory = get_session_factory(engine)
        dbsession = session_factory()

        sql = "select distinct emp_esquemadb  from comprobantes.tempresa"
        esquemas_procesar = dbsession.query('emp_esquemadb').from_statement(text(sql)).all()

        compeleutildao = CompeleUtilDao(dbsession)
        gen_data = GenDataForFacte(dbsession)
        tasifacte_dao = TasiFacteDao(dbsession)

        for esquema_tupla in esquemas_procesar:
            esquema = esquema_tupla[0]
            log.info('--Inicia proceso para esquema:{0}'.format(esquema))
            try:
                dbsession.execute("SET search_path TO {0}".format(esquema))

                sql = """
                select distinct asifacte.trn_codigo, asi.trn_fecha, asifacte.tfe_estado from {esquema}.tasifacte asifacte
                join {esquema}.tasiento asi on asi.trn_codigo =asifacte.trn_codigo and asi.trn_valido =0 and asi.trn_docpen ='F'
                where asifacte.tfe_estado in (3,5) order by asi.trn_fecha asc
                """.format(esquema=esquema)

                tupla_desc = ('trn_codigo', 'trn_fecha', 'tfe_estado')
                result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                for item in result:
                    log.info(
                        'envio autorizar: trn_codigo {0} tfe_estado:{1} emp_codigo:{2}'.format(item[0], item[2],
                                                                                               esquema))
                    compeleutildao.autorizar(trn_codigo=item[0],
                                             emp_codigo=0,
                                             emp_esquema=esquema)

            except Exception as exs:
                log.info('Error 1 al procesar esquema:{0}'.format(exs), exs)
                dbsession = reopen_db_connection(current_db_session=dbsession)
                dbsession.execute("SET search_path TO {0}".format(esquema))

            try:
                sql = """
                        select distinct asifacte.trn_codigo, asi.trn_fecha, asifacte.tfe_estado from {esquema}.tasifacte asifacte
                        join {esquema}.tasiento asi on asi.trn_codigo =asifacte.trn_codigo and asi.trn_valido =0 and asi.trn_docpen ='F'
                        where asifacte.tfe_estado in (0,4) order by asi.trn_fecha asc
                        """.format(esquema=esquema)

                tupla_desc = ('trn_codigo', 'trn_fecha', 'tfe_estado')
                result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                for item in result:
                    log.info('envio validar trn_codigo {0} tfe_estado:{1} emp_codigo:{2}'.format(
                        item[0], item[2], esquema))
                    try:
                        compeleutildao.redis_enviar(trn_codigo=item[0],
                                                    emp_codigo=0,
                                                    emp_esquema=esquema)
                    except ErrorValidacionExc as ExF:
                        log.error("Error al ejecutar envio:{0}".format(ExF))

            except Exception as exs:
                log.info('Error 2 al procesar esquema:{0}'.format(exs), exs)
                dbsession = reopen_db_connection(current_db_session=dbsession)
                dbsession.execute("SET search_path TO {0}".format(esquema))

            # Proceso para verificar facturas en estado rechazado cuyo mensaje sea CLAVEACCESO REGISTRADA
            try:
                sql = """
                       select distinct asifacte.trn_codigo, asifacte.tfe_estado, asifacte.tfe_mensajes, asi.trn_fecha from {esquema}.tasifacte asifacte
                       join {esquema}.tasiento asi on asi.trn_codigo =asifacte.trn_codigo and asi.trn_valido =0 and asi.trn_docpen ='F'
                       where asifacte.tfe_estado = 2 order by asi.trn_fecha asc
                       """.format(esquema=esquema)

                tupla_desc = ('trn_codigo', 'tfe_estado', 'tfe_mensajes', 'trn_fecha')
                result = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                dbsession.execute("SET search_path TO {0}".format(esquema))
                for item in result:
                    try:
                        tfe_message = item[2]
                        if message_is_clave_acceso_registrada(tfe_message):
                            log.info(
                                'envio autorizar comprobante rechazada por CLAVEACCESO REGISTRADA trn_codigo {0} tfe_estado:{1} emp_codigo:{2}'.format(
                                    item[0], item[1], esquema))
                            sql =("select tfe_codigo, public.fn_update_factele_to_status({trncod}, 5) as status "
                                  "from {esquema}.tasifacte t where trn_codigo = {trncod}").format(esquema=esquema, trncod=item[0])
                            log.info(sql)
                            tupla_desc = ('tfe_codigo', 'status')
                            result_update_status = dbsession.query(*tupla_desc).from_statement(text(sql)).all()
                    except Exception as exupd:
                        log.error("Error al ejecutar db funcion de actualizacion", exupd)
                if result is not None and len(result)>0:
                    dbsession.commit()
            except Exception as exs:
                log.info('Error 3 al procesar mensjes rechazados esquema:{0}'.format(exs), exs)

    except Exception as ex:
        log.info('Ucurrio un error en el proceso {0}'.format(ex), ex)
    finally:
        try:
            dbsession.close()
            log.info('Conexion cerrada')
        except:
            log.info('Error al cerrar conexion')

    log.info('<--------------------Termina proceso check facturas electronicas')
