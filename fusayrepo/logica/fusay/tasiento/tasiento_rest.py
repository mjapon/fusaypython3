# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasiento', path='/api/tasiento/{trn_codigo}', cors_origins=('*',))
class TAsientoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasientodao = TasientoDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)

        if accion == 'formcab':
            tra_codigo = self.get_request_param('tra_cod')
            tdv_codigo = self.get_request_param('tdv_codigo')
            ttpdvdao = TtpdvDao(self.dbsession)
            alm_codigo = ttpdvdao.get_alm_codigo_from_tdv_codigo(tdv_codigo)
            form_cab = tasientodao.get_form_cabecera(tra_codigo, alm_codigo, 0, tdv_codigo)
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)
            formaspago = ttransaccdao.get_formas_pago(tra_codigo=tra_codigo)
            form_det = tasientodao.get_form_detalle()
            return self.res200(
                {'formcab': form_cab, 'ttransacc': ttransacc, 'formaspago': formaspago, 'formdet': form_det})

        elif accion == 'gdetdoc':
            trn_codigo = self.get_request_param('trncod')
            doc = tasientodao.get_documento(trn_codigo=trn_codigo)
            return self.res200({'doc': doc})

    def collection_post(self):
        accion = self.get_request_param('accion')
        tasientodao = TasientoDao(self.dbsession)
        if accion == 'creadoc':
            form = self.get_json_body()
            trn_codigo = tasientodao.crear(form=form['form'], form_persona=form['form_persona'],
                                           user_crea=self.get_user_id(),
                                           detalles=form['detalles'], pagos=form['pagos'])
            msg = 'Registro exitoso'
            return self.res200({'trn_codigo': trn_codigo, 'msg': msg})
