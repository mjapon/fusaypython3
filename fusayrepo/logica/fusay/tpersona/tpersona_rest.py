# coding: utf-8
"""
Fecha de creacion 
@autor: 
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.utils import ctes
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tpersona', path='/api/tpersona/{per_id}', cors_origins=('*',))
class TPersonaRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        if 'form' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            form = tpersonadao.getform()
            return {'status': 200, 'form': form}
        elif 'buscaci' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_porciruc(per_ciruc=self.get_request_param('ciruc'))
            if res is not None:
                return {'status': 200, 'persona': res}
            else:
                return {'status': 404}
        elif 'buscacifull' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_porciruc_full(per_ciruc=self.get_request_param('ciruc'))
            if res is not None:
                return {'status': 200, 'persona': res}
            else:
                return {'status': 404}
        elif 'buscaporidfull' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_porperid_full(per_id=self.get_request_param('perid'))
            if res is not None:
                return {'status': 200, 'persona': res}
            else:
                return {'status': 404}
        elif 'buscaporid' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_porcodigo(per_id=self.get_request_param('perid'))
            if res is not None:
                return self.res200({'persona': res})
            else:
                return self.res404()

        elif 'buscaemail' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_poremail(per_ciruc=self.get_request_param('email'))
            if res is not None:
                return {'status': 200, 'persona': res}
            else:
                return {'status': 404}
        elif 'buscatipo' == accion:
            tpersonadao = TPersonaDao(self.dbsession)
            per_tipo = self.get_request_param('per_tipo')
            res = tpersonadao.listar_por_tipo(per_tipo)
            return {'status': 200, 'items': res}
        elif 'filtronomapel' == accion:
            filtro = self.get_request_param('filtro')
            tpersonadao = TPersonaDao(self.dbsession)
            res = tpersonadao.buscar_pornomapelci(filtro)
            return {'status': 200, 'items': res}
        elif 'filtropag' == accion:
            filtro = self.get_request_param('filtro')
            lastpage = self.get_request_param('pag')
            intlastpage = 0
            try:
                intlastpage = int(lastpage)
            except Exception as ex:
                log.error('Error al parsear a int la pagina', ex)

            tpersonadao = TPersonaDao(self.dbsession)
            limit = 50
            offset = intlastpage * limit
            items = tpersonadao.buscar_pornomapelci(filtro, solo_cedulas=True, limit=limit, offsset=offset)
            hasMore = items is not None and len(items) == limit
            return {'status': 200, 'items': items, 'hasMore': hasMore, 'nextp': intlastpage + 1}
        elif 'lmedicos' == accion:
            tipo = self.get_request_param('tipo')
            tpersonadao = TPersonaDao(self.dbsession)
            medicos = tpersonadao.listar_medicos(med_tipo=tipo)
            return {'status': 200, 'medicos': medicos}

        elif 'gtotaldeudas':
            tasicreditodao = TAsicreditoDao(self.dbsession)
            percodigo = self.get_request_param('codper')
            totaldeudas = tasicreditodao.get_total_deudas(per_codigo=percodigo,
                                                          tra_codigo=ctes.TRA_CODIGO_FACTURA_VENTA)
            return self.res200({'deudas': totaldeudas})

    def post(self):
        tpersonadao = TPersonaDao(self.dbsession)
        form = self.get_json_body()
        per_id_gen = tpersonadao.crear(form=form)
        return {'status': 200, 'msg': u'Registrado exitosamente', 'per_id': per_id_gen}

    def put(self):
        per_id = self.get_request_matchdict('per_id')
        tpersonadao = TPersonaDao(self.dbsession)
        form = self.get_json_body()
        if int(per_id) == 0:
            return self.post()
        else:
            upd = tpersonadao.actualizar(per_id=per_id, form=form)
            msg = u'Actualizado exitosamente'
            if not upd:
                msg = 'No se pudo actualizar, no existe un registro con el codigo:{0}'.format(per_id)

            return {'status': 200, 'msg': msg}
