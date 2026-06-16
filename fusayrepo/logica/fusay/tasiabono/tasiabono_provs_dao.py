import datetime

from sqlalchemy import and_

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tasiabono.tasiabono_model import TAsiAbonoProv, TAsiAbonoProvDetail
from fusayrepo.utils import fechas


class AbonosProveedoresDAO(BaseDao):

    def crear_abono_proveedor(self, credito_prov, abo_codigo, from_date, to_date, dt_codigos_ventas, user_create):
        """
        Crea un abono a proveedor por el monto indicado, asociado al credito_prov y a las ventas indicadas
        """
        # Crear el registro del abono a proveedor
        abop_codigo = self.crear_abono_proveedor_db(credito_prov, abo_codigo, from_date, to_date, user_create)

        # Crear los registros del detalle del abono a proveedor asociados a las ventas indicadas
        for dt_codigo_venta in dt_codigos_ventas:
            self.crear_abono_proveedor_detail_db(abop_codigo, dt_codigo_venta, user_create)

    def crear_abono_proveedor_db(self, credito_prov, abo_codigo, from_date, to_date, user_create):
        """
        Crea un registro de abono a proveedor en la base de datos y retorna el codigo del abono creado
        """
        tasiabonoprov = TAsiAbonoProv()
        tasiabonoprov.cre_codigo = credito_prov
        tasiabonoprov.abo_codigo = abo_codigo
        tasiabonoprov.abop_sales_from = fechas.parse_cadena(from_date)
        tasiabonoprov.abop_sales_to = fechas.parse_cadena(to_date)
        tasiabonoprov.abop_creation_date = datetime.datetime.now()
        tasiabonoprov.abop_user_create = user_create
        tasiabonoprov.abop_status = 1
        self.dbsession.add(tasiabonoprov)
        self.flush()
        return tasiabonoprov.abop_codigo

    def crear_abono_proveedor_detail_db(self, abop_codigo, dt_codigo_venta, user_create):
        """
        Crea un registro de detalle de abono a proveedor en la base de datos asociado al codigo de abono a proveedor indicado
        """
        tasiabonoprovdetail = TAsiAbonoProvDetail()
        tasiabonoprovdetail.abop_codigo = abop_codigo
        tasiabonoprovdetail.dt_codigo_venta = dt_codigo_venta
        tasiabonoprovdetail.abpd_creation_date = datetime.datetime.now()
        tasiabonoprovdetail.abpd_user_create = user_create
        tasiabonoprovdetail.abpd_status = 1
        self.dbsession.add(tasiabonoprovdetail)

    def anular_detalles(self, abop_codigos, user_anula):
        abop_details = (self.dbsession.query(TAsiAbonoProvDetail)
                        .filter(and_(TAsiAbonoProvDetail.abop_codigo.in_(abop_codigos),
                                     TAsiAbonoProvDetail.abpd_status == 1)).all())
        if abop_details is not None and len(abop_details) > 0:
            for detail in abop_details:
                detail.abpd_status = 0
                detail.abpd_update_date = datetime.datetime.now()
                detail.abpd_user_update = user_anula
                self.dbsession.add(detail)

    def anular_abono_proveedor(self, cre_codigo, abo_codigo, user_anula):
        abonosprovs = self.dbsession.query(TAsiAbonoProv).filter(and_(TAsiAbonoProv.cre_codigo == cre_codigo,
                                                                      TAsiAbonoProv.abo_codigo == abo_codigo,
                                                                      TAsiAbonoProv.abop_status == 1)).all()
        if abonosprovs is not None and len(abonosprovs) > 0:
            abop_codigos = []
            for abono in abonosprovs:
                abono.abop_status = 0
                abono.abop_update_date = datetime.datetime.now()
                abono.abop_user_update = user_anula
                abop_codigos.append(abono.abop_codigo)
                self.dbsession.add(abono)
            self.anular_detalles(abop_codigos, user_anula)
