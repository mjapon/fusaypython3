# coding: utf-8
"""
Fecha de creacion 4/29/21
@autor: mjapon
"""
import logging

from fusayrepo.logica.aguap.tagp_models import TAgpContrato
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao

log = logging.getLogger(__name__)


class TAgpContratoDao(BaseDao):

    def listar_tarifas(self):
        sql = """
        select ic.ic_id, ic.ic_nombre, ic.ic_code, trf.trf_id
        from tagp_tarifa trf join titemconfig ic on trf.ic_id = ic.ic_id
        order by ic.ic_nombre
        """

        tupla_desc = ('ic_id', 'ic_nombre', 'ic_code', 'trf_id')
        return self.all(sql, tupla_desc)

    def get_form_anterior(self):
        refdao = TPersonaDao(self.dbsession)
        form_per = refdao.get_form()
        form_contra = {
            'cna_id': 0,
            'per_id': 0,
            'cna_fechaini': '',
            'cna_fechafin': '',
            'cna_estado': 1,
            'cna_estadoserv': 1,
            'cna_nmingas': 0,
            'cna_barrio': '',
            'cna_sector': '',
            'cna_direccion': '',
            'cna_referencia': '',
            'cna_adjunto': 0,
            'trn_codigo': 0,
            'cna_teredad': False
        }

        tarifas = self.listar_tarifas()
        return {
            'form': form_contra,
            'formper': form_per,
            'tarifas': tarifas
        }

    def get_form(self, tipo):
        pass

    def crear(self, form, formper):
        persondao = TPersonaDao(self.dbsession)
        persondao.crear(form=formper, permit_ciruc_null=False)
        tagpContrato = TAgpContrato(self.dbsession)
