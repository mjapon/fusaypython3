# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.excepciones.validacion import ErrorValidacionExc
from fusayrepo.logica.fusay.tasidetalle.tasidetalle_model import TAsidetalle
from fusayrepo.logica.fusay.tasidetimp.tasidetimp_model import TAsidetimp
from fusayrepo.logica.fusay.tasiento.tasiento_model import TAsiento
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao
from fusayrepo.logica.fusay.ttransaccpdv.ttransaccpdv_dao import TTransaccPdvDao
from fusayrepo.utils import fechas, numeros

log = logging.getLogger(__name__)


class TasientoDao(BaseDao):

    def find_entity_byid(self, trn_codigo):
        return self.dbsession.query(TAsiento).filter(TAsiento.trn_codigo == trn_codigo).first()

    def get_form_cabecera(self, tra_codigo, alm_codigo, sec_codigo, tdv_codigo):

        ttransacc_pdv = TTransaccPdvDao(self.dbsession)
        resestabsec = ttransacc_pdv.get_estabptoemi_secuencia(alm_codigo=alm_codigo, tra_codigo=tra_codigo,
                                                              tdv_codigo=tdv_codigo, sec_codigo=sec_codigo)
        trn_compro = ''
        form_asiento = {
            'dia_codigo': 0,
            'trn_fecreg': fechas.parse_fecha(fechas.get_now()),
            'trn_compro': trn_compro,
            'trn_docpen': 'F',
            'trn_pagpen': 'F',
            'sec_codigo': sec_codigo,
            'tra_codigo': tra_codigo,
            'trn_observ': '',
            'tdv_codigo': tdv_codigo,
            'fol_codigo': 0,
            'trn_tipcom': '',
            'trn_suscom': '',
            'tps_codigo': resestabsec['tps_codigo'],
            'estabptoemi': resestabsec['estabptoemi'],
            'secuencia': resestabsec['secuencia']
        }

        return form_asiento

    def get_form_detalle(self):
        form = {
            'cta_codigo': 0,
            'art_codigo': 0,
            'ic_nombre': '',
            'per_codigo': 0,
            'pry_codigo': 0,
            'dt_cant': 1,
            'dt_precio': 0.0,
            'dt_debito': 0,
            'dt_preref': 0.0,
            'dt_decto': 0.0,
            'dt_valor': 0.0,
            'dt_dectogen': 0.0,
            'dt_tipoitem': 1,
            'dt_valdto': 0.0,
            'dto_valdtogen': 0.0,
            'dt_codsec': 1,
            'dai_imp0': None,
            'dai_impg': None,
            'dai_ise': None,
            'dai_ice': None
        }

        return form

    def get_documento(self, trn_codigo):
        sql = """
        select trn_codigo,
        dia_codigo,
        trn_fecreg,
        trn_compro,
        trn_fecha,
        trn_valido,
        trn_docpen,
        trn_pagpen,
        sec_codigo,
        per_codigo,
        tra_codigo,
        us_id,
        trn_observ,
        tdv_codigo,
        fol_codigo,
        trn_tipcom,
        trn_suscom,
        per_codres from tasiento where trn_codigo = {0}
        """.format(trn_codigo)
        tupla_desc = ('trn_codigo',
                      'dia_codigo',
                      'trn_fecreg',
                      'trn_compro',
                      'trn_fecha',
                      'trn_valido',
                      'trn_docpen',
                      'trn_pagpen',
                      'sec_codigo',
                      'per_codigo',
                      'tra_codigo',
                      'us_id',
                      'trn_observ',
                      'tdv_codigo',
                      'fol_codigo',
                      'trn_tipcom',
                      'trn_suscom',
                      'per_codres')

        tasiento = self.first(sql, tupla_desc)

        sql = """
        select dt_codigo, trn_codigo, cta_codigo, art_codigo, per_codigo, pry_codigo, dt_cant, dt_precio, dt_debito,
        dt_preref, dt_decto, dt_valor, dt_dectogen, dt_tipoitem, dt_valdto, dt_valdtogen, dt_codsec, b.ic_nombre
        from tasidetalle a join titemconfig b on a.art_codigo = b.ic_id where dt_tipoitem = 1 and trn_codigo = {0}
        """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre')
        detalles = self.all(sql, tupla_desc)

        sql = """
                select dt_codigo, trn_codigo, cta_codigo, art_codigo, per_codigo, pry_codigo, dt_cant, dt_precio, dt_debito,
                dt_preref, dt_decto, dt_valor, dt_dectogen, dt_tipoitem, dt_valdto, dt_valdtogen, dt_codsec, b.ic_nombre
                from tasidetalle a join titemconfig b on a.cta_codigo = b.ic_id where dt_tipoitem = 2 and trn_codigo = {0}
                """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre')

        pagos = self.all(sql, tupla_desc)

        sql = """
                select dt_codigo, trn_codigo, cta_codigo, art_codigo, per_codigo, pry_codigo, dt_cant, dt_precio, dt_debito,
                dt_preref, dt_decto, dt_valor, dt_dectogen, dt_tipoitem, dt_valdto, dt_valdtogen, dt_codsec, b.ic_nombre
                from tasidetalle a join titemconfig b on a.cta_codigo = b.ic_id where dt_tipoitem = 3 and trn_codigo = {0}
                """.format(trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre')
        impuestos = self.all(sql, tupla_desc)

        # Sumar todos los items del articulo
        total = 0.0
        for item in detalles:
            total += item['dt_valor']

        total = round(total, 2)
        tasiento['totalfact'] = total

        return {
            'tasiento': tasiento,
            'detalles': detalles,
            'pagos': pagos,
            'impuestos': impuestos
        }

    def get_form_pago(self):
        form = {
            'cta_codigo': 0,
            'dt_debito': 1,
            'ic_nombre': '',
            'dt_valor': 0.0,
            'dt_codsec': 1
        }
        return form

    def crear(self, form, form_persona, user_crea, detalles, pagos, totales, creaupdpac=True):
        dia_codigo = form['dia_codigo']
        trn_fecreg = fechas.parse_cadena(form['trn_fecreg'])
        len_compro = 9
        secuencia = form['secuencia']
        trn_compro = "{0}{1}".format(form['estabptoemi'], str(secuencia).zfill(len_compro))
        trn_compro = trn_compro
        trn_fecha = datetime.now()
        trn_valido = 0
        trn_docpen = form['trn_docpen']
        trn_pagpen = form['trn_pagpen']
        sec_codigo = form['sec_codigo']
        tra_codigo = form['tra_codigo']
        us_id = user_crea
        trn_observ = form['trn_observ']
        tdv_codigo = form['tdv_codigo']
        fol_codigo = int(form['fol_codigo'])
        trn_tipcom = form['trn_tipcom']
        trn_suscom = form['trn_suscom']
        per_codres = None

        personadao = TPersonaDao(self.dbsession)

        per_codigo = int(form_persona['per_codigo'])
        if creaupdpac:
            if per_codigo is not None and per_codigo > 0:
                personadao.actualizar(per_id=per_codigo, form=form_persona)
            else:
                persona = personadao.buscar_porciruc(per_ciruc=form_persona['per_ciruc'])
                if persona is not None:
                    per_codigo = persona[0]
                    personadao.actualizar(per_id=per_codigo, form=form_persona)
                else:
                    per_codigo = personadao.crear(form=form_persona)

        tasiento = TAsiento()
        tasiento.dia_codigo = dia_codigo
        tasiento.trn_fecreg = trn_fecreg
        tasiento.trn_compro = trn_compro
        tasiento.trn_fecha = trn_fecha
        tasiento.trn_valido = trn_valido
        tasiento.trn_docpen = trn_docpen
        tasiento.trn_pagpen = trn_pagpen
        tasiento.sec_codigo = sec_codigo
        tasiento.per_codigo = per_codigo
        tasiento.tra_codigo = tra_codigo
        tasiento.us_id = us_id
        tasiento.trn_observ = trn_observ
        tasiento.tdv_codigo = tdv_codigo
        tasiento.fol_codigo = fol_codigo
        tasiento.trn_tipcom = trn_tipcom
        tasiento.trn_suscom = trn_suscom
        tasiento.per_codres = per_codres

        tps_codigo = form['tps_codigo']
        if tps_codigo is not None:
            transaccpdv_dao = TTransaccPdvDao(self.dbsession)
            transaccpdv_dao.gen_secuencia(tps_codigo=tps_codigo, secuencia=secuencia)

        self.dbsession.add(tasiento)
        self.dbsession.flush()

        trn_codigo = tasiento.trn_codigo

        for detalle in detalles:
            tasidetalle = TAsidetalle()

            tasidetalle.dt_codigo = None
            tasidetalle.trn_codigo = trn_codigo
            tasidetalle.cta_codigo = detalle['cta_codigo']
            tasidetalle.art_codigo = detalle['art_codigo']
            tasidetalle.per_codigo = detalle['per_codigo']
            tasidetalle.pry_codigo = detalle['pry_codigo']
            tasidetalle.dt_cant = detalle['dt_cant']
            tasidetalle.dt_precio = detalle['dt_precio']
            tasidetalle.dt_debito = detalle['dt_debito']
            tasidetalle.dt_preref = detalle['dt_preref']
            tasidetalle.dt_decto = detalle['dt_decto']
            tasidetalle.dt_valor = detalle['dt_valor']
            tasidetalle.dt_dectogen = detalle['dt_dectogen']
            tasidetalle.dt_tipoitem = 1
            tasidetalle.dt_valdto = detalle['dt_valdto']
            tasidetalle.dto_valdtogen = detalle['dto_valdtogen']
            tasidetalle.dt_codsec = detalle['dt_codsec']

            self.dbsession.add(tasidetalle)
            self.dbsession.flush()
            dt_codigo = tasidetalle.dt_codigo

            tasidetimp = TAsidetimp()
            tasidetimp.dai_codigo = None
            tasidetimp.dt_codigo = dt_codigo
            tasidetimp.dai_imp0 = detalle['dai_imp0']
            tasidetimp.dai_impg = detalle['dai_impg']
            tasidetimp.dai_ise = detalle['dai_ise']
            tasidetimp.dai_ice = detalle['dai_ice']

            self.dbsession.add(tasidetimp)

        sumapagos = 0.0
        for pago in pagos:
            detpago = TAsidetalle()
            detpago.trn_codigo = trn_codigo
            detpago.per_codigo = per_codigo
            detpago.cta_codigo = pago['cta_codigo']
            detpago.art_codigo = 0
            detpago.dt_debito = pago['dt_debito']
            detpago.dt_valor = pago['dt_valor']
            detpago.dt_tipoitem = 2
            detpago.dt_codsec = pago['dt_codsec']
            sumapagos += detpago.dt_valor

            ic_clasecc = pago['ic_clasecc']
            if ic_clasecc == 'C':
                # Se debe crear un registro en la tabla de credito
                pass

            self.dbsession.add(detpago)

        totalform = numeros.redondear(float(totales['total']), 2)
        totalsuma = numeros.redondear(sumapagos, 2)

        if totalform != totalsuma:
            raise ErrorValidacionExc(
                'El total de la factura ({0}) no coincide con la suma de los pagos ({1})'.format(totalform, totalsuma))

        return trn_codigo
