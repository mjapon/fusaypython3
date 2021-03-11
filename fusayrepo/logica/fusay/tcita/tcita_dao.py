# coding: utf-8
"""
Fecha de creacion 12/9/20
@autor: mjapon
"""
import logging
from datetime import datetime

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tcita.tcita_model import TCita
from fusayrepo.logica.fusay.ttipocita.ttipocita_dao import TTipoCitaDao
from fusayrepo.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TCitaDao(BaseDao):

    def listar_citas_paciente(self, pac_id):
        sql = u"""
                select cita.ct_id, cita.ct_fecha, cita.ct_hora, cita.ct_hora_fin,cita.pac_id, cita.ct_obs, cita.med_id, cita.ct_serv,
                cita.ct_estado,
                case cita.ct_estado 
                when 0 then 'Pendiente'
                when 1 then 'Atendido'
                when 2 then 'Cancelado'
                else ''
                end as estado,
                medico.per_nombres ||' '|| medico.per_apellidos as nombres_medico 
                from tcita cita
                join tpersona medico on medico.per_id = cita.med_id
                where cita.pac_id = {0} order by ct_fecha, ct_hora asc   
                """.format(pac_id)
        tupla_desc = (
            'ct_id', 'ct_fecha', 'ct_hora', 'ct_hora_fin', 'pac_id', 'ct_obs', 'med_id', 'ct_serv',
            'ct_estado', 'estado', 'nombres_medico'
        )

        citas = self.all(sql, tupla_desc)
        for cita in citas:
            ct_fecha = cita['ct_fecha']
            ct_hora = cita['ct_hora']
            ct_hora_fin = cita['ct_hora_fin']
            ct_hora_str = fechas.num_to_hora(ct_hora)
            ct_fecha_str = fechas.get_fecha_letras_largo(fechas.parse_cadena(ct_fecha))
            ct_hora_fin_str = fechas.num_to_hora(ct_hora_fin)
            cita['ct_fecha_str'] = ct_fecha_str
            cita['ct_hora_str'] = ct_hora_str
            cita['ct_hora_fin_str'] = ct_hora_fin_str

        return citas

    def get_form(self, pac_id):
        return {
            'ct_id': 0,
            'ct_fecha': fechas.get_str_fecha_actual(),
            'pac_id': pac_id,
            'ct_obs': '',
            'med_id': 0,
            'ct_serv': 0,
            'ct_hora': 0.0,
            'ct_hora_fin': 0.0,
            'ct_estado': 0,
            'ct_td': False,
            'ct_color': '#1175f7',
            'ct_titulo': '',
            'ct_tipo': 1
        }

    def get_new_hora(self, horanum):
        return {
            'label': fechas.num_to_hora(horanum),
            'value': horanum
        }

    def get_horas_for_form(self, tipocita):
        tipcitadao = TTipoCitaDao(self.dbsession)
        datostipocita = tipcitadao.get_datos_tipo(tipc_id=tipocita)
        step = 0.25
        cstart = 8.0
        cend = 19.0

        if datostipocita is not None:
            cstart = datostipocita['tipc_calini']
            cend = datostipocita['tipc_calfin']

        horas = []
        for i in range(int(cstart), int(cend)):
            if i == int(cend) - 1:
                for j in range(0, 5):
                    horas.append(self.get_new_hora(horanum=i + (j * step)))
            else:
                for j in range(4):
                    horas.append(self.get_new_hora(horanum=i + (j * step)))
        return horas

    def get_detalles_cita(self, ct_id):
        sql = """
        select a.ct_id, date(a.ct_fecha) as ct_fecha, a.ct_hora, a.ct_hora_fin, coalesce(a.pac_id,0) as pac_id, a.ct_obs, a.med_id, a.ct_titulo,
               per.per_nombres||' '||per.per_apellidos as paciente, per.per_ciruc as ciruc_pac,
               med.per_nombres||' '||med.per_apellidos as medico, med.per_ciruc as ciruc_med, 
        a.ct_color, a.ct_fechacrea, a.user_crea, a.ct_estado, a.ct_tipo  
        from tcita a 
        left join tpersona per on a.pac_id = per.per_id
        left join tpersona med on a.med_id = med.per_id
        where a.ct_id = {0}
        """.format(ct_id)

        tupla_desc = (
            'ct_id', 'ct_fecha', 'ct_hora', 'ct_hora_fin', 'pac_id', 'ct_obs', 'med_id', 'ct_titulo', 'paciente',
            'ciruc_pac', 'medico', 'ciruc_med', 'ct_color', 'ct_fechacrea', 'user_crea', 'ct_estado', 'ct_tipo')
        res = self.first(sql, tupla_desc)
        if res is not None:
            res['ct_hora_str'] = fechas.num_to_hora(res['ct_hora'])
            res['ct_hora_fin_str'] = fechas.num_to_hora(res['ct_hora_fin'])

        return res

    def get_lista_colores(self):
        return [{'colora': '#C85632',
                 'colorb': '#E14747'},
                {'colora': '#7986CB',
                 'colorb': '#039BE5'},
                {'colora': '#3CA574',
                 'colorb': '#C9C9C9'},
                {'colora': '#CE7770',
                 'colorb': '#F6BF26'},
                {'colora': '#1A7A48',
                 'colorb': '#6E759B'},
                {'colora': '#882CA1',
                 'colorb': '#C53836'}]

    def find_by_id(self, ct_id):
        return self.dbsession.query(TCita).filter(TCita.ct_id == ct_id).first()

    def anular(self, ct_id):
        tcita = self.find_by_id(ct_id)
        if tcita is not None:
            tcita.ct_estado = 2
            # TODO: Agregar informacion de anulaciom, usuario, fecha, observacion
            self.dbsession.add(tcita)

    def guardar(self, form, user_crea):
        tcita = TCita()

        tcita.ct_fecha = fechas.parse_cadena(form['ct_fecha'])
        tcita.pac_id = form['pac_id']
        tcita.ct_obs = cadenas.strip(form['ct_obs'])
        tcita.med_id = form['med_id']

        if isinstance(form['ct_hora'], dict):
            tcita.ct_hora = form['ct_hora']['value']
        else:
            tcita.ct_hora = form['ct_hora']

        if isinstance(form['ct_hora_fin'], dict):
            tcita.ct_hora_fin = form['ct_hora_fin']['value']
        else:
            tcita.ct_hora_fin = form['ct_hora_fin']

        tcita.ct_estado = 0
        tcita.user_crea = user_crea
        tcita.ct_fechacrea = datetime.now()
        tcita.ct_td = form['ct_td']
        tcita.ct_color = form['ct_color']
        tcita.ct_titulo = cadenas.strip(form['ct_titulo'])
        if 'ct_tipo' in form:
            tcita.ct_tipo = form['ct_tipo']
        else:
            tcita.ct_tipo = 2  # 1-medico, 2:odontologo

        self.dbsession.add(tcita)

    def actualizar(self, form, user_edita):
        ct_id = form['ct_id']
        tcita = self.find_by_id(ct_id)
        if tcita is not None:
            tcita.ct_fecha = fechas.parse_cadena(form['ct_fecha'])
            tcita.ct_obs = cadenas.strip(form['ct_obs'])
            if isinstance(form['ct_hora'], dict):
                tcita.ct_hora = form['ct_hora']['value']
            else:
                tcita.ct_hora = form['ct_hora']

            if isinstance(form['ct_hora_fin'], dict):
                tcita.ct_hora_fin = form['ct_hora_fin']['value']
            else:
                tcita.ct_hora_fin = form['ct_hora_fin']

            tcita.ct_color = form['ct_color']
            tcita.ct_titulo = cadenas.strip(form['ct_titulo'])

            self.dbsession.add(tcita)

    """
    def crear(self, form):
        celular = form['celular']
        serv_id = form['serv_id']
        med_id = form['med_id']
        dia = form['dia']
        hora_ini = form['hora_ini']
        up_celular = cadenas.strip_upper(celular)
        up_email = form['up_email']
        aux_paciente = self.buscar_por_email(up_email)
        if aux_paciente is None:
            raise ErrorValidacionExc(u'No esta registrado la dirección de correo')
        else:
            pac_id = aux_paciente.up_id
            # aux_paciente.up_nombres = up_nombres
            if cadenas.es_nonulo_novacio(up_celular):
                aux_paciente.up_celular = up_celular
            # aux_paciente.up_photourl = photo_url
            self.dbsession.add(aux_paciente)

        # Se procede a crear la cita
        tcita = TCita()

        hora_ini_num = fechas.hora_to_num(hora_ini)
        tcita.ct_hora = hora_ini_num
        tcita.ct_fecha = fechas.parse_cadena(dia)
        tcita.ct_hora_fin = hora_ini_num + 1
        tcita.ct_serv = serv_id
        tcita.med_id = med_id
        tcita.pac_id = pac_id
        tcita.ct_estado = 0

        self.dbsession.add(tcita)
    """

    def listar_validos(self, desde, hasta, ct_tipo=1):
        sql = """
        select a.ct_id, date(a.ct_fecha) as ct_fecha, a.ct_hora, a.ct_hora_fin, a.pac_id, a.ct_obs, a.med_id, a.ct_titulo,
               per.per_nombres, per.per_apellidos, per.per_ciruc,
        a.ct_color, a.ct_fechacrea, a.user_crea from tcita a left join  tpersona per on
        a.pac_id = per.per_id where a.ct_estado in (0,1) and a.ct_tipo ={2} and  date(a.ct_fecha) between '{0}' and '{1}' order by a.ct_fecha
        """.format(fechas.format_cadena_db(desde), fechas.format_cadena_db(hasta), ct_tipo)
        tupla_desc = ('ct_id',
                      'ct_fecha',
                      'ct_hora',
                      'ct_hora_fin',
                      'pac_id',
                      'ct_obs',
                      'med_id',
                      'ct_titulo',
                      'per_nombres',
                      'per_apellidos',
                      'per_ciruc',
                      'ct_color', 'ct_fechacrea', 'user_crea')
        return self.all(sql, tupla_desc)

    def contar_validos(self, desde, hasta, ct_tipo=1):
        sql = """        
        select count(*) as cuenta, date(a.ct_fecha) as ct_fecha  from tcita a where a.ct_estado in (0,1) and a.ct_tipo={2} and date(a.ct_fecha) between '{0}' and '{1}'
            group by 2 order by 2
                """.format(fechas.format_cadena_db(desde), fechas.format_cadena_db(hasta), ct_tipo)
        tupla_desc = ('cuenta',
                      'ct_fecha')
        return self.all(sql, tupla_desc)

    def listar_citas(self, med_id, fecha_desde):
        sql_fecha = ''
        if fecha_desde is not None and len(fecha_desde) > 0:
            fecha_db = fechas.format_cadena_db(fecha_desde)
            sql_fecha = "and ct_fecha >= '{fecha}'".format(fecha=fecha_db)

        sql = u"""
                select cita.ct_id, cita.ct_fecha, cita.ct_hora, cita.ct_hora_fin,cita.pac_id, cita.ct_obs, cita.med_id, cita.ct_serv,
                cita.ct_estado,
                case cita.ct_estado 
                when 0 then 'Pendiente'
                when 1 then 'Atendido'
                when 2 then 'Cancelado'
                else ''
                end as estado
                from tcita cita
                where med_id = {0} {1} order by ct_fecha, ct_hora asc   
                """.format(med_id, sql_fecha)

        tupla_desc = (
            'ct_id', 'ct_fecha', 'ct_hora', 'ct_hora_fin', 'pac_id', 'ct_obs', 'med_id', 'ct_serv',
            'ct_estado', 'estado'
        )

        citas = self.all(sql, tupla_desc)
        for cita in citas:
            ct_fecha = cita['ct_fecha']
            ct_hora = cita['ct_hora']
            ct_hora_fin = cita['ct_hora_fin']
            ct_hora_str = fechas.num_to_hora(ct_hora)
            ct_fecha_str = fechas.get_fecha_letras_largo(fechas.parse_cadena(ct_fecha))
            ct_hora_fin_str = fechas.num_to_hora(ct_hora_fin)
            cita['ct_fecha_str'] = ct_fecha_str
            cita['ct_hora_str'] = ct_hora_str
            cita['ct_hora_fin_str'] = ct_hora_fin_str

        return citas

    def buscar_citas(self, med_id, serv_id, fecha_desde):
        """
        Busca un registro de cita
        :param med_id:
        :param serv_id:
        :return:
        """
        fecha_db = fechas.format_cadena_db(fecha_desde)

        sql = """
        select ct_id, ct_fecha, ct_hora, ct_hora_fin,pac_id, ct_obs, med_id, ct_serv
        from tcita where med_id = {0} and ct_serv = {1} and ct_fecha >= '{2}' order by ct_fecha, ct_hora asc   
        """.format(med_id, serv_id, fecha_db)

        tupla_desc = (
            'ct_id', 'ct_fecha', 'ct_hora', 'ct_hora_fin', 'pac_id', 'ct_obs', 'med_id', 'ct_serv')

        citas = self.all(sql, tupla_desc)
        for cita in citas:
            ct_fecha = cita['ct_fecha']
            ct_hora = cita['ct_hora']
            ct_hora_fin = cita['ct_hora_fin']
            ct_hora_str = fechas.num_to_hora(ct_hora)
            ct_fecha_str = fechas.get_fecha_letras_largo(fechas.parse_cadena(ct_fecha))
            ct_hora_fin_str = fechas.num_to_hora(ct_hora_fin)
            cita['ct_fecha_str'] = ct_fecha_str
            cita['ct_hora_str'] = ct_hora_str
            cita['ct_hora_fin_str'] = ct_hora_fin_str

    def get_horario_medico(self, med_id):
        sql = "select  hm_id, med_id, hm_dia, hm_horaini,hm_horafin  from thorariomedico where med_id={0} order by hm_dia, hm_horaini".format(
            med_id)

        tupla_desc = ('hm_id', 'med_id', 'hm_dia', 'hm_horaini', 'hm_horafin')
        return self.all(sql, tupla_desc)

    def get_matriz_horas_medico(self, med_id, dia):
        dia_parsed = fechas.parse_cadena(dia)
        weekday = dia_parsed.isoweekday()

        dia_db = fechas.format_cadena_db(dia)

        sql = """
        select hm.hm_id, hm.med_id, hm.hm_dia, hm.hm_horaini,hm.hm_horafin,
        coalesce(cita.ct_hora, 0) as ct_hora,  
        coalesce(cita.pac_id, 0) as pac_id
         from thorariomedico hm
        left join tcita cita on cita.med_id = {medico} and cita.ct_fecha = '{fecha}' 
        where hm.med_id={medico} and hm.hm_dia = {weekday} order by hm.hm_horaini asc        
        """.format(medico=med_id, fecha=dia_db, weekday=weekday)

        tupla_desc = ('hm_id', 'med_id', 'hm_dia', 'hm_horaini', 'hm_horafin', 'ct_hora', 'pac_id')
        res = self.all(sql, tupla_desc)

        horas = []
        setHorasOcupadas = set()

        for item in res:
            ct_hora = item['ct_hora']
            if ct_hora != 0:
                setHorasOcupadas.add(ct_hora)

        if res is not None:
            first_row = res[0]
            hm_horaini = first_row['hm_horaini']
            hm_horafin = first_row['hm_horafin']

            hora_iter = hm_horaini
            while hora_iter < hm_horafin:
                horaiter_fin = hora_iter + 1
                ocupado = 1 if hora_iter in setHorasOcupadas else 0
                hora_iter_str = fechas.num_to_hora(hora_iter)
                horaiter_fin_str = fechas.num_to_hora(horaiter_fin)
                horas.append({'horaIni': hora_iter_str, 'horaFin': horaiter_fin_str, 'ocupado': ocupado})
                hora_iter = horaiter_fin

        return horas

    def cambiar_estado_cita(self, ct_id, estado, observacion):

        tcita = self.dbsession.query(TCita).filter(TCita.ct_id == ct_id).first()
        if tcita is not None:
            tcita.ct_estado = estado
            tcita.ct_obs = observacion
            self.dbsession.add(tcita)

    def get_last_valid_cita(self, per_id, ct_tipo):
        sql = """
        select ct_id, ct_fecha, pac_id, ct_obs, med_id, ct_serv, ct_hora, ct_hora_fin, ct_estado,
        user_crea, ct_fechacrea, ct_td, ct_color, ct_titulo, ct_tipo from tcita where pac_id = {0} and 
        ct_tipo = {1} and ct_estado != 2
        """.format(per_id, ct_tipo)

        tupla_desc = ('ct_id', 'ct_fecha', 'pac_id', 'ct_obs', 'med_id', 'ct_serv', 'ct_hora', 'ct_hora_fin',
                      'ct_estado', 'user_crea', 'ct_fechacrea', 'ct_td', 'ct_color', 'ct_titulo', 'ct_tipo')

        return self.first(sql, tupla_desc)

    def get_prox_valid_cita(self, per_id, ct_tipo, ct_fecha):
        ct_fecha_db = fechas.format_cadena_db(ct_fecha)
        sql = """
                select ct_id, ct_fecha, pac_id, ct_obs, med_id, ct_serv, ct_hora, ct_hora_fin, ct_estado,
                user_crea, ct_fechacrea, ct_td, ct_color, ct_titulo, ct_tipo from tcita where pac_id = {0} and 
                ct_tipo = {1} and ct_estado != 2 and ct_fecha>='{2}'
                """.format(per_id, ct_tipo, ct_fecha_db)

        tupla_desc = ('ct_id', 'ct_fecha', 'pac_id', 'ct_obs', 'med_id', 'ct_serv', 'ct_hora', 'ct_hora_fin',
                      'ct_estado', 'user_crea', 'ct_fechacrea', 'ct_td', 'ct_color', 'ct_titulo', 'ct_tipo')

        return self.first(sql, tupla_desc)
