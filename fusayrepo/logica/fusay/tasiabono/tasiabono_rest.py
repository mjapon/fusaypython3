# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasiabono.tasiabono_dao import TAsiAbonoDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.utils import numeros
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasiabono', path='/api/tasiabono/{trn_codigo}', cors_origins=('*',))
class TAsiAbonoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasiabondao = TAsiAbonoDao(self.dbsession)
        if accion == 'form':
            tra_codigo = self.get_request_param('tracod')
            form = tasiabondao.get_form_abono(tra_codigo=tra_codigo)
            return self.res200({'form': form})
        elif accion == 'abosfact':
            trncod = self.get_request_param('trncod')
            abonos, total = tasiabondao.listar_abonos(trn_codigo=trncod)
            return self.res200({'abonos': abonos, 'total': numeros.roundm2(total)})

    def collection_post(self):
        accion = self.get_request_param('accion')
        if accion == 'crea':
            form = self.get_request_json_body()
            tasientodao = TasientoDao(self.dbsession)
            trn_codigo = tasientodao.crear_asiento_cxcp(formcab=form['formcab'], per_codigo=form['per_codigo'],
                                                        user_crea=self.get_user_id(), detalles=form['detalles'])

            return self.res200({'msg': 'Abono registrado exitosamente', 'trn_codigo': trn_codigo})
        elif accion == 'anular':
            form = self.get_request_json_body()
            tasiabondao = TAsiAbonoDao(self.dbsession)
            tasiabondao.anular(abo_codigo=form['codabo'], user_anula=self.get_user_id(), obs_anula=form['obs'])
            msg = 'Abono anulado exitosamente'
            return self.res200({'msg': msg})
