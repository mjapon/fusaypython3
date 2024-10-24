from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.financiero.tfin_movimientos.tfin_movimientos_dao import TFinMovimientosDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_service import TParamService
from fusayrepo.utils import ctes, numeros
from fusayrepo.utils.cloneutils import clone_formdet


def check_exist_param(key, ctas_movs, param):
    if len(ctas_movs[key]) == 0:
        raise ErrorValidacionExc('Parametro {0} no configurado, favor verificar'.format(param))


def check_exist_cta(datos_cta, cta):
    if datos_cta is None:
        raise ErrorValidacionExc('No pude recuperar la informacion de la cuenta contable {0}'.format(cta))


def crea_asidetalle(formdet, valor, cta_codigo, debito):
    debedet = clone_formdet(formdet)
    debedet['dt_debito'] = debito
    debedet['dt_valor'] = numeros.roundm2(valor)
    debedet['cta_codigo'] = cta_codigo
    debedet['ic_clasecc'] = ''
    return debedet


class TFinMovimientosService(BaseDao):

    def generar_asiento(self, mov_id, sec_codigo, usercrea):
        paramservice = TParamService(self.dbsession)
        ctas_movs = paramservice.get_ctas_contables_for_movs_caja()

        check_exist_param('nc_debe', ctas_movs, ctes.CTA_CONTABLE_MOV_NC_DEBE)
        check_exist_param('nc_haber', ctas_movs, ctes.CTA_CONTABLE_MOV_NC_HABER)
        check_exist_param('nd_debe', ctas_movs, ctes.CTA_CONTABLE_MOV_ND_DEBE)
        check_exist_param('nd_haber', ctas_movs, ctes.CTA_CONTABLE_MOV_ND_HABER)

        tfinmovsdao = TFinMovimientosDao(self.dbsession)
        mov_details = tfinmovsdao.get_mov_details(mov_id=mov_id)
        if mov_details is None:
            raise ErrorValidacionExc('No pude recuperar información de movimiento')

        mov_deb_cred = mov_details['mov_deb_cred']
        mov_total_transa = mov_details['mov_total_transa']
        per_id = mov_details['per_id']
        tipomovobs = 'NC' if mov_deb_cred == 1 else 'ND'

        tasientodao = TasientoDao(self.dbsession)
        formasiento = tasientodao.get_form_asiento(sec_codigo=sec_codigo)

        observacion = 'P/R Movimiento en cuenta de tipo {0} del socio Nro {1}'.format(tipomovobs, per_id)
        formasiento['formasiento']['trn_docpen'] = 'F'
        formasiento['formasiento']['trn_observ'] = observacion
        formasiento['formref']['per_id'] = per_id

        formdet = formasiento['formdet']
        detalles = []

        cta_debe = ctas_movs['nc_debe']
        cta_haber = ctas_movs['nc_haber']
        if mov_deb_cred == -1:
            cta_debe = ctas_movs['nd_debe']
            cta_haber = ctas_movs['nd_haber']

        itemconfidao = TItemConfigDao(self.dbsession)
        datos_cta_debe = itemconfidao.get_detalles_ctacontable_by_code(ic_code=cta_debe)
        check_exist_cta(datos_cta_debe, cta_debe)

        datos_cta_haber = itemconfidao.get_detalles_ctacontable_by_code(ic_code=cta_haber)
        check_exist_cta(datos_cta_haber, cta_haber)

        debedet = crea_asidetalle(formdet, numeros.roundm2(mov_total_transa), datos_cta_debe['ic_id'], debito=1)
        detalles.append(debedet)

        haberdet = crea_asidetalle(formdet, numeros.roundm2(mov_total_transa), datos_cta_haber['ic_id'], debito=-1)
        detalles.append(haberdet)

        formasiento['detalles'] = detalles

        trn_codigo_gen = tasientodao.crear_asiento(formcab=formasiento['formasiento'],
                                                   formref=formasiento['formref'],
                                                   usercrea=usercrea,
                                                   detalles=formasiento['detalles'], update_datosref=False)

        return trn_codigo_gen
