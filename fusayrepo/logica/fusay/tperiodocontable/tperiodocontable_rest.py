# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tperiodocontable.tperiodo_dao import TPeriodoContableDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/tperiodocontable", path='/api/tperiodocontable/{per_id}', cors_origins=('*',))
class TPeriodoContableRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        periododao = TPeriodoContableDao(self.dbsession)
        if accion == 'current':
            periodo_contable = periododao.get_datos_periodo_contable()
            if periodo_contable is None:
                return {'msg': 'No existe un periodo contable activo'}
            else:
                return {'periodo': periodo_contable}
        elif accion == 'anterior':
            periodo_anterior = periododao.get_datos_periodo_anterior()
            info_cta_util_acum = periododao.get_info_cta_utilidades_acumuladas()
            if periodo_anterior is not None:
                return {'existe': True, 'periodo': periodo_anterior, 'info_cta_util_acum': info_cta_util_acum}
            else:
                return {'existe': False, 'info_cta_util_acum': info_cta_util_acum}
        elif accion == 'ctadepacum':
            info_cta_dep_acum = periododao.get_info_cta_depreciacion_acumulada()
            return {'info_cta_dep_acum': info_cta_dep_acum}

    def collection_post(self):
        accion = self.get_rqpa()
        periodo_dao = TPeriodoContableDao(self.dbsession)

        if accion == 'abrir':
            form = self.get_json_body()
            try:
                pc_id = periodo_dao.crear(form=form, user_crea=self.get_user_id())
                return self.res200({'msg': 'Registro exitoso', 'pc_id': pc_id})
            except ErrorValidacionExc as ex:
                log.info('Error al tratar de crear periodo')
                return self.res400({'msg': str(ex)})
        elif accion == 'cerrar':
            form = self.get_json_body()
            periodo_dao.cerrar(pc_id=form['pc_id'],
                               user_cierra=self.get_user_id(),
                               fecha_cierre=form['fecha_cierre'],
                               asientos=form['asientos'])
            return self.res200({'msg': 'Cierre de periodo contable exitoso'})
