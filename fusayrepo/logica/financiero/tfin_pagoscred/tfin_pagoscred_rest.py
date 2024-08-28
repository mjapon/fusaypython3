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
        elif accion == 'gformcalpagos':
            form = pagoscreddao.get_form_calc_pago()
            return self.res200({'form': form})

    def collection_post(self):
        accion = self.get_rqpa()
        pagoscreddao = TFinPagosCredDao(self.dbsession)
        if accion == 'calcuotaspago':
            body = self.get_json_body()
            cuotas = body['cuotas']
            fecha_pago = body['fecpago']
            form = pagoscreddao.calcular_cuotas_pagar(cuotas, fecha_pago)
            return self.res200({'form': form})
        elif accion == 'cuotasformarcapago':
            body = self.get_json_body()
            cuotas = body['cuotas']
            form = pagoscreddao.calcular_cuotas_pagar(cuotas, calcular_mora=False)
            return self.res200({'form': form})
        elif accion == 'savemarcapag':
            body = self.get_json_body()
            result = pagoscreddao.marcar_como_pagado(form=body['form'], user_crea=self.get_user_id())
            return self.res200(result)
        elif accion == 'savepago':
            body = self.get_json_body()
            result = pagoscreddao.crear_pago(form=body['form'], user_crea=self.get_user_id(),
                                             sec_codigo=self.get_sec_id())
            return self.res200(result)
        elif accion == 'anulapago':
            body = self.get_json_body()['form']
            pagoscreddao.anular_pago(pgc_id=body['pgc_id'], user_anula=self.get_user_id(),
                                     obs=body['obs'])
            msg = 'Pago anulado exitósamente'
            return self.res200({'msg': msg})
