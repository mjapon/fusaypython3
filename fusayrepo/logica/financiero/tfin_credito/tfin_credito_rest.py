# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.financiero.tfin_amortiza.tfin_amortiza_dao import TFinAmortizaDao
from fusayrepo.logica.financiero.tfin_credito.tfin_adjunto_cred_dao import TFinAdjuntoCredDao
from fusayrepo.logica.financiero.tfin_credito.tfin_credito_dao import TFinCreditoDao
from fusayrepo.utils import fechas
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path="/api/fin/credito", path='/api/fin/credito/{cre_id}', cors_origins=('*',))
class TFinCreditoRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        credito_dao = TFinCreditoDao(self.dbsession)
        if accion == 'form':
            form = credito_dao.get_form(per_id=0)
            return self.res200({'form': form})
        elif accion == 'formlista':
            form = credito_dao.get_form_lista()
            return self.res200({'form': form['form'], 'estados': form['estados']})
        elif accion == 'tblamor':
            amordao = TFinAmortizaDao(self.dbsession)
            cre_id = self.get_request_param('cred')
            tabla_amor = amordao.get_tabla(cre_id)
            return self.res200('tblamor', tabla_amor)
        elif accion == 'listargrid':
            filtro = self.get_request_param('filtro')
            estado = self.get_request_param('estado')
            grid = credito_dao.get_grid(filtro, estado)
            totales = credito_dao.totalizar_grid(grid)
            return self.res200({'grid': grid, 'totales':totales})
        elif accion == 'gdetcredfull':
            cre_id = self.get_request_param('creid')
            datoscred = credito_dao.get_datos_credito_full(cre_id=cre_id)
            return self.res200({
                'datoscred': datoscred
            })
        elif accion == 'gdetcred':
            cre_id = self.get_request_param('creid')
            datoscred = credito_dao.get_datos_credito(cre_id=cre_id)
            return self.res200({
                'datoscred': datoscred
            })
        elif accion == 'gformadj':
            cre_id = self.get_request_param('creid')
            adjdao = TFinAdjuntoCredDao(self.dbsession)
            form = adjdao.get_form(cre_id)
            return self.res200({'form': form})
        elif accion == 'listadj':
            cre_id = self.get_request_param('creid')
            adjdao = TFinAdjuntoCredDao(self.dbsession)
            adjuntos = adjdao.listar(cre_id)
            return self.res200({'adjuntos': adjuntos})

    def collection_post(self):
        accion = self.get_rqpa()
        cj_credito_dao = TFinCreditoDao(self.dbsession)
        if accion == 'crea':
            cre_id = cj_credito_dao.crear(form=self.get_json_body(), user_crea=self.get_user_id())
            msg = 'Crédito registrado exitósamente'
            return self.res200({'msg': msg, 'codcred': cre_id})
        elif accion == 'calctablamor':
            amordao = TFinAmortizaDao(self.dbsession)
            form = self.get_json_body()
            result = amordao.calcular_tabla(monto_prestamo=float(form['cre_monto']), tasa_interes=form['cre_tasa'],
                                            fecha_prestamo=fechas.parse_cadena(form['cre_fecprestamo']),
                                            ncuotas=int(form['cre_plazo']))
            return self.res200({
                'tabla': result
            })

        elif accion == 'chgstate':
            msg_res = cj_credito_dao.cambiar_estado(form=self.get_json_body(), user_edit=self.get_user_id(),
                                                    sec_codigo=self.get_sec_id())

            return self.res200({'msg': msg_res})
        elif accion == 'creaadj':
            body = self.get_json_body()
            adjdao = TFinAdjuntoCredDao(self.dbsession)
            adjdao.crear(form=body, user_crea=self.get_user_id())
            return self.res200({'msg': 'Adjunto registrado exitósamente'})
