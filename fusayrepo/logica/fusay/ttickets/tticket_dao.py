# coding: utf-8
"""
Fecha de creacion 3/5/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.titemconfig.titemconfig_dao import TItemConfigDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.ttickets.tticket_model import TTicket
from fusayrepo.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TTicketDao(BaseDao):

    def get_entity_byid(self, tk_id):
        return self.dbsession.query(TTicket).filter(TTicket.tk_id == tk_id).first()

    def anular(self, tk_id):
        tticket = self.get_entity_byid(tk_id)
        if tticket is not None:
            tticket.tk_estado = 2
            self.dbsession.add(tticket)

    def get_detalles(self, tk_id):
        sql = """        
        select tk.tk_id, tk.tk_nro, tk.tk_fechahora, tk.tk_perid, tk.tk_observacion,
              tk.tk_usercrea, tk.tk_costo, tk.tk_dia, tk.tk_estado, tk.tk_servicios, tk.sec_id,
              sec.sec_nombre, per.per_id, per.per_ciruc,per.per_nombres, per.per_apellidos,  per.per_nombres||' '||coalesce(per.per_apellidos, '') as referente,
              coalesce(lugar.lug_nombre,'') as residencia, per.per_direccion, per.per_telf, per.per_movil,
              per.per_email, v.referente as refuser,
              case when tk.tk_estado = 1 then 'Valido' else 'Anulado' end as estado,
              tk.tk_observacion
              from ttickets tk
        join tpersona per on tk.tk_perid = per.per_id
        left join vusers v on v.us_id = tk.tk_usercrea
        left join tseccion sec on tk.sec_id = sec.sec_id
        left join public.tlugar lugar on per.per_lugresidencia = lugar.lug_id
        where tk.tk_id = {0}
        """.format(tk_id)

        tupla_desc = ('tk_id', 'tk_nro', 'tk_fechahora', 'tk_perid', 'tk_observacion', 'tk_usercrea', 'tk_costo',
                      'tk_dia', 'tk_estado', 'tk_servicios', 'sec_id', 'sec_nombre', 'per_id', 'per_ciruc',
                      'per_nombres',
                      'per_apellidos', 'referente', 'residencia', 'per_direccion', 'per_telf', 'per_movil', 'per_email',
                      'refuser', 'estado', 'tk_observacion')

        datosticket = self.first(sql, tupla_desc)

        servicios = []
        if datosticket is not None and cadenas.es_nonulo_novacio(datosticket['tk_servicios']):
            sqldet = "select b.ic_id, b.ic_nombre from titemconfig b where b.ic_id in ({0})".format(
                datosticket['tk_servicios'])
            tupla_desc = ('ic_id', 'ic_nombre')
            servicios = self.all(sqldet, tupla_desc)

        if datosticket is not None:
            return {'datosticket': datosticket, 'servicios': servicios}
        else:
            raise ErrorValidacionExc('No se pudo recuperar datos del ticket')

    def listar(self, dia, sec_id, desde, hasta, servicios):
        tgrid_dao = TGridDao(self.dbsession)
        diadb = fechas.format_cadena_db(dia)

        sqlserv = ''
        if cadenas.es_nonulo_novacio(servicios):
            servlist = servicios.split(',')
            likeservlist = []
            for serv in servlist:
                likeservlist.append('a.tk_servicios like \'%{0}%\''.format(serv))
            sqlserv = ' or '.join(likeservlist)

        sqlfechas = ''
        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sqlfechas = " and date(a.tk_dia) between '{desde}' and '{hasta}' ".format(
                desde=fechas.format_cadena_db(desde),
                hasta=fechas.format_cadena_db(hasta))
        elif cadenas.es_nonulo_novacio(desde) and not cadenas.es_nonulo_novacio(hasta):
            sqlfechas = " and date(a.tk_dia) >= '{desde}' ".format(
                desde=fechas.format_cadena_db(desde))
        elif not cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            sqlfechas = " and date(a.tk_dia) <= '{hasta}' ".format(
                hasta=fechas.format_cadena_db(hasta))
        else:
            sqlfechas = " and date(a.tk_dia) = '{0}' ".format(diadb)

        if len(sqlserv) > 0:
            sqlserv = ' and ({0})'.format(sqlserv)

        sqlsec = ''
        if int(sec_id) > 0:
            sqlsec = ' and a.sec_id = {0} '.format(sec_id)

        data = tgrid_dao.run_grid(grid_nombre='tickets', sqlfechas=sqlfechas, sqlsec=sqlsec, sqlserv=sqlserv)
        return data

    def get_next_ticket(self, dia, sec_id):

        sql = """
        select coalesce(max(tk_nro),0) as maxticket 
        from ttickets a where a.tk_estado=1 and a.tk_dia = '{0}' and a.sec_id={1} """.format(dia, sec_id)

        maxticket = self.first_col(sql, 'maxticket')
        return maxticket + 1

    def get_form(self, dia, sec_id):
        tk_nro = self.get_next_ticket(fechas.format_cadena_db(dia), sec_id)

        dia_str = fechas.get_fecha_letras_largo(fechas.parse_cadena(dia))

        return {
            'tk_id': 0,
            'per_id': 0,
            'tk_nro': tk_nro,
            'tk_obs': '',
            'tk_costo': 1.0,
            'tk_dia': dia,
            'tk_servicios': '',
            'dia_str': dia_str
        }

    def get_form_edit(self, tk_id):
        dettkserv = self.get_detalles(tk_id=tk_id)

        dettk = dettkserv['datosticket']
        servicios = dettkserv['servicios']
        setprods = set()
        if servicios is not None:
            for item in servicios:
                setprods.add(item['ic_id'])

        form = {
            'tk_id': dettk['tk_id'],
            'tk_costo': dettk['tk_costo'],
            'tk_nro': dettk['tk_nro'],
            'tk_obs': dettk['tk_observacion'],
            'per_id': dettk['per_id'],
            'per_nombres': dettk['per_nombres'],
            'per_apellidos': dettk['per_apellidos']
        }

        itemconfigdao = TItemConfigDao(self.dbsession)
        prods = itemconfigdao.get_prods_for_tickets()
        for prod in prods:
            ic_marca = False
            if prod['ic_id'] in setprods:
                ic_marca = True
            prod['ic_marca'] = ic_marca

        return {'form': form, 'servicios': prods}

    def find_byid(self, tk_id):
        return self.dbsession.query(TTicket).filter(TTicket.tk_id == tk_id).first()

    def actualizar(self, tk_id, form):
        tticket = self.find_byid(tk_id)
        if tticket is not None:
            tticket.tk_costo = form['tk_costo']
            tticket.tk_observacion = cadenas.strip(form['tk_obs'])
            tticket.tk_servicios = form['tk_servicios']
            self.dbsession.add(tticket)

    def crear(self, form, form_persona, user_crea, sec_id):

        tticket = TTicket()

        persona_dao = TPersonaDao(self.dbsession)

        tticket.tk_nro = form['tk_nro']
        tticket.tk_fechahora = datetime.now()

        per_id = form_persona['per_id']
        if per_id is None or per_id == 0:
            per_id = persona_dao.crear(form_persona, permit_ciruc_null=True)
        else:
            persona_dao.actualizar(per_id, form_persona)

        tticket.tk_perid = per_id
        tticket.tk_observacion = form['tk_obs']
        tticket.tk_usercrea = user_crea
        tticket.tk_costo = form['tk_costo']
        tticket.tk_dia = fechas.parse_cadena(form['tk_dia'])
        tticket.tk_estado = 1
        tticket.tk_servicios = form['tk_servicios']
        tticket.sec_id = sec_id

        self.dbsession.add(tticket)

        self.dbsession.flush()
        return tticket.tk_id
