# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.compele.compele_util import CompeleUtilDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/compele", path="/api/compele/{trn_cod}", cors_origins=('*',))
class GenCompeleRest(TokenView):

    def collection_get(self):
        pass

    def collection_post(self):
        accion = self.get_rqpa()
        datosfact = self.get_request_json_body()
        trncod = datosfact['trncod']
        compeledao = CompeleUtilDao(self.dbsession)

        if accion == 'validar':
            compeledao.enviar(trn_codigo=trncod, sec_codigo=self.get_sec_id())

        if accion == 'autoriza':
            compeledao.autorizar(trn_codigo=trncod, emp_codigo=self.get_emp_codigo(),
                                 emp_esquema=self.get_emp_esquema())

            return self.res200({'exito': True, 'autorizado': True})

        elif accion == 'savecomprob':
            compeledao.registra_comprob_contrib(
                trn_codigo=trncod,
                emp_codigo=self.get_emp_id(),
                estado_envio=datosfact['estado'],
                sec_id=self.get_sec_id()
            )

            return self.res200({'exito': True})
