# coding: utf-8
"""
Fecha de creacion 5/11/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_contrato.tagp_contrato_dao import TAgpContratoDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagpcontrato', path='/api/tagpcontrato/{cna_id}', cors_origins=('*',))
class TagpContratoRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()

        tagpcontratodao = TAgpContratoDao(self.dbsession)
        if accion == 'form':
            form = tagpcontratodao.get_form_anterior()
            return self.res200({'form': form})
        elif accion == 'gformed':
            cna_id = self.get_request_param('cna')
            form = tagpcontratodao.get_form_edit(cna_id)
            return self.res200({'form': form})

        elif accion == 'gbyref':
            per_codigo = self.get_request_param('codref')
            items = tagpcontratodao.find_by_per_codigo(per_codigo=per_codigo)
            return self.res200({'items': items})
        elif accion == 'gbycodmed':
            codmed = self.get_request_param('codmed')
            datosmed = tagpcontratodao.find_by_mdg_id(mdg_id=codmed)
            return self.res200({'datosmed': datosmed})

        elif accion == 'findbynum':
            mdg_num = self.get_request_param('num')
            result = tagpcontratodao.find_by_nummed(mdg_num=mdg_num)
            if result is not None:
                return self.res200({'data': result, 'msg': 'Medidor encontrado'})
            else:
                return self.res404({'msg': 'No se encontró el medidor (num:{0})'.format(mdg_num)})
        elif accion == 'filterbynum':
            filtro = self.get_request_param('filtro')
            result = tagpcontratodao.filter_by_nummed(filtro=filtro)
            return self.res200({'data': result})
        elif accion == 'formlista':
            result = tagpcontratodao.get_form_filtros_listados()
            return self.res200({key: result[key] for key in result.keys()})

        elif accion == 'agp_contratos':
            grid = tagpcontratodao.get_grid_contratos(filtro=self.get_request_param('filtro'))
            return self.res200({'grid': grid, 'titulo': 'Lista de contratos registrados'})
        elif accion == 'agp_lecturas':
            grid = tagpcontratodao.get_grid_lecturas(filtro=self.get_request_param('filtro'),
                                                     anio=self.get_request_param('anio'),
                                                     mes=self.get_request_param('mes'),
                                                     estado=self.get_request_param('estado'))
            return self.res200({'grid': grid, 'titulo': 'Lista de consumos por mes'})
        elif accion == 'agp_pagos':
            grid = tagpcontratodao.get_grid_pagos(filtro=self.get_request_param('filtro'),
                                                  anio=self.get_request_param('anio'),
                                                  mes=self.get_request_param('mes'),
                                                  estado=self.get_request_param('estado'))
            return self.res200({'grid': grid, 'titulo': 'Lista de pagos por mes'})
        elif accion == 'listar':
            filtro = self.get_request_param('filtro')
            gridcontratos = tagpcontratodao.listar_grid_for_view(filtro)
            return self.res200({'gridcontratos': gridcontratos})

    def collection_post(self):
        accion = self.get_rqpa()
        tagpcontratodao = TAgpContratoDao(self.dbsession)
        if accion == 'crea':
            body = self.get_json_body()
            edcrearef = True
            if 'edcrearef' in body:
                edcrearef = body['edcrearef']

            cna_id = tagpcontratodao.crear(form=body['form'], formref=body['formref'], formed=body['formmed'],
                                           usercrea=self.get_user_id(), editcrearef=edcrearef)
            msg = 'Registro exitoso'
            return self.res200({'msg': msg, 'cna_id': cna_id})
        elif accion == 'editar':
            body = self.get_json_body()
            edcrearef = True
            if 'edcrearef' in body:
                edcrearef = body['edcrearef']
            tagpcontratodao.editar(form=body['form'], formref=body['formref'], formed=body['formmed'],
                                   useredit=self.get_user_id(), editcrearef=edcrearef)
            return self.res200({'msg': 'Actualizado exitoso'})
        elif accion == 'anular':
            body = self.get_json_body()
            tagpcontratodao.anular(form=body['form'], useranula=self.get_user_id())
            return self.res200({'msg': 'Registro anulado exitosamente'})
