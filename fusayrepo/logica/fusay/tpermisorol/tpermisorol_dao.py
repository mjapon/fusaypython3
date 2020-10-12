# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, TIMESTAMP, String, Text

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TPermisoRolDao(BaseDao):

    def get_permisos(self, id_rol):
        sql = """
        select a.prm_id, b.prm_nombre, b.prm_abreviacion, b.prm_detalle
                from tpermisorol a join tpermiso b on a.prm_id = b. prm_id and a.rl_id = {id_rol}
        """.format(id_rol=id_rol)

        tupla_desc = ('prm_id', 'prm_nombre', 'prm_abreviacion', 'prm_detalle')
        return self.all(sql, tupla_desc)
