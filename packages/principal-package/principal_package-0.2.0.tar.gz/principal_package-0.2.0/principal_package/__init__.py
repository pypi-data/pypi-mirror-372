import logging
from collections import Counter
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

import importlib.util, importlib.machinery, pathlib, glob

_pkg = pathlib.Path(__file__).parent
_pycache = _pkg / "__pycache__"

# Busca funtions.cpython-*.pyc
matches = glob.glob(str(_pycache / "funtions.cpython-*.pyc"))
if not matches:
    raise ImportError(
        "No se encontró '__pycache__/funtions.cpython-*.pyc'. "
        "Compila antes con: python -m compileall principal_package"
    )

_pyc_path = matches[0]
loader = importlib.machinery.SourcelessFileLoader("principal_package.funtions", _pyc_path)
spec = importlib.machinery.ModuleSpec("principal_package.funtions", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
clearing_description   = mod.clearing_description
processlanguage_reductor = mod.processlanguage_reductor
principal_components   = mod.principal_components
map_separate_clusters  = mod.map_separate_clusters
date_processing        = mod.date_processing
clusters_cercanos      = mod.clusters_cercanos
modelo_d               = mod.modelo_d
silhouette             = mod.silhouette
silhouette_per_sample  = mod.silhouette_per_sample
davies_bouldin         = mod.davies_bouldin
calinski_harabasz      = mod.calinski_harabasz
map_conserve_structure = mod.map_conserve_structure
modelo_h               = mod.modelo_h
generador_plantillas   = mod.generador_plantillas
multiprocess           = mod.multiprocess
delayed                = mod.delayed
tqdm_progress          = mod.tqdm_progress
plt_figure             = mod.plt_figure
plt_show               = mod.plt_show
plt_subplots           = mod.plt_subplots
xl_get_column_letter   = mod.xl_get_column_letter
xl_alignment           = mod.xl_alignment
xl_number_formats      = mod.xl_number_formats
arboles_decision_entrenado      = mod.arboles_decision_entrenado
pipe      = mod.pipe
grafico_arbol      = mod.grafico_arbol


__version__ = "0.2.0"

__all__ = [
    "logging", "Counter",
    "np", "pd", "sns", "plt", "px", "pio",
    "clearing_description",
    "processlanguage_reductor",
    "principal_components",
    "map_separate_clusters",
    "date_processing",
    "clusters_cercanos",
    "modelo_d",
    "silhouette",
    "silhouette_per_sample",
    "davies_bouldin",
    "calinski_harabasz",
    "map_conserve_structure",
    "modelo_h",
    "generador_plantillas",
    "multiprocess",
    "delayed",
    "tqdm_progress",
    "plt_figure",
    "plt_show",
    "plt_subplots",
    "xl_get_column_letter",
    "xl_alignment",
    "xl_number_formats",
    "arboles_decision_entrenado",
    "pipe",
    "grafico_arbol",
    "__version__",
]