# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.dental.todpieza.todpieza_model import TOdObspieza, TOdTratamientoPieza
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TOdPiezaObsDao(BaseDao):

    def crear(self, pac_id, nro_pieza, obs, user_crea):
        if not cadenas.es_nonulo_novacio(obs):
            raise ErrorValidacionExc('Debe ingresar la observación')

        obspieza = TOdObspieza()
        obspieza.pac_id = pac_id
        obspieza.odo_numpieza = nro_pieza
        obspieza.odo_fechacrea = datetime.datetime.now()
        obspieza.user_crea = user_crea
        obspieza.odo_obs = cadenas.strip(obs)

        self.dbsession.add(obspieza)

    def find_byid(self, odo_id):
        return self.dbsession.query(TOdObspieza).filter(TOdObspieza.odo_id == odo_id).first()

    def eliminar(self, odo_id):
        obspieza = self.find_byid(odo_id=odo_id)
        if obspieza is not None:
            self.dbsession.delete(obspieza)


class TOdTratamientoPiezaDao(BaseDao):

    def find_byid(self, odt_id):
        return self.dbsession.query(TOdTratamientoPieza).filter(TOdTratamientoPieza.odt_id == odt_id).first()

    def crea_ini_trata(self, pac_id, nro_pieza):
        tratapieza = TOdTratamientoPieza()
        tratapieza.pac_id = pac_id
        tratapieza.odt_numpieza = nro_pieza
        tratapieza.odt_fechainitrata = datetime.datetime.now()
        self.dbsession.add(tratapieza)

    def marca_trataext(self, pac_id, nro_pieza):
        tratapieza = TOdTratamientoPieza()
        tratapieza.pac_id = pac_id
        tratapieza.odt_numpieza = nro_pieza
        tratapieza.odt_fecharegtrataext = datetime.datetime.now()
        self.dbsession.add(tratapieza)

    def marca_fin_trata(self, pac_id, nro_pieza):
        sql = """
        select odt_id from todtratamientopieza where odt_fechainitrata = 
        (select max(odt_fechainitrata) from todtratamientopieza where pac_id = {0} and odt_numpieza = {2}
        and odt_fechafintrata = null)
        """.format(pac_id, nro_pieza)

        odt_id = self.first_col(sql, 'odt_id')
        if odt_id is not None:
            odtratapieza = self.find_byid(odt_id=odt_id)
            odtratapieza.odt_fechafintrata = datetime.datetime.now()
            self.dbsession.add(odtratapieza)
