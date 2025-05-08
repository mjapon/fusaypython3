# coding: utf-8
"""
Fecha de creacion: 09/04/2025
@autor: mjapon
Mejorado: 07/05/2025
"""
from typing import Dict, List, Any
from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tmedicoconsulta.tmedicoconsulta_dao import TMedicoConsultaDao
from fusayrepo.logica.fusay.tpersona.tpersona_dao import TPersonaDao


def _inicializar_estadisticas_vacias(medico: Dict[str, Any]) -> None:
    """
    Inicializa estadísticas vacías para un médico

    Args:
        medico: Diccionario con información del médico
    """
    medico.update({
        'nconjuntas': 0,
        'nunitarias': 0,
        'ntotal_consultas': 0,
        'cons_conjuntas': [],
        'cons_unitarias': []
    })


def _agregar_estadisticas_medico(
        medico: Dict[str, Any],
        consultas_conjuntas: List[Dict[str, Any]],
        consultas_unitarias: List[Dict[str, Any]]) -> None:
    """
    Agrega estadísticas de consultas conjuntas y unitarias a un médico

    Args:
        medico: Diccionario con información del médico
        consultas_conjuntas: Lista de consultas con múltiples médicos
        consultas_unitarias: Lista de consultas con un solo médico
    """
    med_id = medico.get('med_id')
    if not med_id:
        # Si no hay ID de médico, no podemos procesar estadísticas
        _inicializar_estadisticas_vacias(medico)
        return

    # Inicializamos conjuntos para almacenar IDs de consultas únicas
    ids_consultas_conjuntas = set()
    ids_consultas_unitarias = set()

    # Contador de grupos de atención conjunta donde participa este médico
    count_grupos_conjuntos = 0

    # Procesamos consultas conjuntas
    for consulta_conj in consultas_conjuntas:
        medicos_ids = consulta_conj.get('medicos', [])

        if med_id in medicos_ids:
            count_grupos_conjuntos += 1
            # Agregamos todas las consultas asociadas a este grupo
            ids_consultas_conjuntas.update(consulta_conj.get('consultas', []))

    count_unitarios = 0
    # Procesamos consultas unitarias
    for consulta_unit in consultas_unitarias:
        medicos_ids = consulta_unit.get('medicos', [])

        if med_id in medicos_ids:
            count_unitarios += 1
            # Agregamos todas las consultas asociadas a este grupo
            ids_consultas_unitarias.update(consulta_unit.get('consultas', []))

    # Actualizamos el diccionario del médico con las estadísticas
    medico.update({
        'nconjuntas': len(list(ids_consultas_conjuntas)),
        'nunitarias': len(list(ids_consultas_unitarias)),
        'ntotal_consultas': len(ids_consultas_conjuntas) + len(ids_consultas_unitarias),
        'cons_conjuntas': sorted(list(ids_consultas_conjuntas)),
        'cons_unitarias': sorted(list(ids_consultas_unitarias))
    })


class MedicoConsultaService(BaseDao):
    """
    Servicio para gestionar consultas médicas y generar reportes estadísticos
    """

    def __init__(self, dbsession):
        super().__init__(dbsession)
        self.medico_consulta_dao = TMedicoConsultaDao(self.dbsession)
        self.persona_dao = TPersonaDao(self.dbsession)

    def build_report(self, desde: str, hasta: str) -> List[Dict[str, Any]]:
        """
        Genera un reporte de consultas médicas entre dos fechas específicas

        Args:
            desde: Fecha inicial en formato 'YYYY-MM-DD'
            hasta: Fecha final en formato 'YYYY-MM-DD'

        Returns:
            Lista de diccionarios con estadísticas por médico
        """
        # Obtenemos las estadísticas de consultas en el rango de fechas
        estadisticas = self.medico_consulta_dao.find_consultas(desde, hasta)

        # Obtenemos la lista de médicos
        medicos = self.persona_dao.listar_medicos(med_tipo=1)

        # Extraemos las consultas conjuntas y unitarias de las estadísticas
        consultas_conjuntas = estadisticas.get('conjuntas', [])
        consultas_unitarias = estadisticas.get('unitarias', [])

        # Procesamos cada médico para agregar sus estadísticas
        for medico in medicos:
            _agregar_estadisticas_medico(
                medico,
                consultas_conjuntas,
                consultas_unitarias
            )

        return medicos
