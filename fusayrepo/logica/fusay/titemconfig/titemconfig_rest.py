# coding: utf-8
"""
Fecha de creacion 2/15/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.timpuesto.timpuesto_dao import TImpuestoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.titemconfig_sec.titemconfigsec_dao import TItemConfigSecDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tventatickets.tventatickets_dao import TVentaTicketsDao
from fusayrepo.utils.pyramidutil import TokenView, FusayPublicView

log = logging.getLogger(__name__)


@resource(collection_path='/api/titemconfig', path='/api/titemconfig/{ic_id}', cors_origins=('*',))
class TItemConfigRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        titemconfig_dao = TItemConfigDao(self.dbsession)
        if 'listar' == accion:
            filtro = self.get_request_param('filtro')
            sec_id = self.get_request_param('sec_id')
            data = titemconfig_dao.listar(filtro, sec_id=sec_id)
            return {'status': 200, 'data': data}
        elif 'formcrea' == accion:
            form = titemconfig_dao.get_form()
            return {'status': 200, 'form': form}
        elif 'rubrosgrid' == accion:
            items = titemconfig_dao.listarrubros_grid()
            return {'status': 200, 'items': items}
        elif 'seccodbarra' == accion:
            tparamsdao = TParamsDao(self.dbsession)
            nexcodbar = tparamsdao.get_next_sequence_codbar()
            return {'status': 200, 'codbar': nexcodbar}
        elif 'verifcodbar' == accion:
            codbar = self.get_request_param('codbar')
            datosart = titemconfig_dao.get_codbarnombre_articulo(codbar)
            existe = datosart is not None
            nombreart = datosart['ic_nombre'] if datosart is not None else ''
            return {'status': 200, 'existe': existe, 'nombreart': nombreart}
        elif 'teleservicios' == accion:
            sec_id = self.get_sec_id()
            data = titemconfig_dao.listar_teleservicios(sec_id=sec_id)
            return {'status': 200, 'data': data}
        elif 'formrubros' == accion:
            form = titemconfig_dao.get_form_rubro()
            vtdao = TVentaTicketsDao(self.dbsession)
            tipos = vtdao.get_tipos_cuentas()
            return {'status': 200, 'form': form, 'tipos': tipos}
        elif 'gservdent' == accion:
            filtro = self.get_request_param('filtro')
            items = titemconfig_dao.busca_serv_dentales_filtro(filtro)
            return self.res200({'items': items})
        elif 'gartsserv' == accion:
            filtro = self.get_request_param('filtro')
            secid = self.get_request_param('sec')
            items = titemconfig_dao.buscar_articulos(filtro=filtro, sec_id=secid)
            return self.res200({'items': items})
        elif 'gservdentall' == accion:
            items = titemconfig_dao.busca_serv_dentales_all()
            return self.res200({'items': items})
        elif 'gimpuestos' == accion:
            timpuestodao = TImpuestoDao(self.dbsession)
            impuestos = timpuestodao.get_impuestos()
            return self.res200({'impuestos': impuestos})
        else:
            return {'status': 404, 'msg': 'accion desconocida', 'accion': accion}

    def post(self):
        titemconfig_dao = TItemConfigDao(self.dbsession)
        form = self.get_json_body()
        ic_id = int(self.get_request_matchdict('ic_id'))
        result_ic_id = ic_id

        accion = self.get_request_param('accion')
        if accion is not None:
            if accion == 'del':
                titemconfig_dao.anular(ic_id=ic_id, useranula=self.get_user_id())
                return {'status': 200, 'msg': u'Anulado exitósamente'}
            elif accion == 'updatecode':
                titemconfig_dao.update_barcode(ic_id=ic_id, newbarcode=form['new_ic_code'])
                return {'status': 200, 'msg': u'Actualizado exitósamente'}
            elif accion == 'guardarubro':
                msg = 'Rubro creado exitosamente'
                if result_ic_id == 0:
                    titemconfig_dao.crear_rubro(form, self.get_user_id())
                else:
                    msg = 'Rubro editado exitosamente'
                    titemconfig_dao.editar_rubro(form, self.get_user_id())
                return {'status': 200, 'msg': msg}
        else:
            if ic_id == 0:
                msg = u'Registrado exitósamente'
                result_ic_id = titemconfig_dao.crear(form, self.get_user_id())
            else:
                msg = u'Actualizado exitósamente'
                titemconfig_dao.actualizar(form, self.get_user_id())

            return {'status': 200, 'msg': msg, 'ic_id': result_ic_id}

    def get(self):
        ic_id = self.get_request_matchdict('ic_id')
        titemconfig_dao = TItemConfigDao(self.dbsession)
        accion = self.get_request_param('accion')
        if accion is not None:
            if accion == 'formrubroedit':
                itemconfig = titemconfig_dao.get_form_rubro_edit(ic_id=ic_id)
                vtdao = TVentaTicketsDao(self.dbsession)
                tipos = vtdao.get_tipos_cuentas()
                if itemconfig is not None:
                    return {'status': 200, 'item': itemconfig, 'tipos': tipos}
                else:
                    return {'status': 404, 'msg': 'No existe el registro'}
        else:
            res = titemconfig_dao.get_detalles_prod(ic_id=ic_id)
            itemconfigsec = TItemConfigSecDao(self.dbsession)
            secciones = itemconfigsec.list_for_edit(ic_id=ic_id)

            return {'status': 200, 'datosprod': res, 'secciones': secciones}


@resource(collection_path='/api/public/titemconfig', path='/api/public/titemconfig/{ic_id}', cors_origins=('*',))
class PublicItemConfigRest(FusayPublicView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        titemconfig_dao = TItemConfigDao(self.dbsession)
        if 'teleservicios' == accion:
            sec_id = 1
            data = titemconfig_dao.listar_teleservicios()
            return {'status': 200, 'data': data}
        else:
            return {'status': 404, 'msg': 'accion desconocida'}
