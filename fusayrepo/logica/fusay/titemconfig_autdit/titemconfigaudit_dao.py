# coding: utf-8
"""
Fecha de creacion 4/4/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.titemconfig_autdit.titemconfigaudit_model import TItemConfigAudit
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TItemConfigAuditDao(BaseDao):

    def crear_audit_precioventa(self, ic_id, user_crea, sec_id, val_antes, val_despues):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'v'
        titemconfigaudit.ica_valantes = cadenas.strip(val_antes)
        titemconfigaudit.ica_valdespues = cadenas.strip(val_despues)
        titemconfigaudit.ica_ref = 0
        titemconfigaudit.ica_obs = 'Actualización directa de precio de venta'

        self.dbsession.add(titemconfigaudit)

    def crear_audit_precioventamin(self, ic_id, user_crea, sec_id, val_antes, val_despues):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'm'
        titemconfigaudit.ica_valantes = cadenas.strip(val_antes)
        titemconfigaudit.ica_valdespues = cadenas.strip(val_despues)
        titemconfigaudit.ica_ref = 0
        titemconfigaudit.ica_obs = 'Actualización directa de precio de venta mínimo'

        self.dbsession.add(titemconfigaudit)

    def crear_audit_preciocompra(self, ic_id, user_crea, sec_id, val_antes, val_despues):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'c'
        titemconfigaudit.ica_valantes = cadenas.strip(val_antes)
        titemconfigaudit.ica_valdespues = cadenas.strip(val_despues)
        titemconfigaudit.ica_ref = 0
        titemconfigaudit.ica_obs = 'Actualización directa de precio de compra'

        self.dbsession.add(titemconfigaudit)

    def crear_audit_alta(self, ic_id, user_crea, sec_id):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 'n'
        titemconfigaudit.ica_valantes = ''
        titemconfigaudit.ica_valdespues = ''
        titemconfigaudit.ica_ref = 0
        titemconfigaudit.ica_obs = 'Registro de producto/servicio'

        self.dbsession.add(titemconfigaudit)

    def crear_audit_stock(self, ic_id, user_crea, sec_id, val_antes, val_despues, obs='Actualización directa de stock'):
        titemconfigaudit = TItemConfigAudit()
        titemconfigaudit.user_crea = user_crea
        titemconfigaudit.fecha_crea = datetime.now()
        titemconfigaudit.sec_id = sec_id
        titemconfigaudit.ic_id = ic_id
        titemconfigaudit.ica_tipo = 's'
        titemconfigaudit.ica_valantes = cadenas.strip(val_antes)
        titemconfigaudit.ica_valdespues = cadenas.strip(val_despues)
        titemconfigaudit.ica_ref = 0
        titemconfigaudit.ica_obs = obs

        self.dbsession.add(titemconfigaudit)

    def listar_eventos(self, ic_id):
        sql = """
        select
       a.ica_id,
       a.ic_id,
       a.fecha_crea,
       case
           when a.ica_tipo = 'n' then 'Creación'
           when a.ica_tipo = 'v' then 'Precio Venta'
           when a.ica_tipo = 'c' then 'Precio Compra'
           when a.ica_tipo = 's' then 'Stock'
        else 'Desconocido' end evento,
           a.ica_valantes,
           a.ica_valdespues,
           coalesce(per.per_ciruc,'') ciruc,
           coalesce(per.per_nombres,'')||' '||coalesce(per.per_apellidos,'') referente,
           coalesce(tra.tra_nombre,'') transacc,
           coalesce(a.ica_obs,'') ica_obs
        from titemconfig_audit a
        left join tpersona per on per.per_id = a.ica_ref
        left join ttransacc tra on tra.tra_codigo = a.ica_tracod
        where a.ic_id = {0} order by a.fecha_crea desc
        """.format(ic_id)

        tupla_desc = ('ica_id', 'ic_id', 'fecha_crea', 'evento', 'ica_valantes', 'ica_valdespues', 'ciruc',
                      'referente', 'transacc', 'ica_obs')
        return self.all(sql, tupla_desc)
