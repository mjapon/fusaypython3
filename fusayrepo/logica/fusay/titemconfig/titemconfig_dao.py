# coding: utf-8
"""
Fecha de creacion 2/15/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_model import TItemConfig
from fusayrepo.logica.fusay.titemconfig_datosprod.titemconfigdatosprod_model import TItemConfigDatosProd
from fusayrepo.logica.fusay.tparams.tparam_dao import TParamsDao
from fusayrepo.utils import cadenas, ivautil, fechas

log = logging.getLogger(__name__)


class TItemConfigDao(BaseDao):

    def listar(self, filtro, sec_id):
        tgrid_dao = TGridDao(self.dbsession)
        swhere = u"ic.ic_code like '{0}%' or ic.ic_nombre like '{0}%'".format(
            cadenas.strip_upper(filtro)
        )
        data = tgrid_dao.run_grid(grid_nombre='productos', where=swhere, order='ic_nombre', sec_id=sec_id)
        return data

    def listarrubros_grid(self):
        tgrid_dao = TGridDao(self.dbsession)
        data = tgrid_dao.run_grid(grid_nombre='trubros')
        return data

    def busca_serv_dentales_filtro(self, filtro):
        limit = 50
        sql = """
        select a.ic_id, a.ic_nombre, a.ic_code,
               td.icdp_grabaiva,               
               td.icdp_preciocompra,
               td.icdp_precioventa,
               td.icdp_precioventamin,               
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_preciocompra),2) else td.icdp_preciocompra end as icdp_preciocompra_iva,
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventa),2) else td.icdp_precioventa end as icdp_precioventa_iva,
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventamin),2) else td.icdp_precioventamin end as icdp_precioventamin_iva
        from titemconfig a 
        join titemconfig_datosprod td on a.ic_id = td.ic_id
        where a.ic_estado = 1 and a.ic_dental = true and (a.ic_code like '{0}%' or a.ic_nombre like '{0}%') order by a.ic_nombre limit {1}
        """.format(cadenas.strip_upper(filtro), limit)

        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code', 'icdp_grabaiva', 'icdp_preciocompra', 'icdp_precioventa',
                      'icdp_precioventamin', 'icdp_preciocompra_iva', 'icdp_precioventa_iva', 'icdp_precioventamin_iva')

        return self.all(sql, tupla_desc)

    def busca_serv_dentales_all(self):
        sql = """
                select a.ic_id, a.ic_nombre, a.ic_code,
                       td.icdp_grabaiva,               
                       td.icdp_preciocompra,
                       td.icdp_precioventa,
                       td.icdp_precioventamin,               
                       case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_preciocompra),2) else td.icdp_preciocompra end as icdp_preciocompra_iva,
                       case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventa),2) else td.icdp_precioventa end as icdp_precioventa_iva,
                       case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventamin),2) else td.icdp_precioventamin end as icdp_precioventamin_iva
                from titemconfig a 
                join titemconfig_datosprod td on a.ic_id = td.ic_id
                where a.ic_estado = 1 and a.ic_dental = true  order by a.ic_nombre
                """

        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code', 'icdp_grabaiva', 'icdp_preciocompra', 'icdp_precioventa',
                      'icdp_precioventamin', 'icdp_preciocompra_iva', 'icdp_precioventa_iva', 'icdp_precioventamin_iva')

        return self.all(sql, tupla_desc)

    def listar_teleservicios(self):
        sql = """
        select ic.ic_id, ic.ic_nombre, sm.med_id, per.per_nombres ||' '|| per.per_apellidos as medico from titemconfig ic 
        join tserviciomedico sm on ic.ic_id = sm.serv_id 
        join tpersona per on per.per_id = sm.med_id 
        """
        tupla_desc = ('ic_id', 'ic_nombre', 'med_id', 'medico')

        return self.all(sql, tupla_desc)

    def get_prods_for_tickets(self):
        params_dao = TParamsDao(self.dbsession)
        arts_tickets = params_dao.get_param_value('artsTickets')
        sql = u"select ic_id, ic_nombre, ic_code from titemconfig where ic_id in ({0})".format(arts_tickets)
        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code')
        return self.all(sql, tupla_desc)

    def get_form(self):
        formic = {
            'ic_id': 0,
            'ic_nombre': '',
            'ic_code': '',
            'tipic_id': 1,
            'ic_nota': '',
            'catic_id': 1,
            'ic_fechacrea': '',
            'icdp_grabaiva': False,
            'icdp_preciocompra': 0.0,
            'icdp_preciocompra_iva': 0.0,
            'icdp_precioventa': 0.0,
            'icdp_precioventamin': 0.0,
            'icdp_proveedor': -2,
            'icdp_modcontab': 0,
            'icdp_fechacaducidad': '',
            'ic_dental': False
        }

        return formic

    def existe_artbynombre(self, ic_nombre):
        if (ic_nombre is not None and len(cadenas.strip(ic_nombre)) > 0):
            sql = u"select count(*) as cuenta from titemconfig where  ic_nombre = '{0}' and ic_estado=1".format(
                cadenas.strip(str(ic_nombre)))
            cuenta = self.first_col(sql, 'cuenta')
            return cuenta > 0
        return False

    def get_next_sequence_forcodbar(self):
        tparam_dao = TParamsDao(self.dbsession)
        return tparam_dao.get_next_sequence_codbar()

    def get_codbarnombre_articulo(self, codbar):
        sql = u"select ic_code, ic_nombre from titemconfig where  ic_code = '{0}'".format(
            cadenas.strip(str(codbar)))
        tupla_desc = ('ic_code', 'ic_nombre')
        return self.first(sql, tupla_desc)

    def existe_codbar(self, codbar):
        sql = u"select count(*) as cuenta from titemconfig where  ic_code = '{0}'".format(
            cadenas.strip(str(codbar)))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def find_byid(self, ic_id):
        return self.dbsession.query(TItemConfig).filter(TItemConfig.ic_id == ic_id).first()

    def get_form_rubro(self):
        form = {
            'ic_id': 0,
            'ic_nombre': '',
            'ic_code': '',
            'clsic_id': 0
        }
        return form

    def get_form_rubro_edit(self, ic_id):
        itemconfig = self.find_byid(ic_id)
        if itemconfig is not None:
            return itemconfig.__json__()
        return None

    def editar_rubro(self, form, user_edita):
        ic_id = form['ic_id']
        itemconfig = self.find_byid(ic_id)

        new_ic_nombre = cadenas.strip_upper(form['ic_nombre'])
        if not cadenas.es_nonulo_novacio(new_ic_nombre):
            raise ErrorValidacionExc('Debe ingresar el nombre del rubro')

        new_ic_code = cadenas.strip_upper(form['ic_code'])
        if not cadenas.es_nonulo_novacio(new_ic_code):
            raise ErrorValidacionExc('Debe ingresar la abreviacion del rubro')

        if itemconfig is not None:
            current_ic_nombre = cadenas.strip_upper(itemconfig.ic_nombre)
            current_ic_code = cadenas.strip_upper(itemconfig.ic_code)
            setfechas = False
            if current_ic_nombre != new_ic_nombre:
                itemconfig.ic_nombre = new_ic_nombre
                setfechas = True

            if current_ic_code != new_ic_code:
                if self.existe_codbar(new_ic_code):
                    raise ErrorValidacionExc('Ya existe un rubro registrado con la abreviación ingresada, ingrese otra')
                else:
                    itemconfig.ic_code = new_ic_code
                    setfechas = True

            if setfechas:
                itemconfig.ic_fechaactualiza = datetime.now()
                itemconfig.ic_useractualiza = user_edita
                self.dbsession.add(itemconfig)
        else:
            raise ErrorValidacionExc('No existe un registro con el código indicado')

    def crear_rubro(self, form, user_crea):
        titemconfig = TItemConfig()

        ic_nombre = cadenas.strip_upper(form['ic_nombre'])
        ic_code = cadenas.strip_upper(form['ic_code'])
        tipic_id = 4
        clsic_id = form['clsic_id']

        if not cadenas.es_nonulo_novacio(ic_nombre):
            raise ErrorValidacionExc('Debe ingresar el nombre del rubro')

        if not cadenas.es_nonulo_novacio(ic_code):
            raise ErrorValidacionExc('Debe ingresar la abreviacion del rubro')

        if not cadenas.es_nonulo_novacio(clsic_id):
            raise ErrorValidacionExc('Debe especificar el tipo del rubro')

        if self.existe_codbar(ic_code):
            raise ErrorValidacionExc('Ya existe un rubro registrado con la abreviación ingresada, ingrese otra')

        titemconfig.ic_nombre = ic_nombre
        titemconfig.ic_code = ic_code
        titemconfig.tipic_id = tipic_id
        titemconfig.ic_usercrea = user_crea
        titemconfig.ic_fechacrea = datetime.now()
        titemconfig.ic_estado = 1
        titemconfig.catic_id = 1
        titemconfig.clsic_id = clsic_id
        self.dbsession.add(titemconfig)

    def crear(self, form, user_crea):
        """
        Crea un nuevo articulo
        :param form:
        :param user_crea:
        :param sec_id:
        :return:
        """
        codbar_auto = form['codbar_auto']
        ic_code = cadenas.strip(str(form['ic_code']))
        tparamdao = TParamsDao(self.dbsession)
        if codbar_auto:
            ic_code = tparamdao.get_next_sequence_codbar()

        icdp_preciocompra = form['icdp_preciocompra']
        icdp_precioventa = form['icdp_precioventa']
        icdp_precioventamin = form['icdp_precioventamin']

        icdp_grabaiva = form['icdp_grabaiva']
        if icdp_grabaiva:
            # El precio de compra y de venta se le debe quitar el iva
            # icdp_preciocompra = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_preciocompra))
            icdp_precioventa = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_precioventa))
            icdp_precioventamin = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_precioventamin))

        # Verificar si el codigo del producto ya esta registrado
        if self.existe_codbar(ic_code):
            raise ErrorValidacionExc(u"El código '{0}' ya está registrado, favor ingrese otro".format(ic_code))

        ic_nombre = cadenas.strip_upper(form['ic_nombre'])
        if self.existe_artbynombre(ic_nombre):
            raise ErrorValidacionExc(
                u"Ya existe registrado un producto o servicio con el nombre: '{0}'".format(ic_nombre))

        itemconfig = TItemConfig()
        itemconfig.ic_nombre = ic_nombre
        itemconfig.ic_code = ic_code
        itemconfig.tipic_id = form['tipic_id']
        itemconfig.ic_nota = form['ic_nota']
        if type(form['catic_id']) is dict:
            itemconfig.catic_id = form['catic_id']['catic_id']
        else:
            itemconfig.catic_id = form['catic_id']

        itemconfig.ic_dental = form['ic_dental']
        itemconfig.ic_usercrea = user_crea
        itemconfig.ic_fechacrea = datetime.now()

        self.dbsession.add(itemconfig)
        self.dbsession.flush()

        ic_id = itemconfig.ic_id

        titemconfigdp = TItemConfigDatosProd()
        titemconfigdp.ic_id = ic_id
        titemconfigdp.icdp_grabaiva = icdp_grabaiva

        icdp_fechacaducidad = form['icdp_fechacaducidad']
        if cadenas.es_nonulo_novacio(icdp_fechacaducidad):
            titemconfigdp.icdp_fechacaducidad = fechas.parse_cadena(icdp_fechacaducidad)
        else:
            titemconfigdp.icdp_fechacaducidad = None

        titemconfigdp.icdp_proveedor = form['icdp_proveedor']
        # titemconfigdp.icdp_modcontab = form['icdp_modcontab']
        titemconfigdp.icdp_modcontab = None

        titemconfigdp.icdp_preciocompra = icdp_preciocompra
        titemconfigdp.icdp_precioventa = icdp_precioventa
        titemconfigdp.icdp_precioventamin = icdp_precioventamin

        self.dbsession.add(titemconfigdp)

        if codbar_auto:
            tparamdao.update_sequence_codbar()

        return ic_id

    def actualizar(self, form, user_actualiza):
        # Datos para actualizar:

        ic_id = form['ic_id']
        titemconfig = self.dbsession.query(TItemConfig).filter(TItemConfig.ic_id == ic_id).first()
        if titemconfig is not None:
            # Cosas que se pueden actualizar:
            # Nombre, categoria, proveedro, precio de compra, precio de venta, fecha de caducidad, observacion
            icdp_preciocompra = form['icdp_preciocompra']
            icdp_precioventa = form['icdp_precioventa']
            icdp_precioventamin = form['icdp_precioventamin']

            icdp_grabaiva = form['icdp_grabaiva']
            if icdp_grabaiva:
                # El precio de compra y de venta se le debe quitar el iva
                # icdp_preciocompra = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_preciocompra))
                icdp_precioventa = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_precioventa))
                icdp_precioventamin = ivautil.redondear_precio_db(ivautil.quitar_iva(icdp_precioventamin))

            old_ic_nombre = cadenas.strip(titemconfig.ic_nombre)
            ic_nombre = cadenas.strip_upper(form['ic_nombre'])
            if ic_nombre != old_ic_nombre:
                if self.existe_artbynombre(ic_nombre):
                    raise ErrorValidacionExc(
                        u"Ya existe registrado un producto o servicio con el nombre: '{0}'".format(ic_nombre))

            titemconfig.ic_nombre = ic_nombre
            titemconfig.ic_nota = form['ic_nota']
            if type(form['catic_id']) is dict:
                titemconfig.catic_id = form['catic_id']['catic_id']
            else:
                titemconfig.catic_id = form['catic_id']

            titemconfig.ic_useractualiza = user_actualiza
            titemconfig.ic_fechaactualiza = datetime.now()

            self.dbsession.add(titemconfig)

            titemconfigdp = self.dbsession.query(TItemConfigDatosProd).filter(
                TItemConfigDatosProd.ic_id == ic_id).first()
            if titemconfigdp is not None:
                titemconfigdp.icdp_proveedor = form['icdp_proveedor']

                icdp_fechacaducidad = form['icdp_fechacaducidad']
                if cadenas.es_nonulo_novacio(icdp_fechacaducidad):
                    titemconfigdp.icdp_fechacaducidad = fechas.parse_cadena(icdp_fechacaducidad)
                else:
                    titemconfigdp.icdp_fechacaducidad = None

                titemconfigdp.icdp_grabaiva = icdp_grabaiva
                titemconfigdp.icdp_preciocompra = icdp_preciocompra
                titemconfigdp.icdp_precioventa = icdp_precioventa
                titemconfigdp.icdp_precioventamin = icdp_precioventamin
                # TODO: Agregar logica para registrar kardek del articulo
                self.dbsession.add(titemconfigdp)

            self.dbsession.flush()
            return ic_id

    def get_detalles_prod(self, ic_id):

        sql = """
        select a.ic_id, a.ic_nombre, a.ic_code, a.tipic_id,
               a.ic_fechacrea, a.ic_nota, a.catic_id,
               t.catic_nombre,
               td.icdp_fechacaducidad,
               td.icdp_grabaiva,               
               td.icdp_preciocompra,
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_preciocompra),2) else td.icdp_preciocompra end as icdp_preciocompra_iva,
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventa),2) else td.icdp_precioventa end as icdp_precioventa,
               case td.icdp_grabaiva when TRUE then round(poner_iva(td.icdp_precioventamin),2) else td.icdp_precioventamin end as icdp_precioventamin,
               tipo.tipic_nombre,
               td.icdp_proveedor,
               coalesce(per.per_nombres,'') as proveedor
        from titemconfig a join tcatitemconfig t on a.catic_id = t.catic_id
        join titemconfig_datosprod td on a.ic_id = td.ic_id
        join ttipoitemconfig tipo on a.tipic_id = tipo.tipic_id
        left join tpersona per on td.icdp_proveedor = per.per_id
        where a.ic_id = {0}
        """.format(ic_id)

        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code', 'tipic_id', 'ic_fechacrea', 'ic_nota', 'catic_id',
                      'catic_nombre', 'icdp_fechacaducidad', 'icdp_grabaiva', 'icdp_preciocompra',
                      'icdp_preciocompra_iva', 'icdp_precioventa', 'icdp_precioventamin',
                      'tipic_nombre', 'icdp_proveedor', 'proveedor')

        return self.first(sql, tupla_desc)

    def anular(self, ic_id, useranula):
        titemconfig = self.dbsession.query(TItemConfig).filter(TItemConfig.ic_id == ic_id).first()
        ts = datetime.now().isoformat()
        if titemconfig is not None:
            titemconfig.ic_code = titemconfig.ic_code + '_deleted_ts_' + ts
            titemconfig.ic_estado = 2
            titemconfig.ic_useractualiza = useranula
            titemconfig.ic_fechaactualiza = datetime.now()
            self.dbsession.add(titemconfig)

    def update_barcode(self, ic_id, newbarcode):
        titemconfig = self.dbsession.query(TItemConfig).filter(TItemConfig.ic_id == ic_id).first()
        newbarcode_strip = cadenas.strip(str(newbarcode))
        if titemconfig is not None:
            current_ic_code = titemconfig.ic_code
            if newbarcode_strip != current_ic_code:
                if self.existe_codbar(newbarcode_strip):
                    raise ErrorValidacionExc(
                        u'No se puede cambiar el código de barra, el código {0} ya esta siendo usado por otro producto o servicio'.format(
                            newbarcode))
                else:
                    titemconfig.ic_code = newbarcode_strip
                    self.dbsession.add(titemconfig)
