# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from fusayrepo.logica.compele.gen_data import GenDataForFacte
from fusayrepo.logica.compele.gen_xml import GeneraFacturaCompEle
from fusayrepo.logica.compele.proxy import ProxyClient
from fusayrepo.logica.compele.redisclient import RedisPublisher
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.talmacen.talmacen_dao import TAlmacenDao
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao
from fusayrepo.utils import ctes
from fusayrepo.utils.jsonutil import SimpleJsonUtil

log = logging.getLogger(__name__)


class CompeleUtilDao(BaseDao):

    def __init__(self, dbsession):
        super(CompeleUtilDao, self).__init__(dbsession)
        self.redispublis = RedisPublisher()
        self.myjsonutil = SimpleJsonUtil()

    def get_ambiente(self):
        almdao = TAlmacenDao(self.dbsession)
        return almdao.get_alm_tipoamb()

    def autorizar(self, trn_codigo, emp_codigo, emp_esquema):
        try:
            message = {
                "emp_codigo": emp_codigo,
                "emp_esquema": emp_esquema,
                "trn_codigo": trn_codigo,
                "accion": "autoriza"
            }

            str_message = self.myjsonutil.dumps(message)
            self.redispublis.publish_message(str_message)

        except Exception as ex:
            log.error("Error al tratar de enviar mensaje a la cola de comprobantes electronicos", ex)

    def registra_comprob_contrib(self, trn_codigo, emp_codigo, estado_envio, sec_id):
        gen_fact = GeneraFacturaCompEle(self.dbsession)
        gen_data = GenDataForFacte(self.dbsession)
        datos_fact = gen_data.get_factura_data(trn_codigo=trn_codigo)
        datos_alm_matriz = gen_data.get_datos_alm_matriz(sec_codigo=sec_id)
        ambiente_facte = datos_alm_matriz['alm_tipoamb']

        claveacceso = gen_fact.get_clave_acceso(datos_factura=datos_fact['cabecera'], tipo_ambiente=ambiente_facte)

        gen_data.save_contrib_and_compro(datosfact=datos_fact['cabecera'],
                                         claveacceso=claveacceso,
                                         trn_cod=trn_codigo,
                                         emp_codigo=emp_codigo,
                                         total_fact=datos_fact['totales']['total'],
                                         estado_envio=estado_envio,
                                         ambiente=ambiente_facte)
        return {'status': 200, 'exito': True}

    def logica_check_envio_factura(self, trn_codigo):
        sql = """
        select per_codigo, sec_codigo, tra_codigo from tasiento where trn_codigo = {0}
        """.format(trn_codigo)

        tupla_desc = ('per_codigo', 'sec_codigo', 'tra_codigo')
        datosfact = self.first(sql, tupla_desc)

        sec_id = datosfact['sec_codigo']
        sec_tipoamb = 0
        aplica_facte_por_seccion = False
        tseccion_dao = TSeccionDao(self.dbsession)
        talm_dao = TAlmacenDao(self.dbsession)
        if sec_id is not None and int(sec_id) > 1:
            sec_tipoamb = tseccion_dao.get_sec_tipoamb(sec_id=sec_id)
            aplica_facte_por_seccion = sec_tipoamb > 0

        alm_tipoamb = 0
        if not aplica_facte_por_seccion:
            alm_tipoamb = talm_dao.get_alm_tipoamb()

        compelenviado = False
        estado_envio = 0
        is_cons_final = False
        creando = True
        tra_codigo = datosfact['tra_codigo']
        per_id_asiento = datosfact['per_codigo']
        if (alm_tipoamb > 0 or sec_tipoamb > 0) and creando and tra_codigo == ctes.TRA_COD_FACT_VENTA:
            log.info("Configurado facturacion se envia su generacion--trn_codigo:{0}".format(trn_codigo))
            response_compele = {'enviado': False, 'estado_envio': 4}
            try:
                response_compele = self.enviar(trn_codigo=trn_codigo, sec_codigo=sec_id)
            except Exception as ex:
                log.error("Error al tratar de enviar el comprobante al sri", ex)
            compelenviado = response_compele['enviado']
            estado_envio = response_compele['estado_envio']
            is_cons_final = per_id_asiento < 0

        return {'is_cons_final': is_cons_final, 'compelenviado': compelenviado, 'estado_envio': estado_envio,
                'trn_codigo': trn_codigo}

    def enviar(self, trn_codigo, sec_codigo):
        gen_fact = GeneraFacturaCompEle(self.dbsession)

        gen_data = GenDataForFacte(self.dbsession)
        datos_fact = gen_data.get_factura_data(trn_codigo=trn_codigo)
        datos_alm_matriz = gen_data.get_datos_alm_matriz(sec_codigo=sec_codigo)

        ambiente_facte = datos_alm_matriz['alm_tipoamb']

        xml_facte = gen_fact.generar_factura(ambiente_value=ambiente_facte,
                                             datos_factura=datos_fact['cabecera'],
                                             datos_alm_matriz=datos_alm_matriz,
                                             totales=datos_fact['totales'],
                                             detalles_db=datos_fact['detalles']
                                             )

        claveacceso = xml_facte['clave']
        alm_ruc = datos_fact['cabecera']['alm_ruc']

        client_proxy = ProxyClient(self.dbsession)

        proxy_response = None
        try:
            proxy_response = client_proxy.enviar_comprobante(claveacceso=claveacceso, comprobante=xml_facte['xml'],
                                                             ambiente=ambiente_facte, ruc_empresa=alm_ruc)
        except Exception as ex:
            log.error("Error al tratar de enviar el comprobante al sri", ex)

        enviado = False
        estado_envio = 4  # Sin transmitir
        if proxy_response is not None:
            proxy_response['numeroAutorizacion'] = claveacceso
            if proxy_response['claveAcceso'] is None:
                proxy_response['claveAcceso'] = claveacceso

            estado_envio = proxy_response['estado']
            gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=ambiente_facte,
                                              proxy_response=proxy_response)
            enviado = True
        else:
            gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=ambiente_facte,
                                              proxy_response={
                                                  'estado': 4,
                                                  'estadoSRI': '',
                                                  'fechaAutorizacion': '',
                                                  'mensajes': '',
                                                  'numeroAutorizacion': claveacceso,
                                                  'claveAcceso': claveacceso
                                              })

        """
        try:
            message = {
                "emp_codigo": emp_codigo,
                "emp_esquema": emp_esquema,
                "trn_codigo": trn_codigo,
                "clave_acceso": claveacceso
            }

            str_message = self.myjsonutil.dumps(message)
            self.redispublis.publish_message(str_message)

        except Exception as ex:
            log.error("Error al tratar de enviar mensaje a la cola de comprobantes electronicos", ex)
        """

        return {'status': 200, 'exito': True, 'enviado': enviado, 'proxyresponse': proxy_response,
                'estado_envio': estado_envio}
