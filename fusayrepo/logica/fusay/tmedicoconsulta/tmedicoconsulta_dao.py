# coding: utf-8
"""
Fecha de creacion: 09/04/2025
@autor: mjapon
"""
import datetime
import logging
from collections import defaultdict

import pandas as pd

from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tmedicoconsulta.tmedicoconsulta_model import TMedicoConsulta
from fusayrepo.utils import fechas

log = logging.getLogger(__name__)


def analizar_consultas_conjuntas(df):
    # Primero identificamos las consultas con múltiples médicos
    consultas_multi_medico = {}

    # Agrupamos por cosm_id
    for cosm_id, grupo in df.groupby("cosm_id"):
        # Obtenemos los médicos únicos en esta consulta
        medicos = grupo["med_id"].unique().tolist()

        # Si hay más de un médico, guardamos esta consulta como conjunta
        if len(medicos) > 1:
            consultas_multi_medico[cosm_id] = medicos

    # Ahora agrupamos por combinaciones de médicos
    grupos_medicos = defaultdict(list)

    for cosm_id, medicos in consultas_multi_medico.items():
        # Creamos una clave ordenada de médicos (tupla)
        medicos_key = tuple(sorted(medicos))
        # Añadimos esta consulta al grupo de estos médicos
        grupos_medicos[medicos_key].append(cosm_id)

    # Formateamos el resultado como lista de diccionarios según la estructura solicitada
    resultados = []
    for medicos, consultas in grupos_medicos.items():
        resultados.append({
            "medicos": list(medicos),
            "consultas": sorted(consultas),
            "tipo": 1,
            "cantidad": len(consultas)
        })

    return resultados


def analizar_consultas_unitarias(df):
    # Agrupamos por médico para encontrar sus consultas unitarias
    consultas_por_medico = defaultdict(list)

    # Primero identificamos las consultas con un solo médico
    consultas_unitarias = {}

    for cosm_id, grupo in df.groupby("cosm_id"):
        # Obtenemos los médicos únicos en esta consulta
        medicos = grupo["med_id"].unique()

        # Si hay un solo médico, guardamos esta consulta como unitaria
        if len(medicos) == 1:
            consultas_unitarias[cosm_id] = medicos[0]

    # Agrupamos estas consultas unitarias por médico
    for cosm_id, medico in consultas_unitarias.items():
        consultas_por_medico[medico].append(cosm_id)

    # Formateamos el resultado como lista de diccionarios
    resultados = []
    for medico, consultas in consultas_por_medico.items():
        resultados.append({
            "medicos": [int(medico)],
            "tipo": 2,
            "cantidad": len(consultas),
            "consultas": sorted(consultas)
        })

    return resultados


class TMedicoConsultaDao(BaseDao):

    def crear_medico_consulta(self, cosm_id, med_id, usercrea):
        medicoconsulta = TMedicoConsulta()
        medicoconsulta.cosm_id = cosm_id
        medicoconsulta.med_id = med_id
        medicoconsulta.fecharegistro = datetime.datetime.now()
        medicoconsulta.usercrea = usercrea

        self.dbsession.add(medicoconsulta)
        self.dbsession.flush()

        return medicoconsulta.cosmed_id

    def obtener_medico_consulta(self, cosmed_id):
        return self.dbsession.query(TMedicoConsulta).filter(TMedicoConsulta.cosmed_id == cosmed_id).first()

    def get_medicos_consulta(self, cosmed_id):
        sql = f"select med_id from tmedicoconsulta where cosm_id = {cosmed_id}"
        tupla_desc = ('med_id',)
        return self.all(sql, tupla_desc)

    def actualizar_medico_consulta(self, cosmed_id, **kwargs):
        medicoconsulta = self.obtener_medico_consulta(cosmed_id)
        if medicoconsulta:
            for key, value in kwargs.items():
                setattr(medicoconsulta, key, value)
            self.dbsession.flush()
            return True
        return False

    def eliminar_medico_consulta(self, cosmed_id):
        medicoconsulta = self.obtener_medico_consulta(cosmed_id)
        if medicoconsulta:
            self.dbsession.delete(medicoconsulta)
            self.dbsession.flush()
            return True
        return False

    def find_consultas(self, desde, hasta):
        desde_db = fechas.format_cadena_db(desde)
        hasta_db = fechas.format_cadena_db(hasta)

        sql = f"""
        select cosm.cosm_id, medc.med_id, med.per_id, per.per_nombres||' '||coalesce(per.per_apellidos,'') as medico, 
        per.per_ciruc from tmedicoconsulta medc
        join tconsultamedica cosm on medc.cosm_id  = cosm.cosm_id 
        join tmedico med on medc.med_id  = med.med_id
        join tpersona per on med.per_id  = per.per_id
        where cosm.cosm_estado  = 1 and date(cosm.cosm_fechacrea) between '{desde_db}' and '{hasta_db}' order by cosm.cosm_id 
        """

        resultados = self.all_raw(sql)

        df = pd.DataFrame(resultados, columns=["cosm_id", "med_id", "per_id", "medico", "per_ciruc"])

        consultas_conjuntas = analizar_consultas_conjuntas(df)
        consultas_unitarias = analizar_consultas_unitarias(df)
        return {
            'conjuntas': consultas_conjuntas,
            'unitarias': consultas_unitarias
        }

    def find_detalles_atenciones(self, lista_id_consultas):

        ids = ",".join(map(str, lista_id_consultas))
        sql = f"""
        select cm.cosm_id, cm.cosm_fechacrea, cm.cosm_motivo, 
            pac.per_nombres||' '||coalesce(pac.per_apellidos,'') as paciente, pac.per_ciruc, pac.per_direccion, 
            get_medicos(cm.cosm_id) as medicos
            from tconsultamedica cm
            join tpersona pac on cm.pac_id  = pac.per_id 
            where cm.cosm_estado = 1 and cosm_id in ({ids})
        """

        tupla_desc = ('cosm_id', 'cosm_fechacrea', 'cosm_motivo', 'paciente', 'per_ciruc', 'per_direccion', 'medicos')
        return self.all(sql, tupla_desc)
