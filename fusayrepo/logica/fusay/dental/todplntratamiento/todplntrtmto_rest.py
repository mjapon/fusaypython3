# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.fusay.dental.todplntratamiento.todplntrtmto_dao import TOdPlanTratamientoDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.ttpdv.ttpdv_dao import TtpdvDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.logica.fusay.ttransaccpago.ttransaccpago_dao import TTransaccPagoDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/todplantrata', path='/api/todplantrata/{pnt_id}', cors_origins=('*',))
class TodPlanTrantamientoRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        plantrata_dao = TOdPlanTratamientoDao(self.dbsession)
        tasientodao = TasientoDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)
        ttransaccpagodao = TTransaccPagoDao(self.dbsession)

        if accion == 'form':
            formplan = plantrata_dao.get_form(pac_id=self.get_request_param('pac'))

            tra_codigo = self.get_request_param('tra_cod')
            tdv_codigo = self.get_request_param('tdv_codigo')
            ttpdvdao = TtpdvDao(self.dbsession)
            alm_codigo = ttpdvdao.get_alm_codigo_from_tdv_codigo(tdv_codigo)
            form_cab = tasientodao.get_form_cabecera(tra_codigo, alm_codigo, 0, tdv_codigo)
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)
            formaspago = ttransaccpagodao.get_formas_pago(tra_codigo=tra_codigo)
            form_det = tasientodao.get_form_detalle(sec_codigo=self.get_sec_id())
            form_pago = tasientodao.get_form_pago()

            tpersonadao = TPersonaDao(self.dbsession)
            medicos = tpersonadao.listar_medicos(med_tipo=2)

            return self.res200(
                {'formplan': formplan, 'formcab': form_cab, 'ttransacc': ttransacc, 'formaspago': formaspago,
                 'formdet': form_det, 'medicos': medicos, 'formpago': form_pago})

        elif accion == 'listar':
            pac_id = self.get_request_param('pac')
            items = plantrata_dao.listar(pac_id=pac_id)
            return self.res200({'items': items})
        elif accion == 'gdet':
            planid = self.get_request_param('pnt_id')
            plan = plantrata_dao.get_detalles(pnt_id=planid)
            if plan is not None:
                tasientodao = TasientoDao(self.dbsession)
                doc = tasientodao.get_documento(trn_codigo=plan['trn_codigo'])
                return self.res200({'plan': plan, 'doc': doc})
            else:
                return {'status': 404, 'msg': 'No se puedo encontrar el plan de tratamient para codigo especificado'}

    def collection_post(self):
        accion = self.get_request_param('accion')
        plantratadao = TOdPlanTratamientoDao(self.dbsession)

        if accion == 'crea':
            jbody = self.get_json_body()
            res = plantratadao.crear(form=jbody, user_crea=self.get_user_id())

            return self.res200({'msg': 'Registrado exitosamente', 'res': res})

        elif accion == 'chgestado':
            jbody = self.get_json_body()
            nuevo_estado = jbody['nv_estado']
            plantratadao.cambiar_estado(pnt_id=jbody['pnt_id'], nuevo_estado=nuevo_estado,
                                        user_upd=self.get_user_id())
            msg = 'Cambio de estado exitoso'
            if int(nuevo_estado) == 5:
                msg = 'Registro anulado exitosamente'

            return self.res200({'msg': msg})
