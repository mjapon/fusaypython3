# coding: utf-8
"""
Fecha de creacion 3/28/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.utilidadesventas.utilventas_dao import UtilidadesVentasDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/utilventas', path='/api/utilventas/{trn_cod}', cors_origins=('*',))
class UtilidadesVentasRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        utilventasdao = UtilidadesVentasDao(self.dbsession)
        if accion == 'form':
            form = utilventasdao.get_form()
            return self.res200({'form': form['form'],
                                'transaccs': form['transaccs'],
                                'formaspago': form['formaspago'],
                                'tiposprodserv': form['tiposprodserv']})

    def collection_post(self):
        accion = self.get_rqpa()
        utilventasdao = UtilidadesVentasDao(self.dbsession)
        if accion == 'getgrid':
            form = self.get_json_body()
            grid, totales = utilventasdao.listar_grid(form=form)
            return self.res200({'grid': grid, 'totales': totales})
