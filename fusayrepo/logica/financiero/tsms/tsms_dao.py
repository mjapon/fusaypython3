# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.financiero.tsms.tsms_model import TFinSms

log = logging.getLogger(__name__)


class TSmsDao(BaseDao):

    def crear(self, form):

        error_code = None
        error_message = None

        if form['error_code'] is not None:
            error_code = form['error_code'][:40]

        if form['error_message'] is not None:
            error_message = form['error_message'][:100]

        tsms = TFinSms()
        tsms.sms_status = form['status'][:40]
        tsms.sms_error_code = error_code
        tsms.sms_error_message = error_message
        tsms.sms_phone = form['phone']
        tsms.sms_message = form['message'][:500]
        tsms.sms_fecha_creacion = datetime.datetime.now()
        tsms.sms_external_id = form['id'][:50]

        self.dbsession.add(tsms)
        self.dbsession.flush()
