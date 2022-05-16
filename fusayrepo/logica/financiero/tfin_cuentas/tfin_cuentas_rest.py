# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.financiero.tfin_cuentas.tfin_cuentas_dao import TFinCuentasDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/fin/cuentas", path="/api/fin/cuentas/{cue_id}", cors_origins=('*',))
class TFinCuentasRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        cuentas_dao = TFinCuentasDao(self.dbsession)
        if accion == 'form':
            perid = self.get_request_param('perid')
            form = cuentas_dao.get_form(per_id=perid)
            return self.res200({'form': form})
        elif accion == 'chkexist':
            perid = self.get_request_param('perid')
            has_cuenta = cuentas_dao.has_cuenta(perid, 1)
            return self.res200({'has_cuenta': has_cuenta})
        elif accion == 'gdatoscuenta':
            perid = self.get_request_param('perid')
            tipo = self.get_request_param('tipo')
            datoscuenta = cuentas_dao.get_datos_cuenta(perid, tipo);
            if datoscuenta is not None:
                return self.res200({'datoscuenta': datoscuenta, 'existe': 1})
            else:
                return self.res200({'existe': 0})
        elif accion == 'gdatctabynum':
            numcta = self.get_request_param('numcta')
            if not cadenas.es_nonulo_novacio(numcta):
                raise ErrorValidacionExc('Debe ingresar el numero de la cuenta para buscar')
            datoscuenta = cuentas_dao.get_datos_cuenta_by_num(numcta)
            if datoscuenta is not None:
                return self.res200({'datoscuenta': datoscuenta, 'existe': 1})
            else:
                return self.res200({'existe': 0})
        elif accion == 'listctasbysocio':
            codsocio = self.get_request_param('socio')
            cuentas = cuentas_dao.listar_cuentas_socio(codsocio)
            return self.res200({'cuentas': cuentas})

    def collection_post(self):
        accion = self.get_rqpa()
        cuentas_dao = TFinCuentasDao(self.dbsession)
        if accion == 'apertura':
            form = self.get_json_body()
            cue_id = cuentas_dao.crear(form=form, user_crea=self.get_user_id())
            msg = 'Cuenta aperturada exitósamente. Su número de cuenta es: {0}'.format(cue_id)
            return self.res200({'msg': msg, 'numctagen': cue_id})
