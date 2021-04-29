# coding: utf-8
"""
Fecha de creacion 1/22/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tplan.tplan_dao import TPlanDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.utils import ctes
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tplan', path='/api/tplan/{pln_id}', cors_origins=('*',))
class TPlanRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        tpladao = TPlanDao(self.dbsession)
        if accion == 'form':
            formplan = tpladao.get_form()
            return self.res200({'formplan': formplan})
        elif accion == 'listarg':
            grid = tpladao.listar_grid()
            ttransaccdao = TTransaccDao(self.dbsession)
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=ctes.TRA_COD_PLAN)
            return self.res200({'grid': grid, 'ttransacc': ttransacc})
        elif accion == 'listaplanes':
            planes = tpladao.listar()
            return self.res200({'planes': planes})

    def collection_post(self):
        accion = self.get_request_param('accion')
        tplandao = TPlanDao(self.dbsession)
        if accion == 'crea':
            form = self.get_json_body()
            pln_id = tplandao.crear(form, usercrea=self.get_user_id())
            return self.res200({'msg': 'Plan creado exitosamente', 'pln_id': pln_id})
