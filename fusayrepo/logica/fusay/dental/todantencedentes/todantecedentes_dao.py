# coding: utf-8
"""
Fecha de creacion 12/8/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todantencedentes.todantecedentes_model import TOdAntecedentes
from fusayrepo.logica.fusay.tconsultamedica.tconsultamedica_dao import TConsultaMedicaDao
from fusayrepo.logica.fusay.tconsultamedica.tconsultamedica_model import TConsultaMedicaValores

log = logging.getLogger(__name__)


class TOdAntecedentesDao(BaseDao):

    def get_form(self, od_tipo, pac_id):
        """

        :param od_tipo: 5:antecedentes odontologicos, 6:examen fisico
        :param pac_id:
        :return:
        """
        cabecera = {
            'od_antid': 0,
            'od_tipo': od_tipo,
            'pac_id': pac_id,
            'od_hallazgoexamfis': ''
        }

        cat = self.get_codcat_from_tipo(int(od_tipo))
        tconsmedicadao = TConsultaMedicaDao(self.dbsession)
        detelles = tconsmedicadao.get_form_valores(catc_id=cat)

        return {
            'cabecera': cabecera,
            'detalles': detelles
        }

    def get_codcat_from_tipo(self, od_tipo):
        cat = None
        if od_tipo == 1:
            cat = 5
        elif od_tipo == 2:
            cat = 3

        return cat

    def guardar(self, form, user_crea):
        cabecera = form['cabecera']
        detalles = form['detalles']

        todantecedntes = TOdAntecedentes()
        todantecedntes.pac_id = cabecera['pac_id']
        todantecedntes.od_tipo = cabecera['od_tipo']
        todantecedntes.od_antestado = 1
        todantecedntes.od_antfechacrea = datetime.datetime.now()
        todantecedntes.od_antusercrea = user_crea
        todantecedntes.od_hallazgoexamfis = cabecera['od_hallazgoexamfis']

        self.dbsession.add(todantecedntes)
        self.dbsession.flush()

        od_antid = todantecedntes.od_antid

        for item in detalles:
            codcat = item['cmtv_cat']
            valorpropiedad = item['valorreg']
            codtipo = item['cmtv_id']
            tconsultmvalores = TConsultaMedicaValores()
            tconsultmvalores.cosm_id = -1
            tconsultmvalores.valcm_tipo = codtipo
            tconsultmvalores.valcm_valor = valorpropiedad
            tconsultmvalores.valcm_categ = codcat
            tconsultmvalores.od_antid = od_antid
            self.dbsession.add(tconsultmvalores)

    def get_valid_last(self, pac_id, od_tipo):
        sql = """
        select o.od_antid, o.od_antfechacrea, o.od_antusercrea, o.od_tipo, o.pac_id, o.od_hallazgoexamfis, f.us_cuenta from todantecedentes o
        join tfuser f on  o.od_antusercrea = f.us_id where o.pac_id = {0} and o.od_antestado = 1 and o.od_tipo = {1} 
        order by o.od_antfechacrea desc limit 1  
        """.format(pac_id, od_tipo)

        tupla_desc = (
            'od_antid', 'od_antfechacrea', 'od_antusercrea', 'od_tipo', 'pac_id', 'od_hallazgoexamfis', 'us_cuenta')

        cabecera = self.first(sql, tupla_desc)
        if cabecera is not None:
            od_antid = cabecera['od_antid']
            cat = self.get_codcat_from_tipo(cabecera['od_tipo'])
            tconsultamedica_dao = TConsultaMedicaDao(self.dbsession)
            detalles = tconsultamedica_dao.get_valores_adc_odonto(catc_id=cat, od_antid=od_antid)
            return {
                'cabecera': cabecera,
                'detalles': detalles
            }
        return None

    def get_registros_antiguos(self, pac_id, od_tipo):
        sql = """
                select o.od_antid, o.od_antfechacrea, o.od_antusercrea, o.od_tipo, o.pac_id, f.us_cuenta from todantecedentes o
                join tfuser f on  o.od_antusercrea = f.us_id where o.pac_id = {0} and o.od_tipo = {1} and o.od_antestado = 1 
                order by o.od_antfechacrea desc  
                """.format(pac_id, od_tipo)

        tupla_desc = ('od_antid', 'od_antfechacrea', 'od_antusercrea', 'od_tipo', 'pac_id', 'us_cuenta')
        return self.all(sql, tupla_desc)

    def get_cabecera_byid(self, od_antid):
        sql = """
                    select o.od_antid, o.od_antfechacrea, o.od_antusercrea, o.od_tipo, o.pac_id, od_hallazgoexamfis from todantecedentes o
                    where o.od_antid = {0}""".format(od_antid)

        tupla_desc = ('od_antid', 'od_antfechacrea', 'od_antusercrea', 'od_tipo', 'pac_id', 'od_hallazgoexamfis')
        return self.first(sql, tupla_desc)

    def get_detalles_byantid(self, od_antid):
        cabecera = self.get_cabecera_byid(od_antid)
        if cabecera is not None:
            cat = self.get_codcat_from_tipo(cabecera['od_tipo'])
            tconsultamedica_dao = TConsultaMedicaDao(self.dbsession)
            detalles = tconsultamedica_dao.get_valores_adc_odonto(catc_id=cat, od_antid=od_antid)
        return {
            'cabecera': cabecera,
            'detalles': detalles
        }

    def find_byid(self, od_antid):
        return self.dbsession.query(TOdAntecedentes).filter(TOdAntecedentes.od_antid == od_antid).first()

    def anular(self, od_antid, user_anula):
        todantecedentes = self.find_byid(od_antid)
        if todantecedentes is not None:
            todantecedentes.od_antestado = 2
            todantecedentes.od_fechanula = datetime.datetime.now()
            todantecedentes.od_useranula = user_anula
            self.dbsession.add(todantecedentes)

    def actualizar(self, od_antid, form, user_edita):
        todantecedentes = self.find_byid(od_antid)
        if todantecedentes is not None:
            self.guardar(form, user_crea=user_edita)
            self.dbsession.delete(todantecedentes)
