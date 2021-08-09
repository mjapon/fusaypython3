# coding: utf-8
"""
Fecha de creacion 12/3/20
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.dental.todontograma.todontograma_model import TOdontograma, TOdontogramaHist
from fusayrepo.utils import cadenas, fechas, ctes

log = logging.getLogger(__name__)


class TOdontogramaDao(BaseDao):

    def get_form(self):
        return {
            'od_id': 0,
            'od_tipo': 1,
            'od_protesis': '',
            'od_odontograma': '',
            'od_obsodonto': '',
            'pac_id': 0
        }

    def crear(self, user_crea, pac_id, od_tipo, od_odontograma, od_obs, od_protesis):
        todontograma = TOdontograma()
        todontograma.od_fechacrea = datetime.datetime.now()
        todontograma.user_crea = user_crea
        todontograma.od_odontograma = od_odontograma
        todontograma.od_obsodonto = od_obs
        todontograma.od_tipo = od_tipo
        todontograma.od_protesis = od_protesis
        todontograma.pac_id = pac_id
        self.dbsession.add(todontograma)
        self.dbsession.flush()

        od_id = todontograma.od_id
        self.save_histo(od_id=od_id, user_crea=user_crea)

        return od_id

    def find_byid(self, od_id):
        return self.dbsession.query(TOdontograma).filter(TOdontograma.od_id == od_id).first()

    def find_histo_byid(self, odh_id):
        return self.dbsession.query(TOdontogramaHist).filter(TOdontogramaHist.odh_id == odh_id).first()

    def actualizar(self, od_id, user_upd, od_odontograma, od_obs, od_protesis):
        todontograma = self.find_byid(od_id)
        if todontograma is not None:
            todontograma.user_upd = user_upd
            todontograma.od_fechaupd = datetime.datetime.now()
            todontograma.od_protesis = od_protesis
            todontograma.od_odontograma = od_odontograma
            todontograma.od_obsodonto = od_obs
            self.dbsession.add(todontograma)
            self.save_histo(od_id=od_id, user_crea=user_upd)

    def get_odontograma_by_id(self, od_id):
        sql = """select od_id, od_fechacrea, od_fechaupd, user_crea, od_odontograma, 
                od_obsodonto, od_tipo, od_protesis, pac_id from todontograma where od_id = {0}""".format(od_id)
        tupla_desc = ('od_id', 'od_fechacrea', 'od_fechaupd', 'user_crea', 'od_odontograma',
                      'od_obsodonto', 'od_tipo', 'od_protesis', 'pac_id')
        return self.first(sql, tupla_desc)

    def get_odontograma(self, pac_id, tipo):
        sql = """select od_id, od_fechacrea, od_fechaupd, user_crea, od_odontograma, 
                od_obsodonto, od_tipo, od_protesis, pac_id from todontograma where pac_id = {0} and od_tipo = {1}""".format(
            pac_id, tipo)
        tupla_desc = ('od_id', 'od_fechacrea', 'od_fechaupd', 'user_crea', 'od_odontograma',
                      'od_obsodonto', 'od_tipo', 'od_protesis', 'pac_id')
        return self.first(sql, tupla_desc)

    def get_last_odontograma(self, pac_id):
        sql = "select od_odontograma, od_tipo from todontograma where pac_id={0} and od_tipo in (1,2) order by od_id desc limit 2".format(
            pac_id)
        res = self.all(sql, ('od_odontograma', 'od_tipo'))
        resdict = {}
        for item in res:
            resdict[item['od_tipo']] = item['od_odontograma']

        return resdict

    def get_dientes_json_css(self):
        sql = """
                select odc_numpieza, odc_corona, odc_ds, odc_ds, odc_cara, odc_raiz, odc_perno, odc_reten, odc_dnt, odc_dntc 
                from todcss
                """

        tupla_desc = (
            'odc_numpieza', 'odc_corona', 'odc_ds', 'odc_ds', 'odc_cara', 'odc_raiz', 'odc_perno', 'odc_reten',
            'odc_dnt', 'odc_dntc')

        items = self.all(sql, tupla_desc)
        allitems_dict = {}
        for item in items:
            newcss = {}
            # print('Iter item numpieza {0}'.format(item['odc_numpieza']))
            for key in item:
                if key != 'odc_numpieza' and cadenas.es_nonulo_novacio(item[key]):
                    newcss[key] = self.obj(item[key])
            allitems_dict[item['odc_numpieza']] = newcss

        return allitems_dict

    def get_css(self, npieza):
        sql = """
        select odc_corona, odc_ds, odc_ds, odc_cara, odc_raiz, odc_perno, odc_reten, odc_dnt, odc_dntc 
        from todcss where odc_numpieza = {0}
        """.format(npieza)

        tupla_desc = (
            'odc_corona', 'odc_ds', 'odc_ds', 'odc_cara', 'odc_raiz', 'odc_perno', 'odc_reten',
            'odc_dnt', 'odc_dntc')

        css = self.first(sql, tupla_desc)
        newcss = {}
        if css is not None:
            for key in css:
                if cadenas.es_nonulo_novacio(css[key]):
                    newcss[key] = self.obj(css[key])

        return newcss

    def find_histo(self, pac_id, fecha):
        sql = """
        select odh_id from todontograma_hist where pac_id = {0} and odh_fecha = '{1}'
        """.format(pac_id, fecha)

        odh_id = self.first_col(sql, 'odh_id')
        if odh_id is not None:
            return self.find_histo_byid(odh_id=odh_id)
        return None

    def list_histo(self, pac_id):
        today = fechas.get_str_fecha_actual(ctes.APP_FMT_FECHA_DB)
        sql = """
        select odh_id, odh_fechacrea, odh_fecha, pac_id, odh_tipo, 
        case when odh_tipo = 1 then 'Permanente' else 'Temporal' end as tipodesc 
        from todontograma_hist where pac_id = {0} 
        and odh_fecha<='{1}'
        order by odh_fecha asc
        """.format(pac_id, today)

        tupla_desc = ('odh_id', 'odh_fechacrea', 'odh_fecha', 'pac_id', 'odh_tipo', 'tipodesc')

        return self.all(sql, tupla_desc)

    def get_json_histo(self, odh_id):
        sql = """
        select odh_odontograma, odh_protesis from todontograma_hist where odh_id = {0}
        """.format(odh_id)

        tupla_desc = ('odh_odontograma', 'odh_protesis')
        return self.first(sql, tupla_desc)

    def save_histo(self, od_id, user_crea):
        todontograma = self.find_byid(od_id=od_id)
        today = datetime.datetime.now()
        odhist = self.find_histo(pac_id=todontograma.pac_id, fecha=today)
        if odhist is not None:
            odhist.odh_odontograma = todontograma.od_odontograma
            odhist.odh_tipo = todontograma.od_tipo
            odhist.odh_protesis = todontograma.od_protesis
            odhist.odh_odontograma = todontograma.od_odontograma
            self.dbsession.add(odhist)
        else:
            odhistnew = TOdontogramaHist()
            odhistnew.odh_fechacrea = today
            odhistnew.odh_odontograma = todontograma.od_odontograma
            odhistnew.odh_protesis = todontograma.od_protesis
            odhistnew.odh_tipo = todontograma.od_tipo
            odhistnew.pac_id = todontograma.pac_id,
            odhistnew.user_crea = user_crea
            odhistnew.odh_fecha = today
            self.dbsession.add(odhistnew)
