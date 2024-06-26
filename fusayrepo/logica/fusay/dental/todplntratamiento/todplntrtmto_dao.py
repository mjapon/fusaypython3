# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import datetime
import logging

from fusayrepo.logica.compele.compele_util import CompeleUtilDao
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.dental.todplntratamiento.todplntrtmto_model import TOdPlnTrtmto
from fusayrepo.logica.fusay.tasiento.auxlogicasi_dao import AuxLogicAsiDao
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tbilletera.tbilleterahist_dao import TBilleteraHistoDao
from fusayrepo.logica.fusay.tmodelocontab.tmodelocontab_dao import TModelocontabDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


class TOdPlanTratamientoDao(BaseDao):

    @staticmethod
    def get_form(pac_id):
        form = {
            'pnt_id': 0,
            'pnt_nombre': '',
            'med_id': 0,
            'pac_id': pac_id,
            'trn_codigo': 0,
            'pnt_obs': ''
        }
        return form

    def crear(self, form, user_crea, sec_codigo):
        formplan = form['formplan']
        formcab = form['form_cab']
        form_persona = form['form_persona']
        detalles = form['detalles']
        pagos = form['pagos']

        # Los detalles se les debe agregar el model contable en caso de que tenga
        tra_codigo = formcab['tra_codigo']
        tmodcontabdao = TModelocontabDao(self.dbsession)
        for det in detalles:
            datosmc = tmodcontabdao.get_itemconfig_with_mc(ic_id=det['art_codigo'], tra_codigo=tra_codigo,
                                                           sec_codigo=sec_codigo)
            if datosmc is not None:
                det['cta_codigo'] = datosmc['cta_codigo']
                det['dt_debito'] = datosmc['mcd_signo']
            else:
                raise ErrorValidacionExc(
                    'No es posible registrar el plan de tratamiento, no se ha definido modelo contable (art:{0})'.format(
                        det['art_codigo']))

        if int(formcab['trn_codigo']) > 0:
            resultedit = self.editar(trn_codigo=formcab['trn_codigo'], user_edita=user_crea, sec_codigo=sec_codigo,
                                     detalles=detalles, pagos=pagos, totales=form['totales'], formplan=formplan)

            return resultedit

        tplantratamiento = TOdPlnTrtmto()
        tplantratamiento.pnt_nombre = cadenas.strip_upper(formplan['pnt_nombre'])
        tplantratamiento.pnt_fechacrea = datetime.datetime.now()
        tplantratamiento.user_crea = user_crea
        tplantratamiento.pnt_obs = cadenas.strip(formplan['pnt_obs'])
        tplantratamiento.med_id = formplan['med_id']
        tplantratamiento.pac_id = formplan['pac_id']
        tplantratamiento.pnt_estado = 1

        # Registro de factura
        tsientodao = TasientoDao(self.dbsession)
        formcab['trn_observ'] = cadenas.strip(formplan['pnt_obs'])
        trn_codigo = tsientodao.crear(form=formcab, form_persona=form_persona, user_crea=user_crea, detalles=detalles,
                                      pagos=pagos, creaupdpac=False, totales=form['totales'], gen_secuencia=False)
        tplantratamiento.trn_codigo = trn_codigo

        self.dbsession.add(tplantratamiento)
        self.dbsession.flush()
        return {'trn_codigo': trn_codigo, 'pnt_codigo': tplantratamiento.pnt_id}

    def editar(self, trn_codigo, user_edita, sec_codigo, detalles, pagos, totales, formplan):
        tasientodao = TasientoDao(self.dbsession)
        formcab = {
            'trn_observ': formplan['pnt_obs']
        }
        new_trn_codigo = tasientodao.editar(trn_codigo=trn_codigo, user_edita=user_edita, sec_codigo=sec_codigo,
                                            detalles=detalles, pagos=pagos, totales=totales, formcab=formcab)

        self.edit_datos_plan(formplan=formplan, new_trcod=new_trn_codigo)

        return {'trn_codigo': new_trn_codigo, 'pnt_codigo': formplan['pnt_id']}

    def find_by_id(self, pnt_id):
        return self.dbsession.query(TOdPlnTrtmto).filter(TOdPlnTrtmto.pnt_id == pnt_id).first()

    def edit_datos_plan(self, formplan, new_trcod):
        pnt_id = formplan['pnt_id']

        plantrata = self.find_by_id(pnt_id=pnt_id)
        if plantrata is not None:
            plantrata.trn_codigo = new_trcod
            plantrata.pnt_obs = formplan['pnt_obs']
            plantrata.pnt_nombre = cadenas.strip_upper(formplan['pnt_nombre'])
            self.dbsession.add(plantrata)

    def listar(self, pac_id):
        sql = """
        select pnt_id, pnt_nombre, pnt_fechacrea, pnt_estado,
        case when  pnt_estado = 1 then 'Creado'
        when  pnt_estado = 2 then 'Aprobado'
        when  pnt_estado = 3 then 'En curso'
        when  pnt_estado = 4 then 'Finalizado'
        when  pnt_estado = 5 then 'Anulado'
        else 'Desconocido' end as estadodesc,
        med_id, pac_id, trn_codigo, pnt_obs from todplntrtmto
        where pac_id = {0} and pnt_estado != 5 order by pnt_fechacrea desc
        """.format(pac_id)

        tupla_desc = (
            'pnt_id', 'pnt_nombre', 'pnt_fechacrea', 'pnt_estado', 'estadodesc', 'med_id', 'pac_id', 'trn_codigo',
            'pnt_obs')
        return self.all(sql, tupla_desc)

    def cambiar_estado(self, pnt_id, nuevo_estado, user_upd,
                       cod_tipo_doc=0, alm_codigo=0, sec_id=0, tdv_codigo=0, formreferente=None,
                       emp_codigo=None, emp_esquema=None):
        todplantratamiento = self.dbsession.query(TOdPlnTrtmto).filter(TOdPlnTrtmto.pnt_id == pnt_id).first()
        response_logica_facte = None
        tasientodao = TasientoDao(self.dbsession)
        if todplantratamiento is not None:
            todplantratamiento.user_upd = user_upd
            todplantratamiento.fecha_upd = datetime.datetime.now()
            todplantratamiento.pnt_estado = nuevo_estado

            if int(nuevo_estado) == 5:  # Se anula el plan, se debe anular tambien la factura
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                if tasiento is not None:
                    tasiento.trn_valido = 2
                    self.dbsession.add(tasiento)

            elif int(nuevo_estado) == 2:
                # Cuaando el estado es aprobado entonces se quita la marca de factura pendiente
                tasientodao = TasientoDao(self.dbsession)
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                compeleutil = CompeleUtilDao(self.dbsession)
                if tasiento is not None:
                    if int(cod_tipo_doc) > 0:
                        aulogicasidao = AuxLogicAsiDao(self.dbsession)
                        log.error('ODONTO MJ--> tipodoc:{0}, alm_codigo:{1}, sec_id:{2}, tdv_codigo:{3}'.format(
                            cod_tipo_doc,
                            alm_codigo, sec_id, tdv_codigo))
                        form_cab = tasientodao.get_form_cabecera(cod_tipo_doc,
                                                                 alm_codigo, sec_id, tdv_codigo, tra_emite=1)

                        if formreferente is not None:
                            personadao = TPersonaDao(self.dbsession)
                            per_codigo = formreferente['per_id']
                            per_ciruc = formreferente['per_ciruc']
                            if per_codigo is not None and per_codigo > 0:
                                personadao.actualizar(per_id=per_codigo, form=formreferente)
                            else:
                                persona = personadao.buscar_porciruc(per_ciruc=per_ciruc)
                                if persona is not None:
                                    per_codigo = persona[0]['per_id']
                                    personadao.actualizar(per_id=per_codigo, form=formreferente)
                                else:
                                    per_codigo = personadao.crear(form=formreferente)

                        aulogicasidao.aux_set_datos_secuencia(tasiento=tasiento, formcab=form_cab,
                                                              per_codigo=per_codigo, sec_codigo=sec_id)
                        response_logica_facte = compeleutil.logica_check_envio_factura_dental(
                            trn_codigo=tasiento.trn_codigo)

                        tbillhist_dao = TBilleteraHistoDao(self.dbsession)
                        tbillhist_dao.generate_history_mov(trn_codigo=todplantratamiento.trn_codigo)

            self.dbsession.add(todplantratamiento)

        return response_logica_facte

    def get_detalles(self, pnt_id):
        sql = """
        select pnt_id, pnt_nombre, pnt_fechacrea, user_crea, pnt_estado, med_id, pac_id, trn_codigo, pnt_obs,
        user_upd, fecha_upd, b.per_nombres||' '|| b.per_apellidos as medico, c.per_ciruc as pac_ciruc, 
        c.per_nombres||' '||c.per_apellidos as paciente from todplntrtmto a left join tpersona b on a.med_id = b.per_id
        left join tpersona c on a.pac_id = c.per_id where pnt_id = {0}  
        """.format(pnt_id)

        tupla_desc = ('pnt_id', 'pnt_nombre', 'pnt_fechacrea', 'user_crea', 'pnt_estado', 'med_id', 'pac_id',
                      'trn_codigo', 'pnt_obs', 'user_upd', 'fecha_upd', 'medico', 'pac_ciruc', 'paciente')
        return self.first(sql, tupla_desc)
