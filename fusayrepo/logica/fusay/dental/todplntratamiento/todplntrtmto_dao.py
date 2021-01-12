# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todplntratamiento.todplntrtmto_model import TOdPlnTrtmto
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TOdPlanTratamientoDao(BaseDao):

    def get_form(self, pac_id):
        form = {
            'pnt_id': 0,
            'pnt_nombre': '',
            'med_id': 0,
            'pac_id': pac_id,
            'trn_codigo': 0,
            'pnt_obs': ''
        }
        return form

    def crear(self, form, user_crea):
        formplan = form['formplan']
        formcab = form['form_cab']
        form_persona = form['form_persona']
        detalles = form['detalles']
        pagos = form['pagos']

        tplantratamiento = TOdPlnTrtmto()
        tplantratamiento.pnt_nombre = cadenas.strip_upper(formplan['pnt_nombre'])
        tplantratamiento.pnt_fechacrea = datetime.datetime.now()
        tplantratamiento.user_crea = user_crea
        tplantratamiento.pnt_obs = cadenas.strip(formplan['pnt_obs'])
        tplantratamiento.med_id = formplan['med_id']
        tplantratamiento.pac_id = formplan['pac_id']
        tplantratamiento.pnt_estado = 1

        # Registro de factura
        tsientodao = TasientoDao(self.dbsession)
        trn_codigo = tsientodao.crear(form=formcab, form_persona=form_persona, user_crea=user_crea, detalles=detalles,
                                      pagos=pagos, creaupdpac=False, totales=form['totales'])
        tplantratamiento.trn_codigo = trn_codigo

        self.dbsession.add(tplantratamiento)
        self.dbsession.flush()
        return {'trn_codigo': trn_codigo, 'pnt_codigo': tplantratamiento.pnt_id}

    def listar(self, pac_id):
        sql = """
        select pnt_id, pnt_nombre, pnt_fechacrea, pnt_estado,
        case when  pnt_estado = 1 then 'Creado'
        when  pnt_estado = 2 then 'Aprobado'
        when  pnt_estado = 3 then 'En curso'
        when  pnt_estado = 4 then 'Finalizado'
        when  pnt_estado = 5 then 'Anulado'
        else 'Desconocido' end as estadodesc,
        med_id, pac_id, trn_codigo, pnt_obs from todplntrtmto
        where pac_id = {0} and pnt_estado != 5 order by pnt_fechacrea
        """.format(pac_id)

        tupla_desc = (
            'pnt_id', 'pnt_nombre', 'pnt_fechacrea', 'pnt_estado', 'estadodesc', 'med_id', 'pac_id', 'trn_codigo',
            'pnt_obs')
        return self.all(sql, tupla_desc)

    def cambiar_estado(self, pnt_id, nuevo_estado, user_upd):
        todplantratamiento = self.dbsession.query(TOdPlnTrtmto).filter(TOdPlnTrtmto.pnt_id == pnt_id).first()
        if todplantratamiento is not None:
            todplantratamiento.user_upd = user_upd
            todplantratamiento.fecha_upd = datetime.datetime.now()
            todplantratamiento.pnt_estado = nuevo_estado

            if int(nuevo_estado) == 5:  # Se anula el plan, se debe anular tambien la factura
                tasientodao = TasientoDao(self.dbsession)
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                if tasiento is not None:
                    tasiento.trn_valido = 2
                    self.dbsession.add(tasiento)
            elif int(nuevo_estado) == 2:
                # Cuaando el estado es aprobado entonces se quita la marca de factura pendiente
                tasientodao = TasientoDao(self.dbsession)
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                if tasiento is not None:
                    tasiento.trn_docpen = 'F'
                    self.dbsession.add(tasiento)

            self.dbsession.add(todplantratamiento)

    def get_detalles(self, pnt_id):
        sql = """
        select pnt_id, pnt_nombre, pnt_fechacrea, user_crea, pnt_estado, med_id, pac_id, trn_codigo, pnt_obs,
        user_upd, fecha_upd, b.per_nombres||' '|| b.per_apellidos as medico, c.per_ciruc as pac_ciruc, 
        c.per_nombres||' '||c.per_apellidos as paciente from todplntrtmto a left join tpersona b on a.med_id = b.per_id
        left join tpersona c on a.pac_id = c.per_id where pnt_id = {0}  
        """.format(pnt_id)

        tupla_desc = ('pnt_id', 'pnt_nombre', 'pnt_fechacrea', 'user_crea', 'pnt_estado', 'med_id', 'pac_id',
                      'trn_codigo', 'pnt_obs', 'user_upd', 'fecha_upd', 'medico', 'pac_ciruc', 'paciente')
        return self.first(sql, tupla_desc)
