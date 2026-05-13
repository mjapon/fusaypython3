# coding: utf-8
"""
Fecha de creacion 1/15/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.tasicredito.tasicred_cxp_provs import CuentasPorPagarProvsService
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.utils import cadenas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tasicredito', path='/api/tasicredito/{trn_codigo}')
class TAsiCreditoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tasicredao = TAsicreditoDao(self.dbsession)
        if accion == 'listarcreds':
            per_codigo = self.get_request_param('per')
            clase = self.get_request_param('clase')
            if not cadenas.es_nonulo_novacio(clase):
                clase = 1
            tipopago = self.get_request_param('tipopago')
            tipopagoint = 0
            if cadenas.es_nonulo_novacio(tipopago):
                tipopagoint = int(tipopago)

            creds, sumas = tasicredao.listar_creditos(per_codigo=per_codigo, tipopago=tipopagoint, clase=clase,
                                                      sec_codigo=self.get_sec_id())
            return self.res200({'creds': creds, 'totales': sumas})
        elif accion == 'gdet':
            cre_codigo = self.get_request_param('codcred')
            datoscredito = tasicredao.get_datos_credito(cre_codigo)
            return self.res200({'datoscred': datoscredito})
        elif accion == 'listargrid':
            tipo = self.get_request_param('tipo')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            filtro = self.get_request_param('filtro')
            limit = self.get_request_param('limit')
            first = self.get_request_param('first')
            tipopago = self.get_request_param('tipopago')
            doexp = self.get_request_param('doexp')  # Indica si se debe buscar para exportacion de datos
            tipopagoint = 0
            if cadenas.es_nonulo_novacio(tipopago):
                tipopagoint = int(tipopago)

            if doexp == '1':
                data = tasicredao.listar_for_export(tipo, desde, hasta, filtro, sec_id=self.get_sec_id(),
                                                    tipopago=tipopagoint, limit=limit)
            else:
                data = tasicredao.listar(tipo, desde, hasta, filtro, sec_id=self.get_sec_id(),
                                         tipopago=tipopagoint, limit=limit, first=first)
            """
            totalsalopend = 0
            if int(first) == 0:
                totalsalopend = tasicredao.get_total_deudas(tipo=tipo, sec_codigo=self.get_sec_id())
            """
            return self.res200({'grid': data})
        elif accion == 'gformcrea':
            clase = self.get_request_param('clase')
            codref = self.get_request_param('ref')
            form = tasicredao.get_form(clase=clase, per_codigo=codref, sec_codigo=self.get_sec_id())
            return self.res200({'form': form})
        elif accion == 'report_cxp_provs':
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            prov = self.get_request_param('prov')
            first = self.get_request_param('first')
            limit = self.get_request_param('limit')
            doexp = self.get_request_param('doexp')  # Indica si se debe buscar para exportacion de datos

            if not cadenas.es_nonulo_novacio(first):
                first = 0
            if not cadenas.es_nonulo_novacio(limit):
                limit = 50

            report_serv = CuentasPorPagarProvsService(self.dbsession)
            if doexp == '1':
                data = report_serv.get_report_for_export(from_date=desde, to_date=hasta, provider_code=prov,
                                                         limit=limit)
            else:
                data = report_serv.get_report(from_date=desde, to_date=hasta, provider_code=prov, first=first,
                                              limit=limit)
            return self.res200({'report': data})
        elif accion == 'gridprov':
            limit = self.get_request_param('limit')
            first = self.get_request_param('first')
            tipopago = self.get_request_param('tipopago')
            prov = self.get_request_param('prov')
            doexp = self.get_request_param('doexp')

            tipopagoint = 0
            if cadenas.es_nonulo_novacio(tipopago):
                tipopagoint = int(tipopago)

            report_serv = CuentasPorPagarProvsService(self.dbsession)
            data = report_serv.find(provider_code=prov, tipopago=tipopagoint, first=first, limit=limit)
            return self.res200({'grid': data})
        elif accion == "detailscredprov":
            codcredprov = self.get_request_param('credprov')
            report_serv = CuentasPorPagarProvsService(self.dbsession)
            result = report_serv.find_details(crpr_codigo=codcredprov)
            return self.res200({'details': result})

    def collection_post(self):
        accion = self.get_rqpa()
        tasicredao = TAsicreditoDao(self.dbsession)
        if accion == 'crea':
            formtosave = self.get_json_body()
            trn_codigo_gen = tasicredao.create_from_referente(formtosave=formtosave, usercrea=self.get_user_id())
            msg = 'Operación exitosa'
            return self.res200({'trncod': trn_codigo_gen, 'msg': msg})
        elif accion == 'crea_deudas_provs':
            report_serv = CuentasPorPagarProvsService(self.dbsession)
            form = self.get_json_body()
            result = report_serv.crear_asientos_cuenta_por_pagar(lista_data=form['items'],
                                                                 user_crea=self.get_user_id(),
                                                                 sec_id=self.get_sec_id(),
                                                                 sales_from=form['from'],
                                                                 sales_to=form['to'], )
            if result:
                return self.res200({'msg': 'Cuentas por pagar registradas exitósamente'})
            else:
                return self.res400({'msg': 'No se crearon cuenta por pagar, favor revisar los datos'})
