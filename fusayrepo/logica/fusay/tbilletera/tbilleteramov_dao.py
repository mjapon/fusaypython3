# coding: utf-8
"""
Fecha de creacion 3/18/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.dental.todrxdocs.todrxdocs_dao import TOdRxDocsDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tbilletera.tbilletera_dao import TBilleteraDao
from fusayrepo.logica.fusay.tbilletera.tbilletera_model import TBilleteraMov
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TBilleteraMovDao(BaseDao):

    def get_tipos_mov(self):
        tipos = [
            {'label': 'Todos', 'value': 0},
            {'label': 'Ingreso', 'value': 1},
            {'label': 'Gasto', 'value': 2}
        ]

        return tipos

    def get_form_filtros(self):
        formfiltros = {
            'desde': '',
            'hasta': '',
            'tipo': 0,
            'cuenta': 0
        }

        return formfiltros

    def get_cuentas_bytipo_add_todos(self, tipo):
        cuentas = self.get_cuentas_bytipo(tipo=tipo)
        cuentasret = [{'ic_id': 0, 'ic_nombre': 'Todos'}]
        for cuenta in cuentas:
            cuentasret.append(cuenta)

        return cuentasret

    def get_cuentas_bytipo(self, tipo):
        tparamdao = TParamsDao(self.dbsession)
        cod_cta_ing = tparamdao.get_param_value('codRootCtaContabIng')
        cod_cta_gast = tparamdao.get_param_value('codRootCtaContabGast')

        if cod_cta_ing is None:
            raise ErrorValidacionExc(
                'El código raiz de la cuenta contable ingresos (codRootCtaContabIng) no ha sido definido ')
        if cod_cta_gast is None:
            raise ErrorValidacionExc(
                'El código raiz de la cuenta contable gastos (codRootCtaContabGast) no ha sido definido ')

        codeparent = '{0}.'.format(cod_cta_ing)
        if int(tipo) == 2:
            codeparent = '{0}.'.format(cod_cta_gast)

        sql = """
        select ic_id, ic_code, ic_nombre, ic_clasecc from titemconfig where
        tipic_id = 3 and ic_estado = 1 and ic_haschild = false and  ic_code like '{0}%' order by ic_nombre asc 
        """.format(codeparent)

        tupla_desc = ('ic_id', 'ic_code', 'ic_nombre', 'ic_clasecc')
        cuentasformov = self.all(sql, tupla_desc)

        return cuentasformov

    def get_form_mov(self, clase_mov):

        tparamdao = TParamsDao(self.dbsession)
        nextnumov = tparamdao.get_next_sequence_billmov()

        form = {
            'bmo_monto': 0.0,
            'bmo_fechatransacc': fechas.get_str_fecha_actual(),
            'bmo_numero': nextnumov,
            'bmo_codadj': 0,
            'trn_codigo': 0,
            'bmo_clase': clase_mov,
            'bmo_obs': '',
            'bmo_claseslist': [],
            'cuentas': [{'cta_codigo': 0, 'dt_valor': 0.0}],
            'billeteras': [{'cta_codigo': 0, 'dt_valor': 0.0}]
        }

        cuentasformov = self.get_cuentas_bytipo(tipo=clase_mov)

        billdao = TBilleteraDao(self.dbsession)
        billeterasformov = billdao.listar_min()

        tasientodao = TasientoDao(self.dbsession)
        formasiento = tasientodao.get_form_asiento()
        return {
            'formbillmov': form,
            'cuentasformov': cuentasformov,
            'billeterasformov': billeterasformov,
            'formasiento': formasiento
        }

    def clone_formdet(self, formdet):
        newformdet = {}
        for key in formdet.keys():
            newformdet[key] = formdet[key]
        return newformdet

    def find_by_id(self, bmo_id):
        return self.dbsession.query(TBilleteraMov).filter(TBilleteraMov.bmo_id == bmo_id).first()

    def anular(self, bmo_id, user_anula):
        tbilleteramov = self.find_by_id(bmo_id)
        if tbilleteramov is not None:
            tasientodao = TasientoDao(self.dbsession)
            tbilleteramov.bmo_estado = 2
            self.dbsession.add(tbilleteramov)
            tasientodao.anular(trn_codigo=tbilleteramov.trn_codigo, user_anula=user_anula,
                               obs_anula='AUT: Anulado por transaccion de ingreso/gasto')
        else:
            raise ErrorValidacionExc('No es posible anular este registro, ningún resultado')

    def confirmar(self, bmo_id):
        tbilleteramov = self.find_by_id(bmo_id)
        if tbilleteramov is not None:
            tasientodao = TasientoDao(self.dbsession)
            tbilleteramov.bmo_estado = 1
            tasientodao.update_trn_docpen(trn_codigo=tbilleteramov.trn_codigo, trn_docpen_value='F')
            self.dbsession.add(tbilleteramov)

    def crear(self, formtosave, usercrea):
        formbillmov = formtosave['form']
        if 'archivo' in formtosave:
            archivo = formtosave['archivo']

        formasiento = formtosave['formasiento']
        tbilleteramov = TBilleteraMov()

        tparamdao = TParamsDao(self.dbsession)
        nextnumov = tparamdao.get_next_sequence_billmov()
        tasientodao = TasientoDao(self.dbsession)

        formasiento['formasiento']['trn_fecreg'] = formbillmov['bmo_fechatransacc']
        formasiento['formasiento']['trn_docpen'] = 'T'
        formasiento['formasiento']['trn_observ'] = formbillmov['bmo_obs']
        formasiento['formref']['per_id'] = -1

        formdet = formasiento['formdet']

        bmo_clase = int(formbillmov['bmo_clase'])

        cuentas = formbillmov['cuentas']
        billeteras = formbillmov['billeteras']

        dtdebito_cuentas = -1
        dtdebito_bill = 1

        if bmo_clase == 2:
            dtdebito_cuentas = 1
            dtdebito_bill = -1

        detalles = []
        for cuenta in cuentas:
            if float(cuenta['dt_valor']) > 0:
                newformdet = self.clone_formdet(formdet)
                newformdet['dt_debito'] = dtdebito_cuentas
                newformdet['dt_valor'] = cuenta['dt_valor']
                if int(cuenta['cta_codigo']) == 0:
                    raise ErrorValidacionExc('Debe seleccionar la cuenta afectada')

                newformdet['cta_codigo'] = cuenta['cta_codigo']
                detalles.append(newformdet)

        for bill in billeteras:
            if float(bill['dt_valor']) > 0:
                newformdet = self.clone_formdet(formdet)
                newformdet['dt_debito'] = dtdebito_bill
                newformdet['dt_valor'] = bill['dt_valor']
                if int(bill['cta_codigo']) == 0:
                    raise ErrorValidacionExc('Debe seleccionar la billetera afectada')
                newformdet['cta_codigo'] = bill['cta_codigo']
                detalles.append(newformdet)

        formasiento['detalles'] = detalles

        trn_codigo_gen = tasientodao.crear_asiento(formcab=formasiento['formasiento'],
                                                   formref=formasiento['formref'],
                                                   usercrea=usercrea,
                                                   detalles=formasiento['detalles'])
        tbilleteramov.bmo_numero = nextnumov
        tbilleteramov.bmo_fechacrea = datetime.now()
        tbilleteramov.trn_codigo = trn_codigo_gen
        tbilleteramov.bmo_clase = formbillmov['bmo_clase']
        tbilleteramov.bmo_estado = 0
        tbilleteramov.bmo_monto = formbillmov['bmo_monto']
        tbilleteramov.bmo_fechatransacc = fechas.parse_cadena(formbillmov['bmo_fechatransacc'])

        if archivo is not None:
            todrxdocsdao = TOdRxDocsDao(self.dbsession)
            thefile = archivo['archivo']
            formfile = {
                'rxd_filename': archivo['rxd_filename'],
                'pac_id': -3,
                'rxd_tipo': 3,
                'rxd_nota': '',
                'rxd_nropieza': 0,
                'rxd_nombre': archivo['rxd_filename']
            }

            rxid = todrxdocsdao.crear(formfile, usercrea, thefile)
            tbilleteramov.bmo_codadj = rxid

        self.dbsession.add(tbilleteramov)
        tparamdao.update_sequence_billmov()

    def get_datos_mov(self, bmo_id):
        sql = """
        select mov.bmo_fechacrea, mov.bmo_fechatransacc, mov.bmo_id, mov.bmo_numero, mov.bmo_monto, mov.bmo_clase,
               mov.trn_codigo, asi.trn_observ, mov.bmo_estado, mov.bmo_codadj,
               case
                   when bmo_estado =0 then 'Pendiente'
                   when bmo_estado =1 then 'Confirmado'
                   when bmo_estado =2 then 'Anulado'
                   else 'Estado desconocido' end as estado,
               case
                   when bmo_clase = 1 then 'Ingreso'
                   when bmo_clase = 2 then 'Gasto'
                   when bmo_clase = 3 then 'Transferencia'
                   else 'Tipo Desconocido' end as clase,
            coalesce(vu.referente, '') as refusercrea,
            coalesce(vu.us_cuenta, '') as usercreacuenta,
            coalesce(mov.bmo_codadj,0) as rxd_id,
            coalesce(adj.rxd_filename,'') as rxd_filename,
            coalesce(adj.rxd_ext,'') as rxd_ext                                      
        from tbilleteramov mov
                 join tasiento asi on mov.trn_codigo = asi.trn_codigo
                 left join vusers vu on vu.us_id = asi.us_id
                 left join todrxdocs adj on adj.rxd_id = mov.bmo_codadj                 
        where mov.bmo_id = {0}        
        """.format(bmo_id)

        tupla_desc = (
            'bmo_fechacrea', 'bmo_fechatransacc', 'bmo_id', 'bmo_numero', 'bmo_monto', 'bmo_clase', 'trn_codigo',
            'trn_observ', 'bmo_estado', 'bmo_codadj', 'estado', 'clase', 'refusercrea', 'usercreacuenta', 'rxd_id',
            'rxd_filename', 'rxd_ext')

        datosmov = self.first(sql, tupla_desc)

        if datosmov is not None:
            tasientodao = TasientoDao(self.dbsession)
            datoasiento = tasientodao.get_datos_asientocontable(trn_codigo=datosmov['trn_codigo'])
            return {
                'datosmov': datosmov,
                'asiento': datoasiento
            }
        else:
            raise ErrorValidacionExc('No se pudo obtener los detalles del movimiento de ingreso/gasto registrado')

    def listar_grid(self, desde, hasta, tipo, cuenta):

        tgrid_dao = TGridDao(self.dbsession)
        andwhere = " and coalesce(ic.ic_clasecc,'') = 'E'"

        sfechas = ' '
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sfechas = " and (mov.bmo_fechatransacc between '{0}' and '{1}')".format(fechas.format_cadena_db(desde),
                                                                                    fechas.format_cadena_db(hasta))

        if tipo is not None and int(tipo) > 0:
            andwhere = " and mov.bmo_clase = {0} and coalesce(ic.ic_clasecc,'') != 'E'".format(tipo)
            if cuenta is not None and int(cuenta) > 0:
                andwhere = " and mov.bmo_clase = {0} and det.cta_codigo = {1}".format(tipo, cuenta)

        swhere = " {0} {1} ".format(sfechas, andwhere)

        data = tgrid_dao.run_grid(grid_nombre='ingrgastos', swhere=swhere)

        return data