"""
Versão modernizada do core land use change analysis.

Pipeline linear inteligente:
1. Carregar rasters com auto-detecção de anos
2. Empilhar rasters com customização automática
3. Gerar contingency table dos rasters empilhados
4. Gerar intensity table da contingency table

Funcionalidades modernizadas:
- Auto-detecção de anos a partir de nomes de arquivos
- Sistema de personalização completo (cores, nomes, regiões)
- Configurações flexíveis e padrões inteligentes
- Mantém paralelização e processamento em blocos
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from concurrent.futures import ThreadPoolExecutor
import gc
import re

import numpy as np
import pandas as pd
import rasterio
import rasterio.windows


@dataclass
class AnalysisConfiguration:
    """Configuração modernizada para análise de mudança de uso da terra."""
    
    # Auto-detecção temporal
    auto_detect_years: bool = True
    year_patterns: List[str] = None
    
    # Personalização de classes
    class_names: Optional[Dict[int, str]] = None
    class_colors: Optional[Dict[int, str]] = None
    region_name: str = "Área de Estudo"
    
    # Configurações de processamento
    exclude_classes: Optional[List[int]] = None
    nodata_value: int = -9999
    max_memory_gb: float = 4.0
    block_size: int = 1000
    use_multiprocessing: bool = True
    
    # Configurações de exportação
    output_format: str = "xlsx"
    decimal_places: int = 4
    include_metadata: bool = True
    
    def __post_init__(self):
        """Inicializa configurações padrão."""
        if self.year_patterns is None:
            self.year_patterns = [
                r'(\d{4})',                    # Padrão geral: qualquer ano de 4 dígitos
                r'LC(\d{4})',                  # Landsat Collection: LC2023
                r'S2_(\d{4})',                 # Sentinel-2: S2_2023
                r'_(\d{4})_',                  # Ano entre underscores: _2023_
                r'(\d{4})[-_](\d{2})[-_](\d{2})',  # Data completa: 2023-01-15
                r'(?:landsat|sentinel|modis).*?(\d{4})',  # Sensores específicos
            ]
        
        if self.exclude_classes is None:
            self.exclude_classes = []


@dataclass
class AnalysisResults:
    """Container modernizado para resultados da análise."""
    
    contingency_table: Optional[pd.DataFrame] = None
    intensity_table: Optional[pd.DataFrame] = None
    classes: Optional[List] = None
    class_names: Optional[Dict] = None
    time_periods: Optional[List] = None
    metadata: Optional[Dict] = None
    configuration: Optional[AnalysisConfiguration] = None


class ContingencyTable:
    """
    Análise modernizada de mudança de uso da terra com recursos inteligentes.
    
    Funcionalidades modernizadas:
    - Auto-detecção de anos a partir de nomes de arquivos
    - Sistema de personalização completo (cores, nomes, regiões)
    - Configurações flexíveis e padrões inteligentes
    - Pipeline linear otimizado
    """
    
    def __init__(self, 
                 raster_data: List[Union[str, np.ndarray]],
                 config: Optional[AnalysisConfiguration] = None,
                 **kwargs):
        """
        Inicializa análise modernizada com configuração inteligente.
        
        Parameters
        ----------
        raster_data : List[Union[str, np.ndarray]]
            Lista de caminhos de arquivos ou arrays numpy
        config : AnalysisConfiguration, optional
            Configuração completa da análise
        **kwargs
            Argumentos de compatibilidade com versão anterior
        """
        # Configuração modernizada
        self.config = self._setup_configuration(config, **kwargs)
        self.raster_data = raster_data
        
        # Auto-detecção de períodos temporais
        self.time_labels = self._auto_detect_time_periods()
        
        # Executar pipeline completo
        self.results = self._execute_pipeline()
    
    def _setup_configuration(self, config: Optional[AnalysisConfiguration], **kwargs) -> AnalysisConfiguration:
        """
        Configura análise com suporte a argumentos legados.
        
        Parameters
        ----------
        config : AnalysisConfiguration, optional
            Configuração moderna
        **kwargs
            Argumentos de compatibilidade
            
        Returns
        -------
        AnalysisConfiguration
            Configuração final
        """
        if config is None:
            config = AnalysisConfiguration()
        
        # Compatibilidade com argumentos legados
        legacy_mapping = {
            'time_labels': None,  # Será auto-detectado
            'class_names': 'class_names',
            'exclude_classes': 'exclude_classes',
            'nodata_value': 'nodata_value',
            'max_memory_gb': 'max_memory_gb',
            'block_size': 'block_size',
            'use_multiprocessing': 'use_multiprocessing'
        }
        
        for old_name, new_name in legacy_mapping.items():
            if old_name in kwargs and new_name:
                setattr(config, new_name, kwargs[old_name])
        
        return config
    
    def _auto_detect_time_periods(self) -> List[str]:
        """
        Auto-detecta períodos temporais a partir de nomes de arquivos.
        
        Returns
        -------
        List[str]
            Lista de períodos detectados
        """
        if not self.config.auto_detect_years:
            return [f"T{i+1}" for i in range(len(self.raster_data))]
        
        detected_periods = []
        
        for data in self.raster_data:
            if isinstance(data, str):
                filename = Path(data).stem
                detected_year = self._extract_year_from_filename(filename)
                detected_periods.append(detected_year or filename)
            else:
                detected_periods.append(f"Array_{len(detected_periods)+1}")
        
        return detected_periods
    
    def _extract_year_from_filename(self, filename: str) -> Optional[str]:
        """
        Extrai ano do nome do arquivo usando múltiplos padrões.
        
        Parameters
        ----------
        filename : str
            Nome do arquivo
            
        Returns
        -------
        Optional[str]
            Ano extraído ou None
        """
        filename_lower = filename.lower()
        
        for pattern in self.config.year_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                # Retorna o primeiro grupo que contém 4 dígitos
                for group in match.groups():
                    if group and len(group) == 4 and group.isdigit():
                        return group
                
                # Se não encontrou grupo de 4 dígitos, usa o primeiro grupo
                if match.groups():
                    return match.group(1)
        
        return None
    
    def _execute_pipeline(self) -> AnalysisResults:
        """
        Executa o pipeline modernizado de análise.
        
        Returns
        -------
        AnalysisResults
            Resultados completos da análise com metadados
        """
        print(f"🚀 Executando pipeline modernizado para {self.config.region_name}...")
        
        # 1. Configurar processamento
        self._setup_processing()
        
        # 2. Descobrir classes únicas
        print("🔍 Descobrindo classes únicas...")
        self.unique_classes = self._discover_unique_classes()
        self._update_class_names()
        
        # 3. Processar rasters empilhados
        print("📦 Processando rasters empilhados...")
        if self._needs_block_processing():
            print(f"📊 Usando processamento em blocos (tamanho: {self.config.block_size})")
            contingency_df = self._process_blocks_stacked()
        else:
            print("📊 Processando stack completo na memória")
            contingency_df = self._process_full_stacked()
        
        # 4. Gerar intensity table
        print("📈 Gerando intensity table...")
        intensity_df = self._calculate_intensity_table(contingency_df)
        
        # 5. Criar metadados completos
        metadata = self._create_analysis_metadata()
        
        print("✅ Pipeline modernizado concluído!")
        
        return AnalysisResults(
            contingency_table=contingency_df,
            intensity_table=intensity_df,
            classes=self.unique_classes,
            class_names=self.config.class_names or {},
            time_periods=self.time_labels,
            metadata=metadata,
            configuration=self.config
        )
    
    def _create_analysis_metadata(self) -> Dict[str, Any]:
        """
        Cria metadados completos da análise.
        
        Returns
        -------
        Dict[str, Any]
            Metadados estruturados
        """
        from datetime import datetime
        
        metadata = {
            'analysis_info': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0-modernized',
                'region_name': self.config.region_name,
                'auto_detection_enabled': self.config.auto_detect_years
            },
            'data_info': {
                'total_rasters': self.n_rasters,
                'dimensions': f"{self.height}x{self.width}",
                'total_pixels': self.total_pixels,
                'time_periods': self.time_labels,
                'detected_classes': len(self.unique_classes) if hasattr(self, 'unique_classes') else 0
            },
            'processing_info': {
                'memory_limit_gb': self.config.max_memory_gb,
                'block_size': self.config.block_size,
                'multiprocessing': self.config.use_multiprocessing,
                'block_processing_used': self._needs_block_processing()
            },
            'customization': {
                'class_names_provided': bool(self.config.class_names),
                'colors_provided': bool(self.config.class_colors),
                'excluded_classes': list(self.config.exclude_classes)
            }
        }
        
        # Adicionar informações de arquivos se disponível
        if isinstance(self.raster_data[0], str):
            metadata['files'] = [str(Path(f).name) for f in self.raster_data]
        
        return metadata
    
    def _setup_processing(self):
        """Configura parâmetros de processamento."""
        # Obter dimensões do primeiro raster
        if isinstance(self.raster_data[0], str):
            with rasterio.open(self.raster_data[0]) as src:
                self.height, self.width = src.shape
                self.dtype = src.dtypes[0]
        else:
            self.height, self.width = self.raster_data[0].shape
            self.dtype = self.raster_data[0].dtype
        
        self.n_rasters = len(self.raster_data)
        self.total_pixels = self.height * self.width
        
        print(f"📐 Dimensões: {self.height}x{self.width} = {self.total_pixels:,} pixels")
        print(f"📅 Períodos temporais: {self.n_rasters}")
    
    def _needs_block_processing(self) -> bool:
        """Determina se precisa de processamento em blocos."""
        # Estimar memória necessária para stack completo
        bytes_per_pixel = 4  # float32
        stack_memory_gb = (self.total_pixels * self.n_rasters * bytes_per_pixel) / (1024**3)
        
        # Usar blocos se estimativa > 70% do limite
        needs_blocks = stack_memory_gb > (self.config.max_memory_gb * 0.7)
        
        if needs_blocks:
            print(f"💾 Stack estimado: {stack_memory_gb:.2f} GB > {self.config.max_memory_gb*0.7:.2f} GB (limite)")
        
        return needs_blocks
    
    def _discover_unique_classes(self) -> List[int]:
        """Descobre classes únicas em todos os rasters."""
        all_classes = set()
        
        for i, raster in enumerate(self.raster_data):
            print(f"   Analisando raster {i+1}/{self.n_rasters}...")
            classes = self._get_raster_classes(raster)
            all_classes.update(classes)
        
        # Remover classes excluídas e nodata
        if self.config.nodata_value is not None:
            all_classes.discard(self.config.nodata_value)
        all_classes -= set(self.config.exclude_classes)
        
        return sorted(list(all_classes))
    
    def _get_raster_classes(self, raster) -> set:
        """Obtém classes únicas de um raster (com processamento em blocos se necessário)."""
        if isinstance(raster, str):
            return self._get_classes_from_file(raster)
        else:
            return self._get_classes_from_array(raster)
    
    def _get_classes_from_file(self, raster_path: str) -> set:
        """Obtém classes de arquivo raster em blocos."""
        unique_classes = set()
        
        with rasterio.open(raster_path) as src:
            # Calcular tamanho de bloco baseado na memória
            max_pixels = int((self.config.max_memory_gb * 0.3 * 1024**3) / 4)  # 30% da memória
            
            if self.total_pixels <= max_pixels:
                # Pequeno o suficiente para ler de uma vez
                data = src.read(1)
                unique_classes.update(np.unique(data))
            else:
                # Processar em blocos
                block_height = max(1, int(max_pixels / self.width))
                
                for i in range(0, self.height, block_height):
                    end_row = min(i + block_height, self.height)
                    window = rasterio.windows.Window(0, i, self.width, end_row - i)
                    block_data = src.read(1, window=window)
                    unique_classes.update(np.unique(block_data))
        
        return unique_classes
    
    def _get_classes_from_array(self, raster_array: np.ndarray) -> set:
        """Obtém classes de array numpy."""
        # Verificar se cabe na memória
        array_size_gb = raster_array.nbytes / (1024**3)
        
        if array_size_gb <= self.config.max_memory_gb * 0.5:
            return set(np.unique(raster_array))
        else:
            # Processar em chunks
            unique_classes = set()
            flat_array = raster_array.flatten()
            chunk_size = int((self.config.max_memory_gb * 0.3 * 1024**3) / 4)
            
            for i in range(0, len(flat_array), chunk_size):
                chunk = flat_array[i:i + chunk_size]
                unique_classes.update(np.unique(chunk))
            
            return unique_classes
    
    def _update_class_names(self):
        """Atualiza nomes das classes usando configuração modernizada."""
        if self.config.class_names is None:
            self.config.class_names = {}
        
        for class_val in self.unique_classes:
            if class_val not in self.config.class_names:
                self.config.class_names[class_val] = f"Class_{class_val}"
    
    def _process_full_stacked(self) -> pd.DataFrame:
        """Processa stack completo na memória."""
        # Criar stack de todos os rasters
        stack = self._create_full_stack()
        
        # Calcular contingency do stack
        return self._calculate_contingency_from_stack(stack)
    
    def _create_full_stack(self) -> np.ndarray:
        """Cria stack completo de todos os rasters."""
        print("📚 Criando stack completo...")
        
        stack = np.zeros((self.n_rasters, self.height, self.width), dtype=self.dtype)
        
        for i, raster in enumerate(self.raster_data):
            if isinstance(raster, str):
                with rasterio.open(raster) as src:
                    stack[i] = src.read(1)
            else:
                stack[i] = raster
        
        return stack
    
    def _process_blocks_stacked(self) -> pd.DataFrame:
        """Processa stack em blocos."""
        # Calcular grid de blocos
        blocks = self._calculate_block_grid()
        print(f"📊 Processando {len(blocks)} blocos...")
        
        # Processar blocos
        if self.use_multiprocessing and len(blocks) > 4:
            print("🔄 Usando processamento paralelo...")
            with ThreadPoolExecutor(max_workers=min(4, len(blocks))) as executor:
                block_results = list(executor.map(self._process_single_block, blocks))
        else:
            block_results = []
            for i, block in enumerate(blocks):
                if i % max(1, len(blocks) // 10) == 0:
                    progress = (i / len(blocks)) * 100
                    print(f"⏳ Progresso: {progress:.1f}% ({i}/{len(blocks)} blocos)")
                
                result = self._process_single_block(block)
                block_results.append(result)
        
        # Agregar resultados dos blocos
        print("🔄 Agregando resultados dos blocos...")
        return self._aggregate_block_results(block_results)
    
    def _calculate_block_grid(self) -> List[Tuple[slice, slice]]:
        """Calcula grid de blocos para processamento."""
        blocks = []
        
        for row_start in range(0, self.height, self.config.block_size):
            for col_start in range(0, self.width, self.config.block_size):
                row_end = min(row_start + self.config.block_size, self.height)
                col_end = min(col_start + self.config.block_size, self.width)
                blocks.append((slice(row_start, row_end), slice(col_start, col_end)))
        
        return blocks
    
    def _process_single_block(self, block_coords: Tuple[slice, slice]) -> pd.DataFrame:
        """Processa um único bloco."""
        row_slice, col_slice = block_coords
        
        # Extrair stack do bloco
        block_stack = self._extract_block_stack(row_slice, col_slice)
        
        # Calcular contingency do bloco
        result = self._calculate_contingency_from_stack(block_stack)
        
        # Limpeza de memória
        del block_stack
        gc.collect()
        
        return result
    
    def _extract_block_stack(self, row_slice: slice, col_slice: slice) -> np.ndarray:
        """Extrai stack de um bloco específico."""
        block_height = row_slice.stop - row_slice.start
        block_width = col_slice.stop - col_slice.start
        block_stack = np.zeros((self.n_rasters, block_height, block_width), dtype=self.dtype)
        
        for i, raster in enumerate(self.raster_data):
            if isinstance(raster, str):
                with rasterio.open(raster) as src:
                    window = rasterio.windows.Window(
                        col_slice.start, row_slice.start,
                        block_width, block_height
                    )
                    block_stack[i] = src.read(1, window=window)
            else:
                block_stack[i] = raster[row_slice, col_slice]
        
        return block_stack
    
    def _calculate_contingency_from_stack(self, stack: np.ndarray) -> pd.DataFrame:
        """Calcula contingency table a partir do stack."""
        n_rasters, height, width = stack.shape
        all_transitions = []
        
        # Transições multistep (sequenciais)
        if n_rasters > 2:
            for i in range(n_rasters - 1):
                transitions = self._extract_transitions(
                    stack[i], stack[i + 1],
                    self.time_labels[i], self.time_labels[i + 1],
                    'multistep'
                )
                all_transitions.extend(transitions)
        
        # Transição onestep (primeira para última)
        if n_rasters > 1:
            transitions = self._extract_transitions(
                stack[0], stack[-1],
                self.time_labels[0], self.time_labels[-1],
                'onestep'
            )
            all_transitions.extend(transitions)
        
        return pd.DataFrame(all_transitions) if all_transitions else pd.DataFrame()
    
    def _extract_transitions(self, from_raster: np.ndarray, to_raster: np.ndarray,
                           time_from: str, time_to: str, transition_type: str) -> List[dict]:
        """Extrai transições entre dois rasters."""
        # Flatten e filtrar pixels válidos
        flat_from = from_raster.flatten()
        flat_to = to_raster.flatten()
        
        # Máscara para pixels válidos
        valid_mask = (
            (flat_from != self.config.nodata_value) & 
            (flat_to != self.config.nodata_value) &
            (flat_from >= 0) & (flat_to >= 0)
        )
        
        # Aplicar exclusões
        for exclude_class in self.config.exclude_classes:
            valid_mask = valid_mask & (flat_from != exclude_class) & (flat_to != exclude_class)
        
        flat_from = flat_from[valid_mask]
        flat_to = flat_to[valid_mask]
        
        if len(flat_from) == 0:
            return []
        
        # Contar transições de forma vectorizada
        transitions = []
        unique_pairs, counts = np.unique(
            np.column_stack([flat_from, flat_to]), 
            axis=0, return_counts=True
        )
        
        for (from_class, to_class), count in zip(unique_pairs, counts):
            transitions.append({
                'time_from': time_from,
                'time_to': time_to,
                'class_from': int(from_class),
                'class_to': int(to_class),
                'count': int(count),
                'transition_type': transition_type
            })
        
        return transitions
    
    def _aggregate_block_results(self, block_results: List[pd.DataFrame]) -> pd.DataFrame:
        """Agrega resultados de múltiplos blocos."""
        # Filtrar resultados vazios
        valid_results = [df for df in block_results if not df.empty]
        
        if not valid_results:
            return pd.DataFrame()
        
        # Concatenar todos os resultados
        combined_df = pd.concat(valid_results, ignore_index=True)
        
        # Agregar por chaves de transição
        aggregated = combined_df.groupby([
            'transition_type', 'time_from', 'time_to', 'class_from', 'class_to'
        ])['count'].sum().reset_index()
        
        return aggregated
    
    def _calculate_intensity_table(self, contingency_df: pd.DataFrame) -> pd.DataFrame:
        """Calcula intensity table a partir da contingency table."""
        if contingency_df.empty:
            return pd.DataFrame()
        
        intensity_data = []
        
        # Agrupar por tipo de transição e período
        for (trans_type, t_from, t_to), group in contingency_df.groupby(['transition_type', 'time_from', 'time_to']):
            
            # Calcular métricas para cada classe
            for class_val in self.unique_classes:
                # Gain: outras classes -> esta classe
                gain = group[
                    (group['class_to'] == class_val) & 
                    (group['class_from'] != class_val)
                ]['count'].sum()
                
                # Loss: esta classe -> outras classes
                loss = group[
                    (group['class_from'] == class_val) & 
                    (group['class_to'] != class_val)
                ]['count'].sum()
                
                # Persistence: esta classe -> esta classe
                persistence = group[
                    (group['class_from'] == class_val) & 
                    (group['class_to'] == class_val)
                ]['count'].sum()
                
                # Total area inicial da classe
                initial_area = group[group['class_from'] == class_val]['count'].sum()
                
                # Total area final da classe
                final_area = group[group['class_to'] == class_val]['count'].sum()
                
                intensity_data.append({
                    'transition_type': trans_type,
                    'time_from': t_from,
                    'time_to': t_to,
                    'class': class_val,
                    'class_name': self.config.class_names.get(class_val, f"Class_{class_val}"),
                    'gain': int(gain),
                    'loss': int(loss),
                    'persistence': int(persistence),
                    'net_change': int(gain - loss),
                    'initial_area': int(initial_area),
                    'final_area': int(final_area),
                    'total_change': int(gain + loss)
                })
        
        return pd.DataFrame(intensity_data)
    
    @classmethod
    def from_files(cls, file_paths: List[str], 
                   config: Optional[AnalysisConfiguration] = None,
                   **kwargs) -> 'ContingencyTable':
        """
        Cria ContingencyTable modernizado a partir de arquivos raster.
        
        Parameters
        ----------
        file_paths : List[str]
            Caminhos para arquivos raster
        config : AnalysisConfiguration, optional
            Configuração modernizada da análise
        **kwargs
            Argumentos de compatibilidade com versão anterior
            
        Returns
        -------
        ContingencyTable
            Instância configurada com auto-detecção
        """
        # Criar configuração se não fornecida
        if config is None:
            config = AnalysisConfiguration()
        
        # Manter compatibilidade com argumentos legados
        if 'time_labels' in kwargs:
            config.auto_detect_years = False
        
        return cls(file_paths, config=config, **kwargs)
    
    @classmethod
    def from_arrays(cls, arrays: List[np.ndarray], **kwargs) -> 'ContingencyTable':
        """
        Cria ContingencyTable a partir de arrays numpy.
        
        Parameters
        ----------
        arrays : List[np.ndarray]
            Lista de arrays numpy
        **kwargs
            Argumentos adicionais passados para __init__
            
        Returns
        -------
        ContingencyTable
            Instância configurada
        """
        return cls(arrays, **kwargs)

    # Propriedades para compatibilidade com código existente
    @property
    def contingency_table(self) -> pd.DataFrame:
        """Acesso direto à contingency table."""
        return self.results.contingency_table
    
    @property
    def intensity_table(self) -> pd.DataFrame:
        """Acesso direto à intensity table."""
        return self.results.intensity_table
    
    @property
    def classes(self) -> List:
        """Acesso direto às classes."""
        return self.results.classes
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Acesso direto aos metadados."""
        return self.results.metadata
    
    @property
    def detected_years(self) -> List[str]:
        """Acesso direto aos anos detectados."""
        return self.time_labels
    
    def export_with_customization(self, 
                                  output_path: str,
                                  include_metadata: bool = True,
                                  custom_colors: Optional[Dict[int, str]] = None) -> str:
        """
        Exporta resultados com personalização completa.
        
        Parameters
        ----------
        output_path : str
            Caminho de saída
        include_metadata : bool
            Se deve incluir metadados
        custom_colors : Dict[int, str], optional
            Cores personalizadas para classes
            
        Returns
        -------
        str
            Caminho do arquivo exportado
        """
        output_path = Path(output_path)
        
        if output_path.suffix.lower() == '.xlsx':
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Tabela de contingência
                self.contingency_table.to_excel(writer, sheet_name='Contingency', index=False)
                
                # Tabela de intensidade
                self.intensity_table.to_excel(writer, sheet_name='Intensity', index=False)
                
                # Metadados se solicitado
                if include_metadata and self.metadata:
                    metadata_df = pd.DataFrame([
                        {'Property': k, 'Value': str(v)} 
                        for k, v in self._flatten_dict(self.metadata).items()
                    ])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Cores personalizadas se fornecidas
                if custom_colors or self.config.class_colors:
                    colors = custom_colors or self.config.class_colors
                    colors_df = pd.DataFrame([
                        {'Class': k, 'Color': v, 'Name': self.config.class_names.get(k, f'Class_{k}')}
                        for k, v in colors.items()
                    ])
                    colors_df.to_excel(writer, sheet_name='Colors', index=False)
        
        else:
            # Formato CSV - apenas contingency table
            self.contingency_table.to_csv(output_path, index=False)
        
        return str(output_path)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Achata dicionário aninhado para exportação."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @classmethod
    def create_cerrado_config(cls,
                              region_name: str = "Cerrado",
                              custom_classes: Optional[Dict[int, str]] = None) -> AnalysisConfiguration:
        """
        Cria configuração pré-definida para análise do Cerrado.
        
        Parameters
        ----------
        region_name : str
            Nome da região
        custom_classes : Dict[int, str], optional
            Classes personalizadas
            
        Returns
        -------
        AnalysisConfiguration
            Configuração para o Cerrado
        """
        # Classes padrão do Cerrado (baseado no MapBiomas)
        default_classes = custom_classes or {
            3: "Formação Florestal",
            4: "Formação Savânica", 
            11: "Campo Alagado e Área Pantanosa",
            12: "Formação Campestre",
            15: "Pastagem",
            18: "Agricultura",
            25: "Outras Áreas não Vegetadas",
            33: "Rio, Lago e Oceano"
        }
        
        # Cores padrão do MapBiomas
        default_colors = {
            3: "#006400",   # Verde escuro - Floresta
            4: "#00FF00",   # Verde claro - Savana
            11: "#0000FF",  # Azul - Área Alagada
            12: "#FFD700",  # Amarelo - Campo
            15: "#FFB6C1",  # Rosa - Pastagem
            18: "#FF1493",  # Pink - Agricultura
            25: "#8B4513",  # Marrom - Área não vegetada
            33: "#4169E1"   # Azul real - Água
        }
        
        return AnalysisConfiguration(
            auto_detect_years=True,
            class_names=default_classes,
            class_colors=default_colors,
            region_name=region_name,
            exclude_classes=[0],  # Excluir NoData
            year_patterns=[
                r'(\d{4})',
                r'mapbiomas.*?(\d{4})',
                r'cerrado.*?(\d{4})',
                r'_(\d{4})_'
            ]
        )


# Aliases para compatibilidade com código existente
MultiStepAnalyzer = ContingencyTable
IntensityAnalyzer = ContingencyTable
