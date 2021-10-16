# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""

import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tcierre.tcierre_dao import TCierreDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tcierre', path='/api/tcierre/{cie_codigo}', cors_origins=('*',))
class TCierreRest(TokenView):

    def collection_get(self):
        cierredao = TCierreDao(self.dbsession)
        accion = self.get_request_param('accion')

        if accion == 'form_aper':
            form = cierredao.get_form_apertura()
            return self.res200({'form': form})
        elif accion == 'form_cierre':
            # TODO: Agregar el parametro de cierre
            form = cierredao.get_form_cierre(cie_codigo=0)
            return self.res200({'form': form})
        elif accion == 'reporte':
            dia = self.get_request_param('dia')
            reporte = cierredao.get_reporte_cierre(dia, self.get_sec_id())
            return self.res200({'reporte': reporte})
