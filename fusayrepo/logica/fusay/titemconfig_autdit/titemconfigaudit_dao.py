# coding: utf-8
"""
Fecha de creacion 4/4/20
@autor: mjapon
"""
import logging
from datetime import datetime

from psycopg2._psycopg import Decimal

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.titemconfig_autdit.titemconfigaudit_model import TItemConfigAudit

log = logging.getLogger(__name__)


class TItemConfigAuditDao(BaseDao):

    def crear_audit_precio(self, ic_id, user_crea, sec_id, val_antes, val_despues):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'P'
        titemconfigaudit.ica_valantes = Decimal(val_antes)
        titemconfigaudit.ica_valdespues = Decimal(val_despues)

        self.dbsession.add(titemconfigaudit)

    def crear_audit_stock(self, ic_id, user_crea, sec_id, val_antes, val_despues):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'S'
        titemconfigaudit.ica_valantes = Decimal(val_antes)
        titemconfigaudit.ica_valdespues = Decimal(val_despues)

        self.dbsession.add(titemconfigaudit)

    def listar_eventos(self, ic_id):
        sql = """
        select
       a.ica_id,
       a.ic_id,
       a.fecha_crea,
       case
           when a.ica_tipo = 'c' then 'Creación'
           when a.ica_tipo = 'p' then 'Cambio de precio'
           when a.ica_tipo = 's' then 'Cambio de stock'
        else 'Desconocido' end evento,
           a.ica_valantes,
           a.ica_valdespues,
           coalesce(per.per_ciruc,'') ciruc,
           coalesce(per.per_nombres,'')||' '||coalesce(per.per_apellidos,'') referente,
           coalesce(tra.tra_nombre,'') transacc
        from titemconfig_audit a
        left join tpersona per on per.per_id = a.ica_ref
        left join ttransacc tra on tra.tra_codigo = a.ica_tracod
        where a.ic_id = {0} order by a.fecha_crea desc
        """.format(ic_id)

        tupla_desc = ('ica_id',
                      'ic_id',
                      'fecha_crea', 'evento', 'ica_valantes', 'ica_valdespues', 'ciruc', 'referente', 'transacc')
        return self.all(sql, tupla_desc)
