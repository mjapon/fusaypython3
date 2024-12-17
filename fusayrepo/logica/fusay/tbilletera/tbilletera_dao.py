# coding: utf-8
"""
Fecha de creacion 3/18/21
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tbilletera.tbilletera_model import TBilletera
from fusayrepo.logica.fusay.tbilletera.tbilleterahist_model import TBilleteraHist
from fusayrepo.logica.fusay.tbilletera.tbilleteramov_dao import TBilleteraMovDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils import cadenas, fechas

log = logging.getLogger(__name__)


class TBilleteraDao(BaseDao):

    def get_form(self, sec_id):
        tparamdao = TParamsDao(self.dbsession)
        seq = tparamdao.get_next_sequence_bill()

        sqlcajasdisp = """
        select a.ic_id, ic_nombre, ic_code from titemconfig a
        join titemconfig_sec ics on a.ic_id = ics.ic_id and ics.sec_id = {0} 
        where tipic_id = 3 and ic_estado =1 and ic_clasecc in ('B','E')
        and ic_haschild = false and a.ic_id not in (select ic_id from tbilletera where bil_estado = 1)
         order by a.ic_nombre
        """.format(sec_id)
        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code')
        cajasdisp = self.all(sqlcajasdisp, tupla_desc)

        tsecciondao = TSeccionDao(self.dbsession)
        secciones = tsecciondao.listar()
        seccionesf = []
        for seccion in secciones:
            seccionesf.append({'value': seccion['sec_id'] == sec_id,
                               'sec_id': seccion['sec_id'],
                               'seccion': seccion})
        return {
            'bil_id': 0,
            'bil_code': {'required': True, 'value': 'BILL_0000{0}'.format(seq)},
            'bil_nombre': {'required': True, 'value': ''},
            'bil_saldo': {'required': True, 'value': 0.0},
            'bil_saldoini': {'required': True, 'value': 0.0},
            'bil_obs': {'required': False, 'value': ''},
            'bil_autogencode': 1,
            'ic_id': {'required': True, 'value': 0},
            'cajas': cajasdisp,
            'haycajasdisp': 1 if len(cajasdisp) > 0 else 0,
            'secciones': seccionesf
        }

    def existe_nombre(self, bill_nombre):
        sql = "select count(*) as cuenta from tbilletera where bil_nombre = '{0}' and bil_estado = 1".format(
            cadenas.strip_upper(bill_nombre))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def existe_code(self, bill_code):
        sql = "select count(*) as cuenta from tbilletera where bil_code = '{0}' and bil_estado = 1".format(
            cadenas.strip_upper(bill_code))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def listar(self, sec_id):
        sql = """
        select bil.bil_id, bil.bil_code, bil.bil_nombre, bil.bil_fechacrea, bil.bil_usercrea, bil.bil_saldo, 
        bil.bil_saldoini, bil.bil_obs, bil.ic_id, ic.ic_nombre
        from tbilletera bil 
        join titemconfig ic on ic.ic_id = bil.ic_id
        join titemconfig_sec ics on ics.ic_id = ic.ic_id and ics.sec_id = {0}
        where bil_estado = 1 order by bil_nombre asc
        """.format(sec_id)
        tupla_desc = ('bil_id', 'bil_code', 'bil_nombre', 'bil_fechacrea',
                      'bil_usercrea', 'bil_saldo', 'bil_saldoini', 'bil_obs', 'ic_id', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def listar_min(self, sec_id):
        sql = """
        select bil.bil_id, bil.bil_code, bil.bil_nombre, bil.ic_id, 
        bil.bil_nombre||' - '||bil.bil_code||' - '||round(bil.bil_saldo,2) as bilnomcodsald 
        from tbilletera bil
        join titemconfig ic on bil.ic_id = ic.ic_id
        join titemconfig_sec ics on ic.ic_id = ics.ic_id and ics.sec_id = {0}
        where bil_estado = 1 order by bil_nombre asc
        """.format(sec_id)
        tupla_desc = ('bil_id', 'bil_code', 'bil_nombre', 'ic_id', 'bilnomcodsald')
        return self.all(sql, tupla_desc)

    def bill_has_moves(self, bil_id):
        sql = """        
        select det.cta_codigo, count(*) as cuenta from tasidetalle det
                                         join tasiento tasi on tasi.trn_valido = 0 and tasi.trn_docpen = 'F' and tasi.trn_valido = 0
                                         join tbilletera bill on det.cta_codigo = bill.ic_id and bill.bil_estado = 1
        where bill.bil_id = {0} group by det.cta_codigo
        """.format(bil_id)

        tupla_desc = ('cta_codigo', 'cuenta')
        res = self.first(sql, tupla_desc)
        if res is not None and len(res) > 0:
            return res['cuenta'] > 0
        return False

    def find_by_id(self, bil_id):
        return self.dbsession.query(TBilletera).filter(TBilletera.bil_id == bil_id).first()

    def anular(self, bil_id, user_anula):
        tbilletera = self.find_by_id(bil_id)
        if tbilletera is not None:
            # Se debe veerificar si esta billetera esta en un modelo contable asociado
            sql = """
            select count(*) as cuenta from ttransaccpago where cta_codigo = {0}
            """.format(tbilletera.ic_id)
            cuenta = self.first_col(sql, 'cuenta')
            if cuenta > 0:
                raise ErrorValidacionExc(
                    'No se puede anular esta billetera, esta siendo usada como forma de pago en transacciones de compra o venta')

            tbilletera.bil_estado = 2
            titemconfigdao = TItemConfigDao(self.dbsession)
            titemconfigdao.anular(tbilletera.ic_id, user_anula)
            return 1
        return 0

    def update(self, form, user_update):
        formsave = {}
        for key in form.keys():
            if type(form[key]) is dict and 'value' in form[key].keys():
                formsave[key] = form[key]['value']
            else:
                formsave[key] = form[key]

        bil_id = formsave['bil_id']
        tbilletera = self.find_by_id(bil_id)

        if not cadenas.es_nonulo_novacio(formsave['bil_nombre']):
            raise ErrorValidacionExc('Debe ingresar el nombre de la billetera')
        if not cadenas.es_nonulo_novacio(formsave['bil_code']):
            raise ErrorValidacionExc('Debe ingresar el código de la billetera')

        if tbilletera is not None:
            if cadenas.strip_upper(formsave['bil_code']) != cadenas.strip_upper(tbilletera.bil_code):
                if self.existe_code(formsave['bil_code']):
                    raise ErrorValidacionExc('Ya existe una billetera con ese código')

            if cadenas.strip_upper(formsave['bil_nombre']) != cadenas.strip_upper(tbilletera.bil_nombre):
                if self.existe_nombre(formsave['bil_nombre']):
                    raise ErrorValidacionExc('Ya existe una billetera con ese nombre, ingrese otra')

            tbilletera.bil_code = cadenas.strip_upper(formsave['bil_code'])
            tbilletera.bil_nombre = cadenas.strip_upper(formsave['bil_nombre'])
            tbilletera.bil_obs = cadenas.strip(formsave['bil_obs'])

            if not self.bill_has_moves(bil_id):
                tbilletera.bil_saldoini = float(formsave['bil_saldoini'])
                tbilletera.bil_saldo = tbilletera.bil_saldoini

            self.dbsession.add(tbilletera)
            icdao = TItemConfigDao(self.dbsession)
            icdao.save_secciones(secciones=form['secciones'], ic_id=tbilletera.ic_id)

    def crear(self, form, user_crea, sec_id):
        formsave = {}
        for key in form.keys():
            if type(form[key]) is dict and 'value' in form[key].keys():
                formsave[key] = form[key]['value']
            else:
                formsave[key] = form[key]

        if not cadenas.es_nonulo_novacio(formsave['bil_nombre']):
            raise ErrorValidacionExc('Debe ingresar el nombre de la billetera')
        if not cadenas.es_nonulo_novacio(formsave['bil_code']):
            raise ErrorValidacionExc('Debe ingresar el código de la billetera')

        if self.existe_nombre(formsave['bil_nombre']):
            raise ErrorValidacionExc('Ya existe una billetera con ese nombre, ingrese otra')

        if self.existe_code(formsave['bil_code']):
            raise ErrorValidacionExc('Ya existe una billetera con ese código')

        # Verificar si se debe crear la cuenta contable
        ic_id = int(formsave['ic_id'])
        if int(formsave['haycajasdisp']) == 1:
            if ic_id == 0:
                raise ErrorValidacionExc('Debe seleccionar la cuenta contable')

            icdao = TItemConfigDao(self.dbsession)
            icdao.save_secciones(secciones=form['secciones'], ic_id=ic_id)
        else:
            # se procede a crear una cuenta contable
            sqlparent = """select ic_padre from titemconfig ic 
            join titemconfig_sec ics on ic.ic_id = ics.ic_id and ics.sec_id = {0} 
            where tipic_id = 3 and ic_estado =1 and ic_clasecc = 'E' order by ic_code asc limit 1""".format(sec_id)

            ic_padre = self.first_col(sqlparent, 'ic_padre')
            if ic_padre is None:
                raise ErrorValidacionExc('No se ha configurado el plan de cuentas para CAJA, verificar')

            itemconfigdao = TItemConfigDao(self.dbsession)
            ic_id = itemconfigdao.crea_ctacontable_billetera(bill_nombre=formsave['bil_nombre'],
                                                             bill_obs=formsave['bil_obs'],
                                                             ic_padre=ic_padre,
                                                             user_crea=user_crea, secciones=form['secciones'])
        tbilletera = TBilletera()
        tbilletera.bil_code = cadenas.strip_upper(formsave['bil_code'])
        tbilletera.bil_nombre = cadenas.strip_upper(formsave['bil_nombre'])
        tbilletera.bil_saldoini = float(formsave['bil_saldoini'])
        tbilletera.bil_saldo = 0.0
        tbilletera.bil_obs = cadenas.strip(formsave['bil_obs'])
        tbilletera.bil_fechacrea = datetime.datetime.now()
        tbilletera.bil_usercrea = user_crea
        tbilletera.bil_estado = 1
        tbilletera.ic_id = ic_id
        if int(formsave['bil_autogencode']) == 1:
            tparamsdao = TParamsDao(self.dbsession)
            tparamsdao.update_sequence_billetera()

        if tbilletera.bil_saldoini > 0:
            # Registrar un asiento contable para registrar el asiento inicial
            billmovdao = TBilleteraMovDao(self.dbsession)
            billmovdao.crea_saldo_inicial(cta_codigo=ic_id, saldoinicial=tbilletera.bil_saldoini,
                                          sec_codigo=sec_id,
                                          usercrea=user_crea)

        self.dbsession.add(tbilletera)

    def get_fecha_inicio_contab(self, sec_id):
        sql = f"select tprm_val from tparams where tprm_abrev = 'fecha_ini_contab' and tprm_seccion = {sec_id} "
        result = self.first_raw(sql)
        fec_ini_contabdb = ''
        if result is not None and len(result) > 0:
            fec_ini_contabdb = " and date(asi.trn_fecha)>='{0}' ".format(fechas.format_cadena_db(result[0]))
        return fec_ini_contabdb

    def totalizar(self, cta_id, user_crea, sec_id=None):
        """
        Totaliza billetera
        """
        fecha_inicio = ''
        if sec_id is not None:
            fecha_inicio = self.get_fecha_inicio_contab(sec_id)

        sql_mov_bills = f"""
        with data as (
            select det.dt_codigo, asi.trn_fecha, det.dt_debito, 
            case when det.dt_debito = 1 then round(det.dt_valor,2) else null end as credito,
            case when det.dt_debito = -1 then round(det.dt_valor,2) else null end as debito,
            det.cta_codigo from tasidetalle det join tasiento asi on det.trn_codigo = asi.trn_codigo
            where coalesce(det.cta_codigo, 0)> 0 and asi.trn_valido = 0 and asi.trn_docpen = 'F' and asi.tra_codigo != 14
              and det.cta_codigo ={cta_id} {fecha_inicio}  order by asi.trn_fecha
            )
            select dt_codigo, trn_fecha, debito, credito, 
               coalesce(sum(abs(credito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  -
               coalesce(sum(abs(debito)) over (order by trn_fecha asc rows between unbounded preceding and current row), 0)  as saldo,
               cta_codigo
            from data order by trn_fecha asc
        """
        results = self.all_raw(sql_mov_bills)

        # Borramos el historial
        self.dbsession.query(TBilleteraHist).filter(TBilleteraHist.cta_codigo == cta_id).delete()

        inserted = 0
        for result in results:
            debito = result[2] if result[2] else None
            credito = result[3] if result[3] else None

            newrow = TBilleteraHist()
            newrow.dt_codigo = result[0]
            newrow.bh_debito = debito
            newrow.bh_credito = credito
            newrow.bh_saldo = result[4]
            newrow.bh_fechacrea = datetime.datetime.now()
            newrow.bh_usercrea = user_crea
            newrow.bh_valido = 0
            newrow.bh_fechatransacc = result[1]
            newrow.cta_codigo = result[5]
            self.dbsession.add(newrow)
            self.flush()

            inserted += 1
            print(newrow.bh_id)

        return inserted
