# coding: utf-8
"""
Fecha de creacion 4/4/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.datoslogged.datoslogged_dao import DataLoggedDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/datosinitlogged', path='/api/datosinitlogged/{user}', cors_origins=('*',))
class DatosLoggedRest(TokenView):

    def collection_get(self):
        datosloged_dao = DataLoggedDao(self.dbsession)
        accion = self.get_rqpa()
        if accion == 'datosgen':
            datoslogged = datosloged_dao.get_datos_logged(user_id=self.get_user_id(), emp_esquema=self.get_emp_esquema())
            return self.res200({'datlogged': datoslogged})
        elif accion == 'chkperm':
            perm = self.get_request_param('perm')
            chkperm = datosloged_dao.check_permiso(user_id=self.get_user_id(), permiso=perm)
            return self.res200({'chkperm': chkperm})
