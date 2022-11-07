# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from suds.client import Client

from fusayrepo.logica.dao.base import BaseDao

log = logging.getLogger(__name__)


class ProxyClient(BaseDao):
    url_proxy_client = "http://localhost:9090/proxy?wsdl"

    def get_soap_client(self):
        client = Client(self.url_proxy_client)
        print(client)
        return client

    def enviar_comprobante(self, claveacceso, comprobante, ambiente, info_adicional="", reenvio=0,
                           ruc_empresa=""):
        client = self.get_soap_client()
        res = client.service.validarComprobante(claveacceso, comprobante, ambiente, info_adicional, reenvio,
                                                ruc_empresa)
        return res

    def consulta_autorizacion(self, claveacceso, ambiente, info_adicional="", ruc_empresa=""):
        client = self.get_soap_client()
        res = client.service.autorizarComprobante(claveacceso, ambiente, info_adicional, ruc_empresa)
        print(res)
        print(type(res))

        return res
