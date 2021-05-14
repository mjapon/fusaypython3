# coding: utf-8
"""
Fecha de creacion 26/12/2019
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tpersona.tpersona_model import TPersona
from fusayrepo.utils import cadenas, fechas, ctes

log = logging.getLogger(__name__)


class TPersonaDao(BaseDao):
    BASE_SQL = u"""
    select per_id,
               per_ciruc,
               per_nombres,
               per_apellidos,
               per_direccion,
               per_telf,
               per_movil,
               per_email,
               per_tipo,
               per_lugnac,
               per_nota,
               per_fechanac,
               per_genero,
               per_estadocivil,
               per_lugresidencia, 
               per_ocupacion from tpersona
    """
    BASE_TUPLA_DESC = ('per_id',
                       'per_ciruc',
                       'per_nombres',
                       'per_apellidos',
                       'per_direccion',
                       'per_telf',
                       'per_movil',
                       'per_email',
                       'per_tipo',
                       'per_lugnac',
                       'per_nota',
                       'per_fechanac',
                       'per_genero',
                       'per_estadocivil',
                       'per_lugresidencia',
                       'per_ocupacion')

    @staticmethod
    def get_form():
        return {
            'per_id': 0,
            'per_ciruc': '',
            'per_nombres': '',
            'per_apellidos': '',
            'per_direccion': '',
            'per_telf': '',
            'per_movil': '',
            'per_email': '',
            'per_fecreg': '',
            'per_tipo': 1,
            'per_lugnac': None,
            'per_nota': '',
            'per_fechanac': '',
            'per_fechanacobj': '',
            'per_genero': None,
            'per_estadocivil': 1,
            'per_lugresidencia': None,
            'per_ocupacion': None,
            'per_edad': {'years': 0, 'months': 0, 'days': 0}
        }

    def get_datos_completos(self, per_ciruc):
        """
        Retorna los datos completos de una persona
        :param per_ciruc:
        :return: per_id,
            per_ciruc,
            per_nombres,
            per_apellidos,
            per_direccion,
            per_telf,
            per_movil,
            per_email,
            per_fecreg,
            per_tipo,
            per_lugnac,
            per_nota,
            per_fechanac,
            per_genero,
            per_estadocivil,
            per_lugresidencia
        """
        sql = u"""select
            per_id,
            per_ciruc,
            per_nombres,
            per_apellidos,
            per_direccion,
            per_telf,
            per_movil,
            per_email,
            per_fecreg,
            per_tipo,
            per_lugnac,
            per_nota,
            per_fechanac,
            per_genero,
            per_estadocivil,
            per_lugresidencia from tpersona where per_ciruc = '{0}' 
        """.format(cadenas.strip(per_ciruc))

        tupla_desc = ('per_id',
                      'per_ciruc',
                      'per_nombres',
                      'per_apellidos',
                      'per_direccion',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'per_fecreg',
                      'per_tipo',
                      'per_lugnac',
                      'per_nota',
                      'per_fechanac',
                      'per_genero',
                      'per_estadocivil',
                      'per_lugresidencia',
                      'per_ocupacion')
        return self.first(sql, tupla_desc)

    @staticmethod
    def _aux_add_per_edad(result):
        try:
            if result is not None:
                if cadenas.es_nonulo_novacio(result['per_fechanac']):
                    edad = fechas.get_edad(fechas.parse_cadena(result['per_fechanac']))
                    result['per_edad'] = edad
                else:
                    result['per_edad'] = {'years': 0, 'months': 0, 'days': 0}
        except Exception as ex:
            log.error('Error controlado al tratar se setear edad', ex)

    def buscar_porciruc(self, per_ciruc):
        sql = "{0} where per_ciruc = '{1}'".format(self.BASE_SQL, cadenas.strip(per_ciruc))
        result = self.first(sql, tupla_desc=self.BASE_TUPLA_DESC)
        self._aux_add_per_edad(result)

        return result

    def aux_busca_por_prop_full(self, propname, propvalue):
        tupla_desc = ('per_id',
                      'per_ciruc',
                      'per_nombres',
                      'per_apellidos',
                      'per_direccion',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'per_tipo',
                      'per_lugnac',
                      'per_nota',
                      'per_fechanac',
                      'per_genero',
                      'per_estadocivil',
                      'per_lugresidencia',
                      'per_ocupacion',
                      'per_tiposangre',
                      'genero',
                      'estadocivil',
                      'profesion',
                      'tiposangre',
                      'tiporef',
                      'residencia')
        sql = """   
                    select per_id,
                       per_ciruc,
                       per_nombres,
                       per_apellidos,
                       per_direccion,
                       per_telf,
                       per_movil,
                       per_email,
                       per_tipo,
                       per_lugnac,
                       per_nota,
                       per_fechanac,
                       per_genero,
                       per_estadocivil,
                       per_lugresidencia,
                       per_ocupacion,
                       per_tiposangre,
                        coalesce(genlval.lval_nombre,'') as genero,
                        coalesce(estclval.lval_nombre,'') as estadocivil,
                        coalesce(profval.lval_nombre,'') as profesion,
                        coalesce(tipsanval.lval_nombre, '') as tiposangre,
                        coalesce(tiporefval.lval_nombre, '') as tiporef,
                        coalesce(lugar.lug_nombre,'') as residencia
                        from tpersona paciente
                            left join public.tlistavalores genlval on paciente.per_genero = genlval.lval_id and genlval.lval_cat=1
                            left join public.tlistavalores estclval on paciente.per_estadocivil = estclval.lval_id and estclval.lval_cat=2
                            left join public.tlistavalores profval on paciente.per_ocupacion = profval.lval_id and profval.lval_cat=3
                            left join public.tlistavalores tipsanval on paciente.per_tiposangre = tipsanval.lval_id and tipsanval.lval_cat=4
                            left join public.tlistavalores tiporefval on paciente.per_tipo = coalesce(tiporefval.lval_valor,'1')::int and tiporefval.lval_cat=5
                            left join public.tlugar lugar on paciente.per_lugresidencia = lugar.lug_id
                        where {0} = {1}""".format(cadenas.strip(propname), cadenas.strip(str(propvalue)))
        result = self.first(sql, tupla_desc)
        self._aux_add_per_edad(result)

        return result

    def buscar_porciruc_full(self, per_ciruc):
        return self.aux_busca_por_prop_full('per_ciruc', "'{0}'".format(per_ciruc))

    def buscar_porperid_full(self, per_id):
        return self.aux_busca_por_prop_full('per_id', per_id)

    def get_entity_byid(self, per_id):
        return self.dbsession.query(TPersona).filter(TPersona.per_id == per_id).first()

    def buscar_porcodigo(self, per_id):
        sql = "{0} where per_id = {1}".format(self.BASE_SQL, per_id)
        return self.first(sql, self.BASE_TUPLA_DESC)

    def buscar_poremail(self, per_email):
        sql = "{0} where per_email = '{1}'".format(self.BASE_SQL, cadenas.strip(per_email))
        return self.first(sql, tupla_desc=self.BASE_TUPLA_DESC)

    def buscar_pornomapelci(self, filtro, solo_cedulas=True, limit=30, offsset=0):
        basesql = u"""
        select per_id,
                        per_ciruc,
                        per_genero,
                        per_nombres||' '||coalesce(per_apellidos,'') as nomapel,
                        per_lugresidencia,
                        coalesce(tlugar.lug_nombre,'') as lugresidencia
                        from tpersona
                        left join public.tlugar on tpersona.per_lugresidencia = tlugar.lug_id
        """
        concedula = u" coalesce(per_ciruc,'')!='' and per_id>0" if solo_cedulas else ''

        if cadenas.es_nonulo_novacio(filtro):
            palabras = cadenas.strip_upper(filtro).split()
            filtromod = []
            for cad in palabras:
                filtromod.append(u"%{0}%".format(cad))

            nombreslike = u' '.join(filtromod)
            filtrocedulas = u" per_ciruc like '{0}%'".format(cadenas.strip(filtro))

            sql = u"""{basesql}
                        where ((per_nombres||' '||per_apellidos like '{nombreslike}') or ({filtrocedulas})) and {concedula} order by 4 limit {limit} offset {offset}
                    """.format(nombreslike=nombreslike,
                               concedula=concedula,
                               limit=limit,
                               offset=offsset,
                               filtrocedulas=filtrocedulas,
                               basesql=basesql)

            tupla_desc = ('per_id', 'per_ciruc', 'per_genero', 'nomapel', 'per_lugresidencia', 'lugresidencia')
            return self.all(sql, tupla_desc)
        else:
            sql = u"""{basesql} where {concedula}
             order by 4 limit {limit} offset {offset}
            """.format(basesql=basesql, limit=limit, offset=offsset, concedula=concedula)

        tupla_desc = ('per_id', 'per_ciruc', 'per_genero', 'nomapel', 'per_lugresidencia', 'lugresidencia')
        return self.all(sql, tupla_desc)

    def existe_ciruc(self, per_ciruc):
        sql = u"select count(*) as cuenta from tpersona t where t.per_ciruc = '{0}'".format(per_ciruc)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def existe_email(self, per_email):
        sql = "select count(*) as cuenta from tpersona t where t.per_email = '{0}'".format(per_email)
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def listar_medicos(self, med_tipo, med_estado=1):
        sql = u"""
                select per.per_id,
                    med.med_id,
                    per.per_ciruc,
                    per.per_genero,
                    per.per_nombres||' '||coalesce(per.per_apellidos,'') as nomapel
                from tpersona per
                join tmedico med on med.per_id = per.per_id 
                where med.med_tipo = {tipo} and med.med_estado = {estado} order by nomapel
                """.format(tipo=med_tipo,
                           estado=med_estado)
        tupla_desc = ('per_id', 'med_id', 'per_ciruc', 'per_genero', 'nomapel')
        return self.all(sql, tupla_desc)

    def listar_por_tipo(self, per_tipo):
        sql = """
        select  per_id,
                per_ciruc,
                per_nombres,
                per_apellidos,
                per_direccion,
                per_telf,      
                per_movil,     
                per_email,     
                per_fecreg,    
                per_tipo,      
                per_lugnac,    
                per_nota from tpersona where per_tipo = {0} order by per_nombres
        """.format(per_tipo)

        tupla_desc = ('per_id',
                      'per_ciruc',
                      'per_nombres',
                      'per_apellidos',
                      'per_direccion',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'per_fecreg',
                      'per_tipo',
                      'per_lugnac',
                      'per_nota')

        return self.all(sql, tupla_desc)

    @staticmethod
    def _aux_set_per_ocupacion(form, tpersona):
        if 'per_ocupacion' in form and cadenas.es_nonulo_novacio(form['per_ocupacion']):
            if type(form['per_ocupacion']) is dict:
                per_ocupacion = form['per_ocupacion']['lval_id']
            else:
                per_ocupacion = form['per_ocupacion']
            tpersona.per_ocupacion = per_ocupacion

    @staticmethod
    def _aux_set_per_genero(form, tpersona):
        if 'per_genero' in form and cadenas.es_nonulo_novacio(form['per_genero']):
            per_genero = form['per_genero']
            tpersona.per_genero = per_genero

    @staticmethod
    def _aux_set_per_telf(form, tpersona):
        if 'per_telf' in form:
            per_telf = form['per_telf']
            tpersona.per_telf = cadenas.strip(per_telf)

    @staticmethod
    def _aux_set_per_fechanac(form, tpersona):
        if 'per_fechanacp' in form:
            per_fechanac_txt = form['per_fechanacp']
            if cadenas.es_nonulo_novacio(per_fechanac_txt):
                per_fechanac = fechas.parse_cadena(per_fechanac_txt)
                tpersona.per_fechanac = per_fechanac

        elif 'per_fechanac' in form:
            per_fechanac_txt = form['per_fechanac']
            if cadenas.es_nonulo_novacio(per_fechanac_txt):
                per_fechanac = fechas.parse_cadena(per_fechanac_txt)
                tpersona.per_fechanac = per_fechanac

    @staticmethod
    def _aux_set_per_estado_civil(form, tpersona):
        if 'per_estadocivil' in form and cadenas.es_nonulo_novacio(form['per_estadocivil']):
            if type(form['per_estadocivil']) is dict:
                per_estadocivil = form['per_estadocivil']['lval_id']
            else:
                per_estadocivil = form['per_estadocivil']
            tpersona.per_estadocivil = per_estadocivil

    @staticmethod
    def _aux_set_per_lug_residencia(form, tpersona):
        if 'per_lugresidencia' in form and cadenas.es_nonulo_novacio(form['per_lugresidencia']):
            if type(form['per_lugresidencia']) is dict:
                per_lugresidencia = form['per_lugresidencia']['lug_id']
            else:
                per_lugresidencia = form['per_lugresidencia']

            if per_lugresidencia != 0:
                tpersona.per_lugresidencia = per_lugresidencia

    @staticmethod
    def _aux_set_per_tiposangre(form, tpersona):
        if 'per_tiposangre' in form and cadenas.es_nonulo_novacio(form['per_tiposangre']):
            if type(form['per_tiposangre']) is dict:
                per_tiposangre = form['per_tiposangre']['lval_id']
            else:
                per_tiposangre = form['per_tiposangre']
            tpersona.per_tiposangre = per_tiposangre

    @staticmethod
    def _aux_set_per_direccion(form, tpersona):
        if 'per_direccion' in form:
            per_direccion = cadenas.strip(form['per_direccion'])
            if len(per_direccion) > 0:
                tpersona.per_direccion = per_direccion
            else:
                tpersona.per_direccion = ''

    @staticmethod
    def _aux_set_per_email(form, tpersona):
        if cadenas.es_nonulo_novacio(form['per_email']):
            tpersona.per_email = cadenas.strip(form['per_email'])
        else:
            tpersona.per_email = None

    @staticmethod
    def _aux_set_per_movil(form, tpersona):
        per_movil = cadenas.strip_upper(form['per_movil'])
        if len(per_movil) > 0:
            tpersona.per_movil = per_movil
        else:
            tpersona.per_movil = ''

    @staticmethod
    def _aux_set_per_nombres(form, tpersona):
        per_nombres = cadenas.strip_upper(form['per_nombres'])
        if len(per_nombres) > 0:
            tpersona.per_nombres = per_nombres
        else:
            tpersona.per_nombres = ''

    @staticmethod
    def _aux_set_per_apellidos(form, tpersona):
        per_apellidos = cadenas.strip_upper(form['per_apellidos'])
        if len(per_apellidos) > 0:
            tpersona.per_apellidos = per_apellidos
        else:
            tpersona.per_apellidos = ''

    @staticmethod
    def _aux_set_per_tipo(form, tpersona):
        tpersona.per_tipo = form['per_tipo']

    @staticmethod
    def _aux_valid_ci_ruc(form):
        if not cadenas.es_nonulo_novacio(form['per_ciruc']):
            raise ErrorValidacionExc('Ingrese el número de cédula, ruc o pasaporte')

    @staticmethod
    def _aux_valid_nombres(form):
        if not cadenas.es_nonulo_novacio(form['per_nombres']):
            raise ErrorValidacionExc('Ingrese los nombres')

    def _chk_existe_ciruc(self, form):
        if self.existe_ciruc(per_ciruc=form['per_ciruc']):
            raise ErrorValidacionExc(
                'El número de ci/ruc o pasaporte {0} ya está registrado, ingrese otro'.format(form['per_ciruc']))

    def _set_datos_ref(self, form, tpersona):

        self._aux_set_per_nombres(form, tpersona)

        self._aux_set_per_apellidos(form, tpersona)

        self._aux_set_per_movil(form, tpersona)

        self._aux_set_per_email(form, tpersona)

        self._aux_set_per_fechanac(form, tpersona)

        self._aux_set_per_genero(form, tpersona)

        self._aux_set_per_estado_civil(form, tpersona)

        self._aux_set_per_lug_residencia(form, tpersona)

        self._aux_set_per_telf(form, tpersona)

        self._aux_set_per_ocupacion(form, tpersona)

        self._aux_set_per_tiposangre(form, tpersona)

        self._aux_set_per_direccion(form, tpersona)

        self._aux_set_per_tipo(form, tpersona)

    def actualizar(self, per_id, form):
        tpersona = self.get_entity_byid(per_id)
        if tpersona is not None:
            self._aux_valid_ci_ruc(form)
            self._aux_valid_nombres(form)

            per_ciruc = cadenas.strip(form['per_ciruc'])

            if len(per_ciruc) > 0:
                current_per_ciruc = cadenas.strip(tpersona.per_ciruc)
                if per_ciruc != current_per_ciruc:
                    self._chk_existe_ciruc(form)
                    tpersona.per_ciruc = per_ciruc

            self._set_datos_ref(form, tpersona)

            self.dbsession.add(tpersona)
            self.dbsession.flush()
            return True
        return False

    def crear(self, form, permit_ciruc_null=False):
        if not permit_ciruc_null:
            self._aux_valid_ci_ruc(form)

        per_ciruc = cadenas.strip_upper(form['per_ciruc'])
        if cadenas.es_nonulo_novacio(form['per_ciruc']):
            self._chk_existe_ciruc(form)
        else:
            per_ciruc = None

        self._aux_valid_nombres(form)

        tpersona = TPersona()
        tpersona.per_ciruc = per_ciruc
        tpersona.per_lugnac = 0
        tpersona.per_telf = ''
        tpersona.per_nota = ''
        tpersona.per_fecreg = datetime.now()

        self._set_datos_ref(form, tpersona)

        self.dbsession.add(tpersona)
        self.dbsession.flush()

        return tpersona.per_id

    def contar_transaccs(self, per_codigo):
        """
        Retorna el total de transaccion de facturas, compras, cuentas por cobrar y pagar que tiene un referente
        :param per_codigo:
        :return: {compras,ventas,cxcobrar,cxpagar}
        """
        sql = """
        select count(*) as cuenta, tra_codigo from tasiento where per_codigo = {0}
        and trn_valido = 0 and trn_docpen = 'F' and trn_pagpen = 'F'
        group by tra_codigo
        """.format(per_codigo)

        tupla_desc = ('cuenta', 'tra_codigo')
        alltransacss = self.all(sql, tupla_desc)

        sql = """
        select count(*) as cuenta, cred.cre_tipo from tasicredito cred
            join tasidetalle det on cred.dt_codigo = det.dt_codigo
            join tasiento asi on det.trn_codigo = asi.trn_codigo and asi.trn_valido = 0 and asi.trn_docpen = 'F' and asi.trn_pagpen = 'F'
            where asi.per_codigo = {0}
            group by cred.cre_tipo
        """.format(per_codigo)
        tupla_desc = ('cuenta', 'cre_tipo')
        allcreds = self.all(sql, tupla_desc)

        totales = {
            'compras': 0,
            'ventas': 0,
            'cxcobrar': 0,
            'cxpagar': 0
        }

        for item in alltransacss:
            if item['tra_codigo'] == ctes.TRA_COD_FACT_VENTA or item['tra_codigo'] == ctes.TRA_COD_NOTAVENTA:
                totales['ventas'] += item['cuenta']
            elif item['tra_codigo'] == ctes.TRA_COD_FACT_COMPRA:
                totales['compras'] += item['cuenta']

        for item in allcreds:
            if item['cre_tipo'] == 1:
                totales['cxcobrar'] += item['cuenta']
            elif item['cre_tipo'] == 2:
                totales['cxpagar'] += item['cuenta']

        return totales
