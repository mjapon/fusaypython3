# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.financiero.tfin_pagoscred.tfin_pagoscred_dao import TFinPagosCredDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/fin/pago", path='/api/fin/pago/{pg_id}', cors_origins=('*',))
class TFinPagosCredRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        pagoscreddao = TFinPagosCredDao(self.dbsession)
        if accion == 'tblpagos':
            cred = self.get_request_param('cred')
            tabla_pagos = pagoscreddao.get_tabla_pagos(cred_id=cred)
            return self.res200({'tblpagos': tabla_pagos})
        elif accion == 'gdetpago':
            pago = self.get_request_param('codpago')
            datospago = pagoscreddao.get_detalles_pago(pgc_id=pago)
            return self.res200({'datospago': datospago})

    def collection_post(self):
        accion = self.get_rqpa()
        pagoscreddao = TFinPagosCredDao(self.dbsession)
        if accion == 'formpago':
            body = self.get_json_body()
            cuotas = body['cuotas']
            form = pagoscreddao.calcular_cuotas(cuotas)
            return self.res200({'form': form})
        elif accion == 'savepago':
            body = self.get_json_body()
            result = pagoscreddao.crear_pago(form=body['form'], user_crea=self.get_user_id())
            return self.res200(result)
        elif accion == 'anulapago':
            body = self.get_json_body()['form']
            pagoscreddao.anular_pago(pgc_id=body['pgc_id'], user_anula=self.get_user_id(),
                                     obs=body['obs'])
            msg = 'Pago anulado exitosamente'
            return self.res200({'msg': msg})
