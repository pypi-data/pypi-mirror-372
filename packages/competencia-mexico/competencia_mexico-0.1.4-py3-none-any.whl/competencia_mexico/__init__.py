"""
Paquete competencia_mexico
-------------------------
Herramientas para análisis de competencia económica, precios,
visualización de datos y recuperación aumentada (RAG) con FAISS + DeepSeek.
"""

# Importar submódulos para acceso directo
from .indices import (
    calcular_ihh_interactivo,
    calcular_id_interactivo,
    variacion_ihh_interactiva,
    variacion_dominancia_interactiva
)

from .sobreprecios import (
    aumentar_precios,
    calcular_sobreprecio,
    perdida_colusion
)

from .graficos import graficar_y_resumir_asuntos_interactiva
from .articulos import buscar_articulos_csv
from .rag import consultar_con_rag_deepseek

# Definir versión del paquete
__version__ = "0.1.0"

# Qué se exporta si el usuario hace `from competencia_mexico import *`
__all__ = [
    # indices
    "calcular_ihh_interactivo",
    "calcular_id_interactivo",
    "variacion_ihh_interactiva",
    "variacion_dominancia_interactiva",
    # precios
    "aumentar_precios",
    "calcular_sobreprecio",
    "perdida_colusion",
    # graficos
    "graficar_y_resumir_asuntos_interactiva",
    # utils
    "buscar_articulos_csv",
    # rag
    "consultar_con_rag_deepseek",
]
