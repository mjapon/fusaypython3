# coding: utf-8
"""
Fecha de creacion 5/12/21
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.aguap.tagp_models import TAgpMedidor
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TagpMedidorAguaDao(BaseDao):

    @staticmethod
    def _aux_valid_mdg_num(form):
        if not cadenas.es_nonulo_novacio(form['mdg_num']):
            raise ErrorValidacionExc('Ingrese el número de cédula, ruc o pasaporte')

    @staticmethod
    def get_form():
        return {
            'mdg_id': 0,
            'cna_id': 0,
            'mdg_num': '',
            'mdg_estado': 1,
            'mdg_estadofis': 1,
            'mdg_obs': ''
        }

    def existe(self, mdg_num):
        sql = """
        select count(*) as cuenta from tagp_medidor where mdg_num = '{0}'
        and mdg_estado = 1
        """.format(cadenas.strip(mdg_num))
        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def validarcrea(self, form):
        self._aux_valid_mdg_num(form)
        mdg_num = form['mdg_num']
        if self.existe(mdg_num):
            raise ErrorValidacionExc(
                'Ya existe un medidor registrado con el número \'{0}\', favor verificar'.format(mdg_num))

    def crear(self, form, usercrea):
        self.validarcrea(form)
        medidor = TAgpMedidor()
        medidor.cna_id = form['cna_id']
        medidor.mdg_num = form['mdg_num']
        medidor.mdg_estado = form['mdg_estado']
        medidor.mdg_estadofis = form['mdg_estadofis']
        medidor.mdg_obs = form['mdg_obs']
        medidor.mdg_fechacrea = datetime.now()
        medidor.mdg_usercrea = usercrea
        self.dbsession.add(medidor)

    def find_by_id(self, mdg_id):
        tagpmedidor = self.dbsession.query(TAgpMedidor).filter(TAgpMedidor.mdg_id == mdg_id).first()
        return tagpmedidor

    def editar(self, form, useredit):
        tagpmedidor = self.find_by_id(form['mdg_id'])
        if tagpmedidor is not None:
            tagpmedidor.mdg_num = form['mdg_num']
            self.dbsession.add(tagpmedidor)

    def anular(self, form, useranula):
        tagpmedidor = self.find_by_id(form['mdg_id'])
        if tagpmedidor is not None:
            tagpmedidor.mdg_estado = 2
            self.dbsession.add(tagpmedidor)

    def anular_by_cna_id(self, cna_id, useranula):
        tagpmedidor = self.dbsession.query(TAgpMedidor).filter(TAgpMedidor.cna_id == cna_id).first()
        if tagpmedidor is not None:
            tagpmedidor.mdg_estado = 2
            self.dbsession.add(tagpmedidor)

    def get_form_edit(self, cna_id):
        sql = """
        select 
        mdg_id,        
        cna_id,
        mdg_num,
        mdg_fechacrea,
        mdg_usercrea,
        mdg_estado,
        mdg_estadofis,
        mdg_obs from tagp_medidor where cna_id ={0}    
        """.format(cna_id)
        tupla_desc = ('mdg_id',
                      'cna_id',
                      'mdg_num',
                      'mdg_fechacrea',
                      'mdg_usercrea',
                      'mdg_estado',
                      'mdg_estadofis',
                      'mdg_obs')
        return self.first(sql, tupla_desc)

    def get_datos_completos(self, mdg_id):
        sql = """
        select cn.cna_id,
           cn.per_id,
           cn.cna_fechacrea,
         date(cn.cna_fechacrea) as dcna_fechacrea,
           cn.cna_usercrea,
           vu.referente as usercrea,
            per.per_ciruc,
            per.per_apellidos,
            per.per_nombres,
            com.cmn_nombre as comunidad,
            cn.cna_barrio,
            cn.cna_sector,
            cn.cna_direccion,
            tm.mdg_num,
            ic.ic_nombre as tarifa,
            cn.cna_teredad,
            case WHEN cn.cna_teredad THEN 'Si' else 'No' end as teredad,
            case
               when cn.cna_estadoserv=1 then 'Habilitado'
               when cn.cna_estadoserv=1 then 'Suspendido'
               else 'Desconocido' end as cna_estadoserv_desc,
            cn.cna_estado,
            cn.cna_estadoserv,
            cn.cna_nmingas,
            cn.cna_referencia,
            tm.mdg_id,
            coalesce(per.per_apellidos,'')||' '||per.per_nombres as nomapel,
           ic.ic_id,
           trf.trf_id
    from tagp_contrato cn
    join tagp_medidor tm on cn.cna_id = tm.cna_id and tm.mdg_estado = 1
    join tpersona per on per.per_id = cn.per_id 
    join vusers vu on vu.us_id = cn.cna_usercrea
    join tagp_tarifa trf on trf.trf_id = cn.cna_tarifa
    join titemconfig ic on trf.ic_id = ic.ic_id
    join public.tcomunidad com on cn.cna_barrio = com.cmn_id
    where  tm.mdg_id  = {0} 
    order by per_apellidos, per_nombres
        
        """.format(mdg_id)

        tupla_desc = (
            'cna_id', 'per_id', 'cna_fechacrea', 'dcna_fechacrea', 'cna_usercrea', 'usercrea', 'per_ciruc',
            'per_apellidos', 'per_nombres', 'comunidad', 'cna_barrio', 'cna_sector', 'cna_direccion', 'mdg_num',
            'tarifa', 'cna_teredad', 'teredad', 'cna_estadoserv_desc', 'cna_estado', 'cna_estadoserv', 'cna_nmingas',
            'cna_referencia', 'mdg_id', 'nomapel', 'ic_id', 'trf_id'
        )

        datos_medidor = self.first(sql, tupla_desc)
        return datos_medidor

    def buscar_byreg(self, per_id):
        sql = """
        select 
        """
