# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasicredito.tasicredito_model import TAsicredProvs, TAsicredProvsDetails


class TAsicreditoProvsDao(BaseDao):
    """
    Data Access Object para la tabla tasicred_provs
    Proporciona métodos para interactuar con los datos de proveedores relacionados con créditos
    """
    def create(self, crpr_sales_from, crpr_sales_to, crpr_user_create, cre_codigo, details):
        """
        Crea un nuevo registro en tasicred_provs
        :param crpr_sales_from: Fecha de inicio de ventas
        :param crpr_sales_to: Fecha de fin de ventas
        :param crpr_user_create: Usuario que crea el registro
        :param cre_codigo: Código del crédito asociado
        :param details: Lista de códigos de detalles asociados
        :return: El nuevo registro creado
        """
        from datetime import datetime

        new_record = TAsicredProvs()
        new_record.crpr_codigo = None  # Se asignará automáticamente por autoincremento
        new_record.crpr_sales_from = crpr_sales_from
        new_record.crpr_sales_to = crpr_sales_to
        new_record.crpr_creation_date = datetime.now()
        new_record.crpr_user_create = crpr_user_create
        new_record.crpr_status = 1  # Activo por defecto
        new_record.cre_codigo = cre_codigo

        self.dbsession.add(new_record)
        self.flush()  # Asegura que el nuevo registro se guarde en la base de datos y se asigne el crpr_codigo
        for dt_codigo in details:
            new_detail_record = TAsicredProvsDetails()
            new_detail_record.crpd_codigo = None  # Se asignará automáticamente por autoincremento
            new_detail_record.crpr_codigo = new_record.crpr_codigo
            new_detail_record.dt_codigo = dt_codigo
            new_detail_record.crp_creation_date = datetime.now()
            new_detail_record.crp_user_create = crpr_user_create
            new_detail_record.crp_status = 1  # Activo por defecto
            self.dbsession.add(new_detail_record)

        return new_record.crpr_codigo

    def invalidate(self, crpr_codigo, crpr_user_update):
        """
        Invalida un registro de tasicred_provs estableciendo su estado a inactivo
        :param crpr_codigo: Código del registro a invalidar
        :param crpr_user_update: Usuario que realiza la actualización
        :return: El número de registros afectados (debería ser 1 si se encuentra el registro)
        """
        from datetime import datetime

        self.dbsession.query(TAsicredProvs).filter(TAsicredProvs.crpr_codigo == crpr_codigo).update({
            TAsicredProvs.crpr_status: 0,
            TAsicredProvs.crpr_update_date: datetime.now(),
            TAsicredProvs.crpr_user_update: crpr_user_update
        })
