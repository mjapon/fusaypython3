# coding: utf-8
"""
Fecha de creacion 1/7/21
@autor: mjapon
"""
import datetime
import logging
from functools import reduce

from sqlalchemy.orm import make_transient

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.dental.todplntratamiento.todplntrtmto_model import TOdPlnTrtmto
from fusayrepo.logica.fusay.tasiabono.tasiabono_model import TAsiAbono
from fusayrepo.logica.fusay.tasicredito.tasicredito_dao import TAsicreditoDao
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasidetimp.tasidetimp_model import TAsidetimp
from fusayrepo.logica.fusay.tasiento.tasiento_dao import TasientoDao
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsientoAud
from fusayrepo.logica.fusay.tmodelocontab.tmodelocontab_dao import TModelocontabDao
from fusayrepo.logica.fusay.ttransacc.ttransacc_dao import TTransaccDao
from fusayrepo.logica.fusay.ttransaccimp.ttransaccimp_dao import TTransaccImpDao
from fusayrepo.utils import cadenas, fechas, ctes, numeros

log = logging.getLogger(__name__)


class TOdPlanTratamientoDao(BaseDao):

    def get_form(self, pac_id):
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
            datosmc = tmodcontabdao.get_itemconfig_with_mc(ic_id=det['art_codigo'], tra_codigo=tra_codigo)
            if datosmc is not None:
                det['cta_codigo'] = datosmc['cta_codigo']
                det['dt_debito'] = datosmc['mcd_signo']

        if int(formcab['trn_codigo']) > 0:
            print('Se procede a crear una nueva factura de plan--->')
            new_trncod = self.editar(trn_codigo=formcab['trn_codigo'], user_edita=user_crea, sec_codigo=sec_codigo,
                                     detalles=detalles, pagos=pagos, totales=form['totales'])

            todplantrata = self.dbsession.query(TOdPlnTrtmto).filter(TOdPlnTrtmto.pnt_id == formplan['pnt_id']).first()
            if todplantrata is not None:
                todplantrata.trn_codigo = new_trncod
                self.dbsession.add(todplantrata)

            return {'trn_codigo': new_trncod, 'pnt_codigo': todplantrata.pnt_id}

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
        trn_codigo = tsientodao.crear(form=formcab, form_persona=form_persona, user_crea=user_crea, detalles=detalles,
                                      pagos=pagos, creaupdpac=False, totales=form['totales'])
        tplantratamiento.trn_codigo = trn_codigo

        self.dbsession.add(tplantratamiento)
        self.dbsession.flush()
        return {'trn_codigo': trn_codigo, 'pnt_codigo': tplantratamiento.pnt_id}

    def editar(self, trn_codigo, user_edita, sec_codigo, detalles, pagos, totales):
        tasientodao = TasientoDao(self.dbsession)
        ttransaccdao = TTransaccDao(self.dbsession)

        trn_codorig = trn_codigo
        tasiento = tasientodao.find_entity_byid(trn_codorig)
        tasicredao = TAsicreditoDao(self.dbsession)

        per_codigo = 0
        tra_codigo = 0
        iscontab = False

        if tasiento is not None:
            per_codigo = tasiento.per_codigo
            tra_codigo = tasiento.tra_codigo
            ttransacc = ttransaccdao.get_ttransacc(tra_codigo=tra_codigo)

            if ttransacc is not None:
                iscontab = ttransacc['tra_contab'] == 1

            self.dbsession.expunge(tasiento)
            make_transient(tasiento)
        else:
            raise ErrorValidacionExc('No pude recupar información de la transacción (tr_cod:{0})'.format(trn_codigo))

        tasiento.trn_codigo = None
        tasiento.sec_codigo = sec_codigo
        tasiento.us_id = user_edita

        datoscred = tasicredao.find_datoscred_intransacc(trn_codigo=trn_codigo)
        abonos = None
        if datoscred is not None:
            print('hay datos de un credito generado buscar abonos asocioados')
            abonos = self.dbsession.query(TAsiAbono).filter(TAsiAbono.dt_codcre == datoscred['dt_codigo']).all()

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        trn_codigo = tasiento.trn_codigo

        valoresdebehaber = []

        ttransaccimpdao = TTransaccImpDao(self.dbsession)
        configtransaccimp = ttransaccimpdao.get_config(tra_codigo=tra_codigo, sec_codigo=sec_codigo)

        impuestos = []
        if configtransaccimp is not None and totales is not None:
            ivaval = totales['iva']
            if ivaval is not None and ivaval > 0:
                impuestos.append({
                    'cta_codigo': configtransaccimp['tra_impg'],
                    'dt_debito': configtransaccimp['tra_signo'],
                    'dt_valor': ivaval
                })

        for detalle in detalles:
            tasidetalle = TAsidetalle()

            per_cod_det = int(detalle['per_codigo'])
            if per_cod_det == 0:
                per_cod_det = tasiento.per_codigo

            tasidetalle.dt_codigo = None
            tasidetalle.trn_codigo = trn_codigo
            tasidetalle.cta_codigo = detalle['cta_codigo']
            tasidetalle.art_codigo = detalle['art_codigo']
            tasidetalle.per_codigo = per_cod_det
            tasidetalle.pry_codigo = detalle['pry_codigo']
            tasidetalle.dt_cant = detalle['dt_cant']
            tasidetalle.dt_precio = detalle['dt_precio']
            tasidetalle.dt_debito = detalle['dt_debito']
            tasidetalle.dt_preref = detalle['dt_preref']
            tasidetalle.dt_decto = detalle['dt_decto']
            tasidetalle.dt_valor = detalle['dt_valor']
            tasidetalle.dt_dectogen = detalle['dt_dectogen']
            tasidetalle.dt_tipoitem = ctes.DT_TIPO_ITEM_DETALLE
            tasidetalle.dt_valdto = detalle['dt_valdto']
            tasidetalle.dt_valdtogen = detalle['dt_valdtogen']
            tasidetalle.dt_codsec = detalle['dt_codsec']

            valoresdebehaber.append({'dt_debito': tasidetalle.dt_debito, 'dt_valor': tasidetalle.dt_valor})

            self.dbsession.add(tasidetalle)
            self.dbsession.flush()
            dt_codigo = tasidetalle.dt_codigo

            tasidetimp = TAsidetimp()
            tasidetimp.dai_codigo = None
            tasidetimp.dt_codigo = dt_codigo
            tasidetimp.dai_imp0 = detalle['dai_imp0'] if cadenas.es_nonulo_novacio(detalle['dai_imp0']) else None
            tasidetimp.dai_impg = detalle['dai_impg'] if cadenas.es_nonulo_novacio(detalle['dai_impg']) else None
            tasidetimp.dai_ise = detalle['dai_ise'] if cadenas.es_nonulo_novacio(detalle['dai_ise']) else None
            tasidetimp.dai_ice = detalle['dai_ice'] if cadenas.es_nonulo_novacio(detalle['dai_ice']) else None

            self.dbsession.add(tasidetimp)

        for impuesto in impuestos:
            detimpuesto = TAsidetalle()
            detimpuesto.trn_codigo = trn_codigo
            detimpuesto.per_codigo = per_codigo
            detimpuesto.cta_codigo = impuesto['cta_codigo']
            detimpuesto.art_codigo = 0
            detimpuesto.dt_debito = impuesto['dt_debito']
            detimpuesto.dt_valor = impuesto['dt_valor']
            valoresdebehaber.append({'dt_debito': detimpuesto.dt_debito, 'dt_valor': detimpuesto.dt_valor})
            detimpuesto.dt_tipoitem = ctes.DT_TIPO_ITEM_IMPUESTO
            detimpuesto.dt_codsec = sec_codigo
            self.dbsession.add(detimpuesto)

        sumapagos = 0.0
        for pago in pagos:
            detpago = TAsidetalle()
            if float(pago['dt_valor']) > 0.0:
                detpago.trn_codigo = trn_codigo
                detpago.per_codigo = per_codigo
                detpago.cta_codigo = pago['cta_codigo']
                detpago.art_codigo = 0
                detpago.dt_debito = pago['dt_debito']
                detpago.dt_valor = float(pago['dt_valor'])
                detpago.dt_tipoitem = ctes.DT_TIPO_ITEM_PAGO
                detpago.dt_codsec = pago['dt_codsec']
                sumapagos += detpago.dt_valor

                valoresdebehaber.append({'dt_debito': detpago.dt_debito, 'dt_valor': detpago.dt_valor})

                ic_clasecc = pago['ic_clasecc']

                self.dbsession.add(detpago)
                self.dbsession.flush()
                dt_codigo = detpago.dt_codigo
                if float(pago['dt_valor']) > 0.0:
                    if ic_clasecc == 'XC' or ic_clasecc == 'XP':
                        cre_tipo = 0
                        if ic_clasecc == 'XC':
                            cre_tipo = 1
                        if ic_clasecc == 'XP':
                            cre_tipo = 2

                        creditodao = TAsicreditoDao(self.dbsession)
                        tra_codigo_cred = ctes.TRA_COD_CRED_VENTA
                        if int(tra_codigo) == ctes.TRA_COD_FACT_COMPRA:
                            tra_codigo_cred = ctes.TRA_COD_CRED_COMPRA

                        formcre = {
                            'dt_codigo': dt_codigo,
                            'cre_fecini': fechas.parse_fecha(tasiento.trn_fecreg),
                            'cre_fecven': None,
                            'cre_intere': 0.0,
                            'cre_intmor': 0.0,
                            'cre_codban': None,
                            'cre_saldopen': detpago.dt_valor,
                            'cre_tipo': cre_tipo
                        }
                        creditodao.crear(form=formcre, tra_codigo_cred=tra_codigo_cred)

                        # Si hay abonos asociados se debe pasar estos abonos a la nueva factdura
                        if abonos is not None:
                            for abono in abonos:
                                abono.dt_codcre = dt_codigo
                                self.dbsession.add(abono)

        totalform = numeros.roundm(float(totales['total']), 2)
        totalsuma = numeros.roundm(sumapagos, 2)

        if totalform != totalsuma:
            raise ErrorValidacionExc(
                'El total de la factura ({0}) no coincide con la suma de los pagos ({1})'.format(totalform, totalsuma))

        if iscontab:
            # Vericar que sumen debe y haber correctamente
            itemsdebe = map(lambda x: x['dt_valor'], filter(lambda item: item['dt_debito'] == 1, valoresdebehaber))
            itemshaber = map(lambda x: x['dt_valor'], filter(lambda item: item['dt_debito'] == -1, valoresdebehaber))

            sumadebe = reduce(lambda a, b: a + b, itemsdebe, 0.0)
            sumahaber = reduce(lambda a, b: a + b, itemshaber, 0.0)

            sumadeberound = numeros.roundm2(sumadebe)
            sumahaberound = numeros.roundm2(sumahaber)
            if sumadeberound != sumahaberound:
                raise ErrorValidacionExc(
                    'La suma del debe ({0}) y el haber({1}) no coinciden, favor verificar'.format(sumadeberound,
                                                                                                  sumahaberound))

        # Se debe anular la facdtura anterior
        tasiento_org = tasientodao.find_entity_byid(trn_codorig)
        tasiento_org.tr_valido = 1
        self.dbsession.add(tasiento_org)
        tasientoaud = TAsientoAud()
        tasientoaud.trn_codigo = tasiento_org
        tasientoaud.aud_accion = ctes.AUD_ASIENTO_ANULAR
        tasientoaud.aud_obs = ''
        tasientoaud.aud_user = user_edita
        self.dbsession.add(tasientoaud)

        return trn_codigo

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
        where pac_id = {0} and pnt_estado != 5 order by pnt_fechacrea
        """.format(pac_id)

        tupla_desc = (
            'pnt_id', 'pnt_nombre', 'pnt_fechacrea', 'pnt_estado', 'estadodesc', 'med_id', 'pac_id', 'trn_codigo',
            'pnt_obs')
        return self.all(sql, tupla_desc)

    def cambiar_estado(self, pnt_id, nuevo_estado, user_upd):
        todplantratamiento = self.dbsession.query(TOdPlnTrtmto).filter(TOdPlnTrtmto.pnt_id == pnt_id).first()
        if todplantratamiento is not None:
            todplantratamiento.user_upd = user_upd
            todplantratamiento.fecha_upd = datetime.datetime.now()
            todplantratamiento.pnt_estado = nuevo_estado

            if int(nuevo_estado) == 5:  # Se anula el plan, se debe anular tambien la factura
                tasientodao = TasientoDao(self.dbsession)
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                if tasiento is not None:
                    tasiento.trn_valido = 2
                    self.dbsession.add(tasiento)
            elif int(nuevo_estado) == 2:
                # Cuaando el estado es aprobado entonces se quita la marca de factura pendiente
                tasientodao = TasientoDao(self.dbsession)
                tasiento = tasientodao.find_entity_byid(trn_codigo=todplantratamiento.trn_codigo)
                if tasiento is not None:
                    tasiento.trn_docpen = 'F'
                    self.dbsession.add(tasiento)

            self.dbsession.add(todplantratamiento)

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
