# coding: utf-8
"""
Fecha de creacion 3/19/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tbilletera.tbilleteramov_dao import TBilleteraMovDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tbilleteramov', path='/api/tbilleteramov/{bmoid}', cors_origins=('*',))
class TBilleteraMovRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        billeteramovdao = TBilleteraMovDao(self.dbsession)
        if accion == 'form':
            clase = self.get_request_param('clase')
            form = billeteramovdao.get_form_mov(clase_mov=clase)
            return self.res200({'form': form})
        elif accion == 'listargrid':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            tipo = self.get_request_param('tipo')
            cuenta = self.get_request_param('cuenta')
            grid = billeteramovdao.listar_grid(desde, hasta, tipo, cuenta)
            return self.res200({'grid': grid})
        elif accion == 'formfiltros':
            formfiltro = billeteramovdao.get_form_filtros()
            tiposmovs = billeteramovdao.get_tipos_mov()
            return self.res200({'formfiltro': formfiltro, 'tiposmovs': tiposmovs})
        elif accion == 'getcuentasbytipo':
            tipo = self.get_request_param('tipo')
            cuentas = billeteramovdao.get_cuentas_bytipo_add_todos(tipo=tipo)
            return self.res200({'cuentas': cuentas})
        elif accion == 'getdatosmov':
            movid = self.get_request_param('movid')
            datosmov = billeteramovdao.get_datos_mov(bmo_id=movid)
            return self.res200({'datosmov': datosmov})

    def collection_post(self):
        accion = self.get_rqpa()
        billeteramovdao = TBilleteraMovDao(self.dbsession)
        if accion == 'crear':
            jsonbody = self.get_json_body()
            billeteramovdao.crear(formtosave=jsonbody, usercrea=self.get_user_id())
            return self.res200({'msg': 'Operación Exitosa'})
        elif accion == 'anular':
            jsonbody = self.get_json_body()
            billeteramovdao.anular(bmo_id=jsonbody['codmov'], user_anula=self.get_user_id())
            return self.res200({'msg': 'Registro anulado exitósamente'})
        elif accion == 'confirmar':
            jsonbody = self.get_json_body()
            billeteramovdao.confirmar(bmo_id=jsonbody['codmov'])
            return self.res200({'msg': 'Registro confirmado exitósamente'})
