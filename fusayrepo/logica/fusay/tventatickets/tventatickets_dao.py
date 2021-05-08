# coding: utf-8
"""
Fecha de creacion 9/14/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tgrid.tgrid_dao import TGridDao
from fusayrepo.logica.fusay.tventatickets.tventatickets_model import TVentaTickets
from fusayrepo.utils import cadenas, fechas

log = logging.getLogger(__name__)


class TVentaTicketsDao(BaseDao):

    @staticmethod
    def get_form():
        return {
            'vt_id': 0,
            'vt_monto': 0.0,
            'vt_tipo': 0,
            'vt_estado': 0,
            'vt_obs': '',
            'vt_clase': 1,
            'vt_fecha': fechas.get_str_fecha_actual(),
            'vt_codadj': 0
        }

    def get_detalles(self, vtkid):
        sql = """
        select vt.vt_id, 
        vt.vt_fechareg, 
        vt.vt_monto, 
        vt.vt_tipo, 
        ic.ic_nombre, 
        vt.vt_estado,
        case when vt_estado = 0 then 'Pendiente'
             when vt_estado = 1  then 'Confirmado'
             when vt_estado = 2  then 'Anulado' else 'desc' end as estadodesc,
        vt.vt_obs, 
        vt.vt_fecha,
        coalesce(vu.referente, '') as refusercrea,
        coalesce(vu.us_cuenta, '') as usercreacuenta,
        coalesce(vt.vt_codadj,0) as rxd_id,
        coalesce(adj.rxd_filename,'') as rxd_filename,
        coalesce(adj.rxd_ext,'') as rxd_ext
        from tventatickets vt
        join titemconfig ic on vt.vt_tipo = ic.ic_id
        left join vusers vu on vu.us_id = vt.vt_usercrea
        left join todrxdocs adj on adj.rxd_id = vt.vt_codadj 
          where vt.vt_estado in (0,1) and vt.vt_id = {0}        
        """.format(vtkid)

        print(sql)

        tupla_desc = ('vt_id', 'vt_fechareg', 'vt_monto', 'vt_tipo', 'ic_nombre', 'vt_estado', 'estadodesc', 'vt_obs',
                      'vt_fecha', 'refusercrea', 'usercreacuenta', 'rxd_id', 'rxd_filename', 'rxd_ext')

        res = self.first(sql, tupla_desc)
        return res

    def get_cuentas(self, tipo):
        sql = """
        select ic_id, ic_nombre from titemconfig
        where tipic_id = 4 and clsic_id = {tipo} order by ic_nombre asc;
        """.format(tipo=tipo)
        tupla_desc = ('ic_id', 'ic_nombre')
        return self.all(sql, tupla_desc)

    def get_entity_byid(self, vt_id):
        return self.dbsession.query(TVentaTickets).filter(TVentaTickets.vt_id == vt_id).first()

    @staticmethod
    def get_tipos_cuentas():
        return [{
            'value': 1, 'label': 'Ingreso',
        },
            {
                'value': 2, 'label': 'Gasto',
            },
            {
                'value': 3, 'label': 'Patrimonio',
            }
        ]

    @staticmethod
    def agregar_todos_inlist(thelist):
        cuentares = [{'ic_id': 0, 'ic_nombre': 'Todos'}]
        for item in thelist:
            cuentares.append(item)

        return cuentares

    def crear(self, formtosave, usercrea):

        if 'form' in formtosave:
            form = formtosave['form']

        tventa_ticket = TVentaTickets()
        monto = form['vt_monto']
        tipo = form['vt_tipo']
        estado = 0
        obs = form['vt_obs']
        clase = form['vt_clase']
        fecha = form['vt_fecha']
        fecha_parsed = fechas.parse_cadena(fecha)

        tventa_ticket.vt_fechareg = datetime.now()
        tventa_ticket.vt_monto = monto
        tventa_ticket.vt_tipo = tipo
        tventa_ticket.vt_estado = estado
        tventa_ticket.vt_obs = cadenas.strip(obs)
        tventa_ticket.vt_clase = clase
        tventa_ticket.vt_fecha = fecha_parsed
        tventa_ticket.vt_usercrea = usercrea

        """
        if fileinfo is not None:
            todrxdocsdao = TOdRxDocsDao(self.dbsession)
            thefile = fileinfo['archivo']
            formfile = {
                'rxd_filename': fileinfo['rxd_filename'],
                'pac_id': -3,
                'rxd_tipo': 3,
                'rxd_nota': '',
                'rxd_nropieza': 0,
                'rxd_nombre': fileinfo['rxd_filename']
            }
            rxid = todrxdocsdao.crear(formfile, usercrea, thefile)
            tventa_ticket.vt_codadj = rxid
        """

        self.dbsession.add(tventa_ticket)

    def cambiar_estado(self, vt_id, estado, userupd):
        tventaticket = self.get_entity_byid(vt_id)
        if tventaticket is not None:
            tventaticket.vt_estado = estado
            tventaticket.vt_useranula = userupd
            tventaticket.vt_fechanul = datetime.now()
            self.dbsession.add(tventaticket)

    def anular(self, vt_id, useranula):
        self.cambiar_estado(vt_id, estado=2, userupd=useranula)

    def confirmar(self, vt_id, userconfirma):
        self.cambiar_estado(vt_id, estado=1, userupd=userconfirma)

    def listar(self, tipo, cuenta):
        tgrid_dao = TGridDao(self.dbsession)
        if cuenta is None or int(cuenta) == 0:
            andwhere = " and ic.clsic_id = {0}".format(tipo)
        else:
            andwhere = " and ic.clsic_id = {0} and vt_tipo={1} ".format(tipo, cuenta)

        data = tgrid_dao.run_grid(grid_nombre='ventatickets', andwhere=andwhere)

        return data
