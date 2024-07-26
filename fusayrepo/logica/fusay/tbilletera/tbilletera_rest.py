# coding: utf-8
"""
Fecha de creacion 3/19/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tbilletera.tbilletera_dao import TBilleteraDao
from fusayrepo.logica.fusay.titemconfig_sec.titemconfigsec_dao import TItemConfigSecDao
from fusayrepo.utils import numeros
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tbilletera', path='/api/tbilletera/{bil_id}', cors_origins=('*',))
class TBilleteraRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        billeteradao = TBilleteraDao(self.dbsession)
        if accion == 'form':
            form = billeteradao.get_form(sec_id=self.get_sec_id())
            return self.res200({'form': form})
        elif accion == 'listar':
            billeteras = billeteradao.listar(sec_id=self.get_sec_id())
            totalsaldobill = 0.0
            if billeteras is not None:
                for bil in billeteras:
                    totalsaldobill += bil['bil_saldo']

            return self.res200({'billeteras': billeteras, 'saldotot': numeros.roundm2(totalsaldobill)})
        elif accion == 'listarmin':
            billeteras = billeteradao.listar_min(sec_id=self.get_sec_id())
            return self.res200({'billeteras': billeteras})
        elif accion == 'bilhasmov':
            bilid = self.get_request_param('bilid')
            hasmoves = billeteradao.bill_has_moves(bil_id=bilid)
            return self.res200({'hasmoves': hasmoves})
        elif accion == 'formsecs':
            ic_id = self.get_request_param('ic')
            iconfigsecdao = TItemConfigSecDao(self.dbsession)
            secciones = iconfigsecdao.procesa_list_for_edit(iconfigsecdao.list_for_edit(ic_id=ic_id))
            form = billeteradao.get_form(sec_id=self.get_sec_id())
            form['secciones'] = secciones
            return self.res200({'form': form})

    def collection_post(self):
        accion = self.get_rqpa()
        billeteradao = TBilleteraDao(self.dbsession)
        if accion == 'create':
            form = self.get_json_body()
            billeteradao.crear(form=form, user_crea=self.get_user_id(), sec_id=self.get_sec_id())
            return self.res200({'msg': 'Billetera registrada exitosamente'})
        elif accion == 'update':
            form = self.get_json_body()
            billeteradao.update(form=form, user_update=self.get_user_id())
            return self.res200({'msg': 'Billetera actualizada exitosamente'})
        elif accion == 'anular':
            form = self.get_json_body()
            bil_id = form['bil_id']
            res = billeteradao.anular(bil_id=bil_id, user_anula=self.get_user_id())
            if res == 1:
                return self.res200({'msg': 'Billetera anulada exitosamente'})
            else:
                return self.res404({'msg':
                    'No se pudo anular la billetera (No existe billetera registrada con el codigo{0})'.format(
                        bil_id)})
        elif accion == 'recalc':
            form = self.get_json_body()
            cta_id = form['cta']
            inserted = billeteradao.totalizar(cta_id=cta_id, user_crea=self.get_user_id(), sec_id=self.get_sec_id())
            return self.res200({'result': inserted, 'msg': 'Actualización exitosa'})
