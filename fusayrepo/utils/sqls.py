# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from fusayrepo.utils import cadenas

log = logging.getLogger(__name__)


def get_filtro_nomapelcedul(filtro):
    whereper = ''
    if cadenas.es_nonulo_novacio(filtro):
        palabras = cadenas.strip_upper(filtro).split()
        filtromod = []
        for cad in palabras:
            filtromod.append(u"%{0}%".format(cad))

        nombreslike = u' '.join(filtromod)
        filtrocedulas = u" per.per_ciruc like '{0}%'".format(cadenas.strip(filtro))
        whereper = u"""
                 (per.per_nombres||' '||per.per_apellidos like '{nombreslike}') or ({filtrocedulas}) 
                """.format(nombreslike=nombreslike, filtrocedulas=filtrocedulas)

    return whereper
