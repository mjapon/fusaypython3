import datetime

from sqlalchemy import and_

from fusayrepo.logica.aguap.tagp_models import TagpPagosMavil, TagpPago
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
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
            'fecha': fechas.get_str_fecha_actual(),
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

    def find_tagppago(self, pg_id):
        return self.dbsession.query(TagpPago).filter(TagpPago.pg_id == pg_id).first()

    def find_pagos_trn_cod(self, trn_codigo):
        return self.dbsession.query(TagpPago).filter(
            and_(TagpPago.trn_codigo == trn_codigo, TagpPago.pg_estado == 1)).all()

    def find_by_trn_codigo(self, trn_codigo):
        sql = """
        select pg_id, trn_codigo from tagp_pago  where pg_estado = 1 and trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('pg_id', 'trn_codigo')
        return self.first(sql, tupla_desc)

    def anula_solo_pago(self, pg_id):
        tagp_pagomavil = self.find_tagppago(pg_id)
        tagp_pagomavil.pg_estado = 2
        self.dbsession.add(tagp_pagomavil)

    def anular(self, form, useranula):
        pgm_id = form['pgm_id']
        tagp_pagomavil = self.find_tagppago(pgm_id)
        if tagp_pagomavil is not None:
            tagp_pagomavil.pg_estado = 2
            self.dbsession.add(tagp_pagomavil)

            # Se debe anular todos los pagos asociados con la factura:
            all_pagos_factura = self.find_pagos_trn_cod(tagp_pagomavil.trn_codigo)
            if all_pagos_factura is not None:
                for it_pago in all_pagos_factura:
                    it_pago.pg_estado = 2
                    self.dbsession.add(it_pago)

            tasientodao = TasientoDao(self.dbsession)
            if not tasientodao.is_transacc_in_state(trn_codigo=tagp_pagomavil.trn_codigo, state=1):
                tasientodao.anular(trn_codigo=tagp_pagomavil.trn_codigo, user_anula=useranula, obs_anula='')

    def get_grid_pagos_mavil(self, anio, mes, fecha):
        griddao = TGridDao(self.dbsession)
        # swhere = ' and extract(year from asi.trn_fecha) =  {0} and extract(month from asi.trn_fecha)  = {1} '.format(
        #    anio, mes)
        # swhere = ' and lm.lmd_anio = {0} and lm.lmd_mes = {1} '.format(anio, mes)
        # swhere = ' and extract(year from asi.trn_fecha) = {0} and extract(month from asi.trn_fecha) = {1} '.format(anio,
        #                                                                                                           mes)

        swhere = """ and date(asi.trn_fecha) >= '{0}'""".format(fechas.format_cadena_db(fecha))

        return griddao.run_grid(grid_nombre='agp_pagosmavil', swhere=swhere)

    def get_grid_newcontratosmavil(self, anio, mes, fecha):
        paramsdao = TParamsDao(self.dbsession)
        fechainicobro = paramsdao.get_param_value('agp_fecinicbreg')
        if cadenas.es_nonulo_novacio(fechainicobro):
            # fechainicobrodb = fechas.format_cadena_db(fechainicobro)
            swhere = """ and date(cna_fechacrea)>={0}""".format(fechas.format_cadena_db('fecha'))
            griddao = TGridDao(self.dbsession)
            return griddao.run_grid(grid_nombre='agp_newcnmavil', swhere=swhere)
        return []

    def get_reporte_pagos_mavil(self, anio, mes, fecha):
        grid_facturas = self.get_grid_pagos_mavil(anio, mes, fecha)
        grid_newcontract = self.get_grid_newcontratosmavil(anio, mes, fecha)

        keys = {}
        totalfacturas = 0.0
        datares = []
        if 'data' in grid_facturas:
            # Primero hago un filtro
            for item in grid_facturas['data']:
                key = '{0}_{1}'.format(item['trn_codigo'], item['dt_codigo'])
                if key not in keys.keys():
                    keys[key] = '1'
                    datares.append(item)

            for row in datares:
                totalfacturas += row['comavil']

        totalnewcontracts = 0.0
        if 'data' in grid_newcontract:
            for row in grid_newcontract['data']:
                totalnewcontracts += row['comavil']

        total = totalfacturas + totalnewcontracts

        grid_facturas['data'] = datares

        return {
            'gridfacts': grid_facturas,
            'gridcontracts': grid_newcontract,
            'totalfact': numeros.roundm2(totalfacturas),
            'totalnc': numeros.roundm2(totalnewcontracts),
            'total': numeros.roundm2(total)
        }
