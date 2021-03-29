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
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TBilleteraDao(BaseDao):

    def get_form(self):
        tparamdao = TParamsDao(self.dbsession)
        seq = tparamdao.get_next_sequence_bill()

        sqlcajasdisp = """
        select ic_id, ic_nombre, ic_code from titemconfig a where tipic_id = 3 and ic_estado =1 and ic_clasecc in ('B','E')
        and ic_haschild = false and ic_id not in (select ic_id from tbilletera where bil_estado = 1)
         order by a.ic_nombre
        """
        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code')
        cajasdisp = self.all(sqlcajasdisp, tupla_desc)

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
            'haycajasdisp': 1 if len(cajasdisp) > 0 else 0
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

    def listar(self):
        sql = """
        select bil.bil_id, bil.bil_code, bil.bil_nombre, bil.bil_fechacrea, bil.bil_usercrea, bil.bil_saldo, 
        bil.bil_saldoini, bil.bil_obs, bil.ic_id, ic.ic_nombre
        from tbilletera bil 
        join titemconfig ic on ic.ic_id = bil.ic_id
        where bil_estado = 1 order by bil_nombre asc 
        
        """
        tupla_desc = ('bil_id', 'bil_code', 'bil_nombre', 'bil_fechacrea',
                      'bil_usercrea', 'bil_saldo', 'bil_saldoini', 'bil_obs', 'ic_id', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def listar_min(self):
        sql = """
        select bil.bil_id, bil.bil_code, bil.bil_nombre, bil.ic_id, 
        bil.bil_nombre||' - '||bil.bil_code||' - '||round(bil.bil_saldo,2) as bilnomcodsald 
        from tbilletera bil where bil_estado = 1 order by bil_nombre asc
        """
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

    def crear(self, form, user_crea):
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
        else:
            # se procede a crear una cuenta contable
            sqlparent = """select ic_padre from titemconfig 
            where tipic_id = 3 and ic_estado =1 and ic_clasecc = 'E' order by ic_code asc limit 1"""
            ic_padre = self.first_col(sqlparent, 'ic_padre')
            if ic_padre is None:
                raise ErrorValidacionExc('No se ha configurado el plan de cuentas para CAJA, verificar')

            itemconfigdao = TItemConfigDao(self.dbsession)
            ic_id = itemconfigdao.crea_ctacontable_billetera(bill_nombre=formsave['bil_nombre'],
                                                             bill_obs=formsave['bil_obs'],
                                                             ic_padre=ic_padre,
                                                             user_crea=user_crea)
        tbilletera = TBilletera()
        tbilletera.bil_code = cadenas.strip_upper(formsave['bil_code'])
        tbilletera.bil_nombre = cadenas.strip_upper(formsave['bil_nombre'])
        tbilletera.bil_saldoini = float(formsave['bil_saldoini'])
        tbilletera.bil_saldo = tbilletera.bil_saldoini
        tbilletera.bil_obs = cadenas.strip(formsave['bil_obs'])
        tbilletera.bil_fechacrea = datetime.datetime.now()
        tbilletera.bil_usercrea = user_crea
        tbilletera.bil_estado = 1
        tbilletera.ic_id = ic_id
        if int(formsave['bil_autogencode']) == 1:
            tparamsdao = TParamsDao(self.dbsession)
            tparamsdao.update_sequence_billetera()

        self.dbsession.add(tbilletera)
