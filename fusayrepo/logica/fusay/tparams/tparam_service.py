from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ForbiddenExc
from fusayrepo.logica.fusay.tfuserrol.tfuserrol_dao import TFuserRolDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import ctes


class TParamService(BaseDao):

    def check_user_has_app_config_rol(self, user_id):
        tfuserdao = TFuserRolDao(self.dbsession)
        if tfuserdao.user_has_permiso(user_id=user_id, prm_abreviacion=ctes.PERMISO_APP_CONFIG):
            return True
        else:
            raise ForbiddenExc('No tiene permisos para administrar parámetros del sistema')

    def find(self, filtro, estado, seccion, userid):
        if self.check_user_has_app_config_rol(userid):
            tparamsdao = TParamsDao(self.dbsession)
            return tparamsdao.find(filtro, estado, seccion)

    def update(self, form, userupd):
        if self.check_user_has_app_config_rol(userupd):
            tparamsdao = TParamsDao(self.dbsession)
            tparamsdao.update_param_value(form['tprm_id'], form, userupd)

    def get_ctas_contables_for_movs_caja(self, prefijo):

        paramdao = TParamsDao(self.dbsession)
        mapeo_claves = {
            f"{prefijo}_{cta}": nombre
            for cta, nombre in [
                (ctes.CTA_CONTABLE_MOV_NC_DEBE, 'nc_debe'),
                (ctes.CTA_CONTABLE_MOV_NC_HABER, 'nc_haber'),
                (ctes.CTA_CONTABLE_MOV_ND_DEBE, 'nd_debe'),
                (ctes.CTA_CONTABLE_MOV_ND_HABER, 'nd_haber')
            ]
        }

        abreviaciones_combinadas = list(mapeo_claves.keys())
        paramsvalue = paramdao.get_params_value(abreviaciones=abreviaciones_combinadas)
        
        resultmap = {nombre: "" for nombre in mapeo_claves.values()}

        if paramsvalue is not None:
            for it in paramsvalue:
                tprm_abrev = it['tprm_abrev']
                if tprm_abrev in mapeo_claves:
                    resultmap[mapeo_claves[tprm_abrev]] = it['tprm_val']

        return resultmap

    @staticmethod
    def get_form_crea():
        return {
            'codigo': '',
            'descripcion': '',
            'valor': '',
            'seccion': 0
        }

    def crear(self, form, usercrea):
        tparamdao = TParamsDao(self.dbsession)
        tparamdao.create_param_value(form, usercrea)
