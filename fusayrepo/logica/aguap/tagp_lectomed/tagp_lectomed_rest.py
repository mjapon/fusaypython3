# coding: utf-8
"""
Fecha de creacion 5/17/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.aguap.tagp_contrato.tagp_contrato_dao import TAgpContratoDao
from fusayrepo.logica.aguap.tagp_lectomed.tagp_lectomed_dao import LectoMedAguaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tagplectomed', path='/api/tagplectomed/{lmd_id}', cors_origins=('*',))
class LectoMedAguaRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        lectomeddao = LectoMedAguaDao(self.dbsession)
        if accion == 'form':
            form = lectomeddao.get_form()
            return self.res200({'form': form})
        elif accion == 'previous':
            numed = self.get_request_param('numed')
            anio = self.get_request_param('anio')
            mes = self.get_request_param('mes')
            lastlectomed = lectomeddao.get_previous_lectomed(mdg_num=numed, anio=anio, mes=mes)
            if lastlectomed is not None:
                return self.res200({'lectomed': lastlectomed})
            else:
                return self.res404({'msg': 'No hay registro de lecturas de medidor'})
        elif accion == 'gantlecto':
            mdg_id = self.get_request_param('mdgid')
            anio = self.get_request_param('anio')
            mes = self.get_request_param('mes')
            lastlectomed = lectomeddao.get_back_lecto(mdg_id=mdg_id, anio=anio, mes=mes)
            if lastlectomed is not None:
                return self.res200({'lectomed': lastlectomed})
            else:
                return self.res404({'msg': 'No hay registro de lecturas de medidor'})

        elif accion == 'last':
            numed = self.get_request_param('numed')
            lastlectomed = lectomeddao.get_last_lectomed(mdg_num=numed)
            if lastlectomed is not None:
                return self.res200({'lectomed': lastlectomed})
            else:
                return self.res404({'msg': 'No hay registro de lecturas de medidor'})

        elif accion == 'listar':
            numed = self.get_request_param('numed')
            lecturas = lectomeddao.listar_lecturas_medidor(mdg_id=numed, limit=24)
            return self.res200({'lecturas': lecturas})

        elif accion == 'conspend':
            codmed = self.get_request_param('codmed')
            consumos = lectomeddao.get_lecturas(mdg_id=codmed)
            return self.res200(consumos)
        elif accion == 'lectopend':
            codmed = self.get_request_param('codmed')
            lectopends = lectomeddao.get_lecturas_pendientes(mdg_id=codmed)
            contratodao = TAgpContratoDao(self.dbsession)
            contrato = contratodao.find_by_mdg_id(codmed)
            haspagospend = True
            msg = ''
            if len(lectopends) == 0:
                haspagospend = False
                msg = 'No tiene pagos pendientes'
            else:
                msg = 'Tiene {0} pago(s) pendiente(s)'.format(len(lectopends))

            return self.res200({'lectopends': lectopends, 'msg': msg, 'haspagospend': haspagospend,
                                'contrato': contrato})
        elif accion == 'lectopendbyid':
            lmd_id = self.get_request_param('codlecto')
            lectopends = lectomeddao.get_lectopend_by_lmd_id(lmd_id=lmd_id)
            return self.res200({'lectopends': lectopends})

    def collection_post(self):
        accion = self.get_rqpa()
        lectomeddao = LectoMedAguaDao(self.dbsession)
        if accion == 'crea':
            form = self.get_json_body()
            trn_codigo = lectomeddao.crear(form=form, user_crea=self.get_user_id(), sec_id=self.get_sec_id(),
                                           tdv_codigo=self.get_tdv_codigo())
            msg_pago_adel = ''
            if trn_codigo > 0:
                msg_pago_adel = 'Esta lectura de agua fue registrada como pagada, ya que el referente tenia un adelanto registrado'
            return self.res200(
                {'msg': 'Registrado exitósamente', 'trn_codigo': trn_codigo, 'msg_pago_adel': msg_pago_adel})
        elif accion == 'anular':
            form = self.get_json_body()
            lectomeddao.anular(lmd_id=form['lmd_id'], lmd_useranula=self.get_user_id())
            return self.res200({'msg': 'Anulado exitoso'})
