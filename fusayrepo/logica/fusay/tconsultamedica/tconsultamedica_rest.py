# coding: utf-8
"""
Fecha de creacion 5/24/20
@autor: mjapon
"""
import logging

from cornice.resource import resource

from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tconsultamedica.tconsultamedica_dao import TConsultaMedicaDao
from fusayrepo.utils.pyramidutil import TokenView

log = logging.getLogger(__name__)


@resource(collection_path='/api/tconsultam', path='/api/tconsultam/{cosm_id}', cors_origins=('*',))
class TConsultaMedicaRest(TokenView):

    def collection_get(self):
        accion = self.get_request_param('accion')
        tconsultam_dao = TConsultaMedicaDao(self.dbsession)
        if accion == 'form':
            form = tconsultam_dao.get_form()
            return {'status': 200, 'form': form}
        elif accion == 'form_odonto':
            form = tconsultam_dao.get_form_odonto()
            return {'status': 200, 'form': form}

        elif accion == 'cie10data':
            cie10data = tconsultam_dao.get_cie10data()
            return {'status': 200, 'cie10data': cie10data}

        elif accion == 'listaatenciones':
            ciruc = self.get_request_param('ciruc')
            items = tconsultam_dao.get_historia_porpaciente(per_ciruc=ciruc)
            # antecedespers = tconsultam_dao.get_antecedentes_personales(per_ciruc=ciruc)
            return {'status': 200, 'items': items}
        elif accion == 'odontograma':
            ciruc = self.get_request_param('ciruc')
            odontograma = tconsultam_dao.get_odontograma(per_ciruc=ciruc)
            return {'status': 200, 'odontograma': odontograma}

        elif accion == 'findhistbycod':
            codhistoria = self.get_request_param('codhistoria')
            datoshistoria = tconsultam_dao.get_datos_historia(cosm_id=codhistoria)
            return {'status': 200, 'datoshistoria': datoshistoria}
        elif accion == 'findhistantecedentes':
            pac_id = self.get_request_param('pac')
            antecedentes = tconsultam_dao.get_antecedentes_paciente(pac_id)
            hasvalue = len(list(filter(lambda it: it['valorreg'] != '', antecedentes))) > 0
            return {'antecedentes': antecedentes, 'hasvalue': hasvalue}
        elif accion == 'galertexfis':
            valor = self.get_request_param('valor')
            categ = self.get_request_param('categ')
            # 1-tension arterial
            # 3-indice de masa corporal
            result, color = tconsultam_dao.buscar_categoria_valor(valor, int(categ))
            return {'status': 200, 'result': result, 'color': color}
        elif accion == 'cpreviasfiltropag':  # Esta opcion lista las atenciones previas realizadas
            filtro = self.get_request_param('filtro')
            desde = self.get_request_param('desde')
            hasta = self.get_request_param('hasta')
            lastpage = self.get_request_param('pag')
            tipo = self.get_request_param('tipo')
            intlastpage = 0
            try:
                intlastpage = int(lastpage)
            except Exception as ex:
                log.error('Error al parsear a int la pagina', ex)

            limit = 50
            offset = intlastpage * limit

            if int(tipo) == 2:
                items, lenitems = tconsultam_dao.listar_odonto(filtro=filtro, desde=desde, hasta=hasta, limit=limit,
                                                               offset=offset)
            else:
                items, lenitems = tconsultam_dao.listar(filtro=filtro, desde=desde, hasta=hasta, tipo=tipo, limit=limit,
                                                        offset=offset)

            hasMore = items is not None and lenitems == limit
            return {'status': 200, 'items': items, 'hasMore': hasMore, 'nextp': intlastpage + 1}
        elif accion == 'proxcitas':
            tipofecha = self.get_request_param('tipofecha')
            tipo = self.get_request_param('tipocita')
            if int(tipo) == 2:
                res, fechastr = tconsultam_dao.listarproxcitasod_grid(int(tipofecha))
            elif int(tipo) == 1:
                res, fechastr = tconsultam_dao.listarproxcita_grid(int(tipofecha), tipocita=tipo)
            else:
                res, fechastr = tconsultam_dao.listarproxcitasgen_grid(int(tipofecha), tipocita=tipo)

            return {'status': 200, 'grid': res, 'fechas': fechastr}

    def collection_post(self):
        accion = self.get_request_param('accion')
        if 'registra' == accion:
            tconsultam_dao = TConsultaMedicaDao(self.dbsession)
            formdata = self.get_request_json_body()
            msg, cosm_id = tconsultam_dao.registrar(form=formdata, usercrea=self.get_user_id())
            return {'status': 200, 'msg': msg, 'ccm': cosm_id}
        elif accion == 'saveantp':
            formdata = self.get_request_json_body()
            tconsultam_dao = TConsultaMedicaDao(self.dbsession)
            tconsultam_dao.save_antencedentes_paciente(pac_id=formdata['pac'], antecedentes=formdata['antecedentes'])
            return {'status': 200, 'msg': 'Registro exitoso'}

        elif 'anular' == accion:
            tconsultam_dao = TConsultaMedicaDao(self.dbsession)
            formdata = self.get_request_json_body()
            tconsultam_dao.anular(cosm_id=formdata['cosm_id'], form=formdata, useranula=self.get_user_id())
            return {'status': 200, 'msg': 'Registro anulado exitósamente'}
        elif 'editar' == accion:
            tconsultam_dao = TConsultaMedicaDao(self.dbsession)
            formdata = self.get_request_json_body()
            msg, cosm_id = tconsultam_dao.actualizar(form=formdata, useredita=self.get_user_id())
            return {'status': 200, 'msg': msg, 'ccm': cosm_id}
        else:
            raise ErrorValidacionExc(u'Ninguna acción especificada')
