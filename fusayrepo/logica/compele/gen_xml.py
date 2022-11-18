# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import itertools
import logging
import xml.etree.ElementTree as et

from fusayrepo.logica.compele import ctes_facte
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.utils import fechas, ctes, cadenas, numeros

log = logging.getLogger(__name__)


class GeneraFacturaCompEle(BaseDao):

    def get_clave_acceso(self, datos_factura, tipo_ambiente=ctes_facte.AMBIENTE_PRUEBAS):
        trn_fecreg = datos_factura['trn_fecreg']

        fechafact = fechas.format_cadena(trn_fecreg, ctes.APP_FMT_FECHA, ctes_facte.APP_FMT_FECHA_SRI)
        tipo_comprobante = '01'
        num_ruc = datos_factura['alm_ruc']

        # serie = '{0}{1}'.format(datos_factura['alm_numest'], datos_factura['tdv_numero'])

        trn_compro = datos_factura['trn_compro']
        serie_secuencial = trn_compro

        codigo_numerico = "00000000"  # potestad del contribuyente

        tipo_emision = "1"

        pre_clave_acceso = "{0}{1}{2}{3}{4}{5}{6}".format(fechafact, tipo_comprobante, num_ruc, tipo_ambiente,
                                                          serie_secuencial, codigo_numerico, tipo_emision)

        digito = self.get_digito_verificador(pre_clave_acceso)

        clave_acceso = '{0}{1}'.format(pre_clave_acceso, digito)
        return clave_acceso

    def get_digito_verificador(self, clave_acceso):

        factores = itertools.cycle((2, 3, 4, 5, 6, 7))
        suma = 0
        for digito, factor in zip(reversed(clave_acceso), factores):
            suma += int(digito) * factor
        control = 11 - suma % 11
        if control == 10:
            return 1
        elif control == 11:
            return 0
        else:
            return control

    def get_tipo_ident_comprador(self, per_codigo, per_ciruc):
        tipo_comprador = ctes_facte.TIPO_COMPRADOR_CONSFINAL
        per_ciruc = cadenas.strip(per_ciruc)
        if per_codigo == -1:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_CONSFINAL
        elif len(per_ciruc) == ctes_facte.LENGTH_CEDULA_ECU:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_CEDULA
        elif len(per_ciruc) == ctes_facte.LENGTH_RUC_ECU:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_RUC
        else:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_PASAPORTE

        return tipo_comprador

    def generar_factura(self, ambiente_value, datos_factura, datos_alm_matriz,
                        totales, detalles_db,
                        tipo_ambiente=ctes_facte.AMBIENTE_PRUEBAS,
                        tipo_emision_value=1):

        root = et.Element('factura')
        root.set("id", "comprobante")
        root.set("version", "1.0.0")

        info_tributaria = et.SubElement(root, "infoTributaria")
        ambiente = et.SubElement(info_tributaria, "ambiente")
        ambiente.text = str(ambiente_value)

        tipo_emision = et.SubElement(info_tributaria, "tipoEmision")
        tipo_emision.text = str(tipo_emision_value)

        razon_social = et.SubElement(info_tributaria, "razonSocial")
        razon_social.text = cadenas.strip(datos_factura['alm_razsoc'])

        nombre_comercial = et.SubElement(info_tributaria, "nombreComercial")
        nombre_comercial.text = cadenas.strip(datos_factura['alm_nomcomercial'])

        ruc = et.SubElement(info_tributaria, "ruc")
        ruc.text = cadenas.strip((datos_factura['alm_ruc']))

        clave_acceso_value = self.get_clave_acceso(datos_factura=datos_factura, tipo_ambiente=tipo_ambiente)
        clave_acceso = et.SubElement(info_tributaria, "claveAcceso")
        clave_acceso.text = clave_acceso_value

        cod_doc = et.SubElement(info_tributaria, "codDoc")
        cod_doc.text = ctes_facte.COD_DOC_FACTURA

        estab = et.SubElement(info_tributaria, "estab")
        estab.text = str(datos_factura['alm_numest'])

        pto_emi = et.SubElement(info_tributaria, "ptoEmi")
        pto_emi.text = str(datos_factura['tdv_numero'])

        secuencial = et.SubElement(info_tributaria, "secuencial")
        trn_compro = datos_factura['trn_compro']

        secuencial_value = trn_compro[6:]
        secuencial.text = secuencial_value

        alm_matriz_value = datos_alm_matriz['alm_direcc']

        dir_matriz = et.SubElement(info_tributaria, "dirMatriz")
        dir_matriz.text = alm_matriz_value

        info_factura = et.SubElement(root, "infoFactura")

        fecha_emision = et.SubElement(info_factura, "fechaEmision")
        fecha_emision.text = datos_factura['trn_fecreg']

        dir_establecimiento = et.SubElement(info_factura, "dirEstablecimiento")
        dir_establecimiento.text = datos_factura['alm_direcc']

        cnt_codigo = datos_alm_matriz['cnt_codigo']
        if cnt_codigo > 0:
            contribuyente_especial = et.SubElement(info_factura, "contribuyenteEspecial")
            contribuyente_especial.text = str(cnt_codigo)

        alm_contab = datos_alm_matriz['alm_contab']
        if alm_contab:
            obligado_contab = et.SubElement(info_factura, "obligadoContabilidad")
            obligado_contab.text = ctes_facte.SI

        tipoidentcomprador_value = self.get_tipo_ident_comprador(per_codigo=datos_factura['per_codigo'],
                                                                 per_ciruc=datos_factura['per_ciruc'])
        tipo_ident_comprador = et.SubElement(info_factura, "tipoIdentificacionComprador")
        tipo_ident_comprador.text = str(tipoidentcomprador_value)

        razon_social_comprador = et.SubElement(info_factura, "razonSocialComprador")
        razon_social_comprador.text = cadenas.strip_upper(datos_factura['per_nomapel'])

        identificacion_comprador = et.SubElement(info_factura, "identificacionComprador")
        identificacion_comprador.text = cadenas.strip(datos_factura['per_ciruc'])

        if cadenas.es_nonulo_novacio(datos_factura['per_direccion']):
            direccion_comprador = et.SubElement(info_factura, "direccionComprador")
            direccion_comprador.text = cadenas.strip(datos_factura['per_direccion'])

        total_sin_impuestos = et.SubElement(info_factura, "totalSinImpuestos")
        total_sin_impuestos.text = str(numeros.roundm2(totales['total_sin_impuesto']))

        total_descuento = et.SubElement(info_factura, "totalDescuento")
        total_descuento.text = str(numeros.roundm2(totales['total_descuentos']))

        total_con_impuestos = et.SubElement(info_factura, "totalConImpuestos")
        total_impuesto = et.SubElement(total_con_impuestos, "totalImpuesto")

        codigo_impuesto_item = et.SubElement(total_impuesto, "codigo")
        codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

        codigo_porcentaje = et.SubElement(total_impuesto, "codigoPorcentaje")
        codigo_porcentaje.text = ctes_facte.CODIGO_IVA_12

        base_imponible = et.SubElement(total_impuesto, "baseImponible")
        base_imponible.text = str(numeros.roundm2(totales['base_imp_iva_12']))

        valor_impuesto = et.SubElement(total_impuesto, "valor")
        valor_impuesto.text = str(numeros.roundm2(totales['impuesto_iva_12']))

        propina = et.SubElement(info_factura, "propina")
        propina.text = str(numeros.roundm2(datos_factura['propina']))

        importe_total_value = numeros.roundm2(totales['total'])
        importe_total = et.SubElement(info_factura, "importeTotal")
        importe_total.text = str(importe_total_value)

        moneda = et.SubElement(info_factura, "moneda")
        moneda.text = ctes_facte.MONEDA

        pagos = et.SubElement(info_factura, "pagos")

        # total_pago_efectivo_value = numeros.roundm2(totales['pago_efectivo'])
        # total_pago_credito_value = numeros.roundm2(totales['pago_credito'])

        pago_efectivo = et.SubElement(pagos, "pago")
        codigo_forma_pago_efec = et.SubElement(pago_efectivo, "formaPago")
        codigo_forma_pago_efec.text = ctes_facte.PAGO_SIN_UTILIZACION_SIS_FINANCIERO

        total_forma_pago_efec = et.SubElement(pago_efectivo, "total")
        total_forma_pago_efec.text = str(importe_total_value)

        #TODO: En esta caso se debe agregar tambien las etiquetes de plazo y unidad de tiempo, por el momento solo se deja el pago sin utilizacion del sistema financiero
        """
        if total_pago_credito_value > 0:
            pago_credito = et.SubElement(pagos, "pago")
            codigo_forma_pago_cre = et.SubElement(pago_credito, "formaPago")
            codigo_forma_pago_cre.text = ctes_facte.PAGO_OTROS_SIN_UTILIZACION

            total_forma_pago_cre = et.SubElement(pago_credito, "total")
            total_forma_pago_cre.text = str(total_pago_credito_value)
        """

        detalles = et.SubElement(root, "detalles")

        for detalle_db in detalles_db:
            detalle_item = et.SubElement(detalles, "detalle")

            codigo_principal_item = et.SubElement(detalle_item, "codigoPrincipal")
            codigo_principal_item.text = cadenas.strip(detalle_db['ic_code'])

            descripcion_item = et.SubElement(detalle_item, "descripcion")
            descripcion_item.text = cadenas.strip_upper(detalle_db['ic_nombre'])

            cantidad_item = et.SubElement(detalle_item, "cantidad")
            cantidad_item.text = str(numeros.roundm2(detalle_db['dt_cant']))

            precio_unitario_item = et.SubElement(detalle_item, "precioUnitario")
            precio_unitario_item.text = str(numeros.roundm2(detalle_db['dt_precio']))

            descuento_item = et.SubElement(detalle_item, "descuento")
            descuento_item.text = str(numeros.roundm2(detalle_db['dt_decto']))

            precio_total_sin_impuesto_item = et.SubElement(detalle_item, "precioTotalSinImpuesto")
            precio_total_sin_impuesto_item.text = str(numeros.roundm2(detalle_db['subtotal']))

            impuestos = et.SubElement(detalle_item, "impuestos")
            impuesto_item = et.SubElement(impuestos, "impuesto")

            codigo_impuesto_item = et.SubElement(impuesto_item, "codigo")
            codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

            dt_cant = detalle_db['dt_cant']
            dai_impg = detalle_db['dai_impg']
            dai_impg_mult = numeros.roundm2(dai_impg * 100)
            dt_decto = detalle_db['dt_decto']
            dt_decto_cant = dt_decto * dt_cant
            if detalle_db['dt_valdto'] >= 0.0:
                dt_decto_cant = dt_decto
            dt_dectogen = detalle_db['dt_dectogen']
            dt_precio = detalle_db['dt_precio']
            subtforiva = (dt_cant * dt_precio) - (dt_decto_cant + dt_dectogen)

            # subt = (detalle_db['dt_cant'] * detalle_db['dt_precio']) - detalle_db['dt_valdto']

            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_12
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = str(dai_impg_mult)
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = str(numeros.roundm2(ivaval))
            else:
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_CERO
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = "0.00"
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = "0.00"

        xml_str = et.tostring(root, encoding='utf8').decode('utf8')

        return {
            'clave': clave_acceso_value,
            'xml': xml_str
        }
        # return xml_str
