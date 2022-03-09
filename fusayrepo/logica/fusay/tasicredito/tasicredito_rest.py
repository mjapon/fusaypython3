# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasicredito', path='/api/tasicredito/{trn_codigo}', cors_origins=('*',))
class TAsiCreditoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasicredao = TAsicreditoDao(self.dbsession)
        if accion == 'listarcreds':
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1

            creds, sumas = tasicredao.listar_creditos(per_codigo=per_codigo, solo_pendientes=False, clase=clase,
                                                      sec_codigo=self.get_sec_id())
            return self.res200({'creds': creds, 'totales': sumas})
        elif accion == 'gdet':
            cre_codigo = self.get_request_param('codcred')
            datoscredito = tasicredao.get_datos_credito(cre_codigo)
            return self.res200({'datoscred': datoscredito})
        elif accion == 'listargrid':
            tipo = self.get_request_param('tipo')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            filtro = self.get_request_param('filtro')
            data, totales = tasicredao.listar(tipo, desde, hasta, filtro, sec_id=self.get_sec_id())
            return self.res200({'grid': data, 'totales': totales})
        elif accion == 'gformcrea':
            clase = self.get_request_param('clase')
            codref = self.get_request_param('ref')
            form = tasicredao.get_form(clase=clase, per_codigo=codref, sec_codigo=self.get_sec_id())
            return self.res200({'form': form})

    def collection_post(self):
        accion = self.get_rqpa()
        tasicredao = TAsicreditoDao(self.dbsession)
        if accion == 'crea':
            formtosave = self.get_json_body()
            trn_codigo_gen = tasicredao.create_from_referente(formtosave=formtosave, usercrea=self.get_user_id())
            msg = 'Operación exitosa'
            return self.res200({'trncod': trn_codigo_gen, 'msg': msg})
