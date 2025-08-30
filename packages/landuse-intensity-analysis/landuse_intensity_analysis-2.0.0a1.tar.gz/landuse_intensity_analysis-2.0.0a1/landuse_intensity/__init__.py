# Classe principal modernizada
from .core import ContingencyTable, AnalysisConfiguration, AnalysisResults

# Aliases para compatibilidade
from .core import MultiStepAnalyzer, IntensityAnalyzer

# Módulos de visualização
from . import visualization
from . import graph_visualization  
from . import map_visualization

# Utilitários
from . import utils
from . import raster
from . import image_processing

__version__ = "2.0.0a1"

__all__ = [
    "ContingencyTable",
    "AnalysisConfiguration", 
    "AnalysisResults",
    "MultiStepAnalyzer", 
    "IntensityAnalyzer",
    "visualization",
    "graph_visualization",
    "map_visualization", 
    "utils",
    "raster",
    "image_processing",
    "__version__"
]
