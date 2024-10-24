# coding: utf-8
"""
Fecha de creacion 3/27/19
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tparams.tparam_model import TParams
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TParamsDao(BaseDao):

    def get_params_value(self, abreviaciones, sec_id=0):
        abrevs_str = ','.join(["'{0}'".format(abr) for abr in abreviaciones])
        sql = ("select tprm_abrev, tprm_val from tparams where tprm_abrev in ({0}) and tprm_seccion = {1}"
               .format(abrevs_str, sec_id))
        return self.all(sql, ('tprm_abrev', 'tprm_val'))

    def get_param_value(self, abreviacion, sec_id=0):
        sql = "select tprm_val as val from tparams where tprm_abrev = '{0}' and tprm_seccion = {1}".format(abreviacion,
                                                                                                           sec_id)
        val = self.first_col(sql, 'val')
        return val

    def find(self, filtro, estado, seccion):
        filtrolike = '%%'
        if cadenas.es_nonulo_novacio(filtro):
            filtrolike = '%{0}%'.format(cadenas.strip(filtro))

        estadosql = ''
        if estado is not None and int(estado) >= 0:
            estadosql = f' and parm.tprm_estado = {estado}'

        seccionsql = ''
        if seccion is not None and int(seccion) > 0:
            seccionsql = f' and parm.tprm_seccion = {seccion}'

        sql = f"""
        select parm.tprm_id, parm.tprm_abrev, parm.tprm_nombre, parm.tprm_val, parm.tprm_estado, 
        case parm.tprm_estado 
        when '0' then 'Activo'
        when '1' then 'Inactivo'
        else 'Desconocido' end as estado,
        coalesce(vusers.referente,'') as user,
        coalesce(parm.tprm_fechaupd, parm.tprm_fechacrea) as fecha,
        coalesce(tseccion.sec_nombre, 'TODOS') as seccion
        from tparams parm 
        left join vusers on coalesce(parm.tprm_userupd,parm.tprm_usercrea) = vusers.us_id
        left join tseccion on coalesce(parm.tprm_seccion, 0) = tseccion.sec_id 
        where (parm.tprm_abrev ilike '{filtrolike}' or parm.tprm_nombre ilike '{filtrolike}') {estadosql} {seccionsql}
         order by parm.tprm_abrev
        """
        tupladesc = ('tprm_id', 'tprm_abrev', 'tprm_nombre', 'tprm_val', 'tprm_estado',
                     'estado', 'user', 'fecha', 'seccion')
        return self.all(sql, tupladesc)

    def update_param_value(self, prm_id, form, userupd):
        tparam = self.dbsession.query(TParams).filter(TParams.tprm_id == prm_id).first()
        if tparam is not None:
            if cadenas.es_nonulo_novacio(form['tprm_nombre']):
                tparam.tprm_nombre = cadenas.strip(form['tprm_nombre'])

            if cadenas.es_nonulo_novacio(form['tprm_val']):
                tparam.tprm_val = cadenas.strip(form['tprm_val'])

            if cadenas.es_nonulo_novacio(form['tprm_estado']):
                tparam.tprm_estado = form['tprm_estado']

            tparam.tprm_fechaupd = datetime.datetime.now()
            tparam.tprm_userupd = userupd
            self.dbsession.add(tparam)

    def exist_abrev(self, abreviacion, seccion):
        sql = "select count(*) as cuenta from tparams where tprm_abrev = :abrev and tprm_seccion = :seccion"
        countrow = self.first_raw(sql, abrev=abreviacion, seccion=seccion)
        return countrow[0] > 0

    def create_param_value(self, form, usercrea):

        if not cadenas.es_nonulo_novacio(form['codigo']):
            raise ErrorValidacionExc('El codigo del parámetro es requerido')
        elif len(cadenas.strip(form['codigo'])) > 20:
            raise ErrorValidacionExc('La logitud del código no puede sobrepasar los 20 caracteres')
        elif self.exist_abrev(abreviacion=form['codigo'], seccion=form['seccion']):
            codigo = form['codigo']
            raise ErrorValidacionExc(f'Ya existe un parámetro con el código \'{codigo}\' para la sección indicada')

        if not cadenas.es_nonulo_novacio(form['descripcion']):
            raise ErrorValidacionExc('La descripción del parámetro es requerida')
        elif len(cadenas.strip(form['descripcion'])) > 80:
            raise ErrorValidacionExc('La longitud de la descripcion no puede sobrepasara los 80 caracteres')

        if not cadenas.es_nonulo_novacio(form['valor']):
            raise ErrorValidacionExc('El valor del parámetro es requerido')
        elif len(cadenas.strip(form['valor'])) > 150:
            raise ErrorValidacionExc('El valor del parámetro no puede sobrepasar los 150 caracteres')

        tparam = TParams()
        tparam.tprm_abrev = cadenas.strip(form['codigo'])
        tparam.tprm_nombre = cadenas.strip(form['descripcion'])
        tparam.tprm_val = cadenas.strip(form['valor'])
        tparam.tprm_seccion = form['seccion']
        tparam.tprm_estado = 0
        tparam.tprm_usercrea = usercrea
        tparam.tprm_fechacrea = datetime.datetime.now()
        self.dbsession.add(tparam)

    def update_sequence_billetera(self):
        abr_sequence = 'billSeqCode'
        self.aux_update_sequence(abr_sequence)

    def aux_update_sequence(self, seqname):
        tparam = self.dbsession.query(TParams).filter(TParams.tprm_abrev == seqname).first()
        if tparam is not None:
            current_val = int(tparam.tprm_val)
            newvalue = current_val + 1
            tparam.tprm_val = str(newvalue)

    def update_sequence_codbar(self):
        abr_sequence = 'artsSeqCodBar'
        self.aux_update_sequence(abr_sequence)
        """
        tparam = self.dbsession.query(TParams).filter(TParams.tprm_abrev == abr_sequence).first()
        if tparam is not None:
            current_val = int(tparam.tprm_val)
            newvalue = current_val + 1
            tparam.tprm_val = str(newvalue)
        """

    def get_next_sequence_billmov(self):
        next_sequence = self.get_param_value('billMovSeq')
        return int(next_sequence)

    def update_sequence_billmov(self):
        abr_sequence = 'billMovSeq'
        self.aux_update_sequence(abr_sequence)

    def get_next_sequence_bill(self):
        next_sequence = self.get_param_value('billSeqCode')
        return int(next_sequence)

    def get_next_sequence_codbar(self):
        next_sequence = self.get_param_value('artsSeqCodBar')
        return int(next_sequence)

    def get_ruta_savejobs(self):
        val = self.get_param_value('pathSaveJobs')
        if val is None:
            raise ErrorValidacionExc(
                u'El parametro pathSaveJobs no está registrado en la base de datos, favor verificar')
        return val

    def aplica_dental(self):
        prmvalue = self.get_param_value('ARTS_DENTAL')
        appldent = False
        if prmvalue is not None:
            appldent = prmvalue == '1'

        return appldent
