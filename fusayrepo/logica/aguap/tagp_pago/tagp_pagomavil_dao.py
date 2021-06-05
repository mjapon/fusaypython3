import datetime

from fusayrepo.logica.aguap.tagp_models import TagpPagosMavil
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.public.tmes_dao import PublicTMesDao
from fusayrepo.utils import fechas, cadenas, numeros


class TagpPagoMavilDao(BaseDao):

    def get_form(self):
        tmesdao = PublicTMesDao(self.dbsession)
        meses = tmesdao.get_current_previus()
        anios = tmesdao.get_current_previus_year()

        form = {
            'pgm_id': 0,
            'pgm_anio': fechas.get_anio_actual(),
            'pgm_mes': fechas.get_mes_actual(),
            'pgm_total': 0.0,
            'pgm_obs': ''
        }
        return {
            'form': form,
            'meses': meses,
            'anios': anios
        }

    def existe_pago(self, pgm_anio, pgm_mes):
        sql = """
        select count(*) as cuenta from tagp_pagosmavil where pgm_anio = {0} and pgm_mes = {1} and pgm_estado = 0        
        """.format(pgm_anio, pgm_mes)
        return self.first_col(sql, 'cuenta') > 0

    def crear(self, form, user_crea):
        if self.existe_pago(pgm_anio=form['pgm_anio'], pgm_mes=form['pgm_mes']):
            raise ErrorValidacionExc('Ya existe un registrado para el año y mes seleccionado, no se puede registrar ')

        tagp_pagosmavil = TagpPagosMavil()
        tagp_pagosmavil.pgm_anio = form['pgm_anio']
        tagp_pagosmavil.pgm_mes = form['pgm_mes']
        tagp_pagosmavil.pgm_fechacrea = datetime.datetime.now()
        tagp_pagosmavil.pgm_usercrea = user_crea
        tagp_pagosmavil.pgm_total = form['pgm_total']
        tagp_pagosmavil.pgm_obs = cadenas.strip(form['pgm_obs'])

        self.dbsession.add(tagp_pagosmavil)

    def find_by_id(self, pgm_id):
        return self.dbsession.query(TagpPagosMavil).filter(TagpPagosMavil.pgm_id == pgm_id).first()

    def anular(self, form):
        pgm_id = form['pgm_id']
        tagp_pagomavil = self.find_by_id(pgm_id)
        if tagp_pagomavil is not None:
            tagp_pagomavil.pgm_estado = 1
            self.dbsession.add(tagp_pagomavil)

    def get_grid_pagos_mavil(self, anio, mes):
        griddao = TGridDao(self.dbsession)
        swhere = ' and lm.lmd_anio = {0} and lm.lmd_mes = {1} '.format(anio, mes)
        return griddao.run_grid(grid_nombre='agp_pagosmavil', swhere=swhere)

    def get_grid_newcontratosmavil(self, anio, mes):
        paramsdao = TParamsDao(self.dbsession)
        fechainicobro = paramsdao.get_param_value('agp_fecinicbreg')
        if cadenas.es_nonulo_novacio(fechainicobro):
            fechainicobrodb = fechas.format_cadena_db(fechainicobro)
            swhere = """ and date(cna_fechacrea)>={0} and date_part('year',cna_fechacrea) = {1}
             and date_part('month',cna_fechacrea) = {2}""".format(fechainicobrodb, anio, mes)
            griddao = TGridDao(self.dbsession)
            return griddao.run_grid(grid_nombre='agp_newcnmavil', swhere=swhere)
        return []

    def get_reporte_pagos_mavil(self, anio, mes):
        grid_facturas = self.get_grid_pagos_mavil(anio, mes)
        grid_newcontract = self.get_grid_newcontratosmavil(anio, mes)

        totalfacturas = 0.0
        if 'data' in grid_facturas:
            for row in grid_facturas['data']:
                totalfacturas += row['comavil']

        totalnewcontracts = 0.0
        if 'data' in grid_newcontract:
            for row in grid_newcontract['data']:
                totalnewcontracts += row['comavil']

        total = totalfacturas + totalnewcontracts

        return {
            'gridfacts': grid_facturas,
            'gridcontracts': grid_newcontract,
            'totalfact': numeros.roundm2(totalfacturas),
            'totalnc': numeros.roundm2(totalnewcontracts),
            'total': numeros.roundm2(total)
        }
