"""
Versão simplificada do core land use change analysis.

Pipeline linear simples:
1. Carregar rasters
2. Empilhar rasters  
3. Gerar contingency table dos rasters empilhados
4. Gerar intensity table da contingency table

Mantém paralelização e processamento em blocos como padrão.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
import gc

import numpy as np
import pandas as pd
import rasterio
import rasterio.windows


@dataclass
class AnalysisResults:
    """Container para resultados da análise."""
    
    contingency_table: Optional[pd.DataFrame] = None
    intensity_table: Optional[pd.DataFrame] = None
    classes: Optional[List] = None
    class_names: Optional[Dict] = None
    time_periods: Optional[List] = None


class ContingencyTable:
    """
    Análise simplificada de mudança de uso da terra com rasters empilhados.
    
    Pipeline linear:
    1. Carrega todos os rasters
    2. Empilha em array 3D (n_rasters, height, width)
    3. Processa em blocos se necessário
    4. Gera contingency e intensity tables
    """
    
    def __init__(self, 
                 raster_data: List[Union[str, np.ndarray]],
                 time_labels: Optional[List[str]] = None,
                 class_names: Optional[Dict[int, str]] = None,
                 exclude_classes: Optional[List[int]] = None,
                 nodata_value: Optional[int] = -9999,
                 max_memory_gb: float = 4.0,
                 block_size: int = 1000,
                 use_multiprocessing: bool = True):
        """
        Inicializa análise de contingência com pipeline simplificado.
        
        Parameters
        ----------
        raster_data : List[Union[str, np.ndarray]]
            Lista de caminhos de arquivos ou arrays numpy
        time_labels : List[str], optional
            Rótulos temporais para cada raster
        class_names : Dict[int, str], optional  
            Mapeamento valor_classe -> nome_classe
        exclude_classes : List[int], optional
            Classes a excluir da análise
        nodata_value : int, optional
            Valor para dados inválidos
        max_memory_gb : float, optional
            Limite de memória em GB
        block_size : int, optional
            Tamanho do bloco para processamento
        use_multiprocessing : bool, optional
            Se deve usar processamento paralelo
        """
        # Configuração básica
        self.raster_data = raster_data
        self.time_labels = time_labels or self._generate_time_labels()
        self.class_names = class_names or {}
        self.exclude_classes = set(exclude_classes or [])
        self.nodata_value = nodata_value
        self.max_memory_gb = max_memory_gb
        self.block_size = block_size
        self.use_multiprocessing = use_multiprocessing
        
        # Executar pipeline completo
        self.results = self._execute_pipeline()
    
    def _generate_time_labels(self) -> List[str]:
        """Gera rótulos temporais padrão."""
        return [f"T{i+1}" for i in range(len(self.raster_data))]
    
    def _execute_pipeline(self) -> AnalysisResults:
        """
        Executa o pipeline completo de análise.
        
        Returns
        -------
        AnalysisResults
            Resultados da análise
        """
        print("🚀 Executando pipeline simplificado...")
        
        # 1. Configurar processamento
        self._setup_processing()
        
        # 2. Descobrir classes únicas
        print("🔍 Descobrindo classes únicas...")
        self.unique_classes = self._discover_unique_classes()
        self._update_class_names()
        
        # 3. Processar rasters empilhados
        print("📦 Processando rasters empilhados...")
        if self._needs_block_processing():
            print(f"📊 Usando processamento em blocos (tamanho: {self.block_size})")
            contingency_df = self._process_blocks_stacked()
        else:
            print("📊 Processando stack completo na memória")
            contingency_df = self._process_full_stacked()
        
        # 4. Gerar intensity table
        print("📈 Gerando intensity table...")
        intensity_df = self._calculate_intensity_table(contingency_df)
        
        print("✅ Pipeline concluído!")
        
        return AnalysisResults(
            contingency_table=contingency_df,
            intensity_table=intensity_df,
            classes=self.unique_classes,
            class_names=self.class_names,
            time_periods=self.time_labels
        )
    
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
        needs_blocks = stack_memory_gb > (self.max_memory_gb * 0.7)
        
        if needs_blocks:
            print(f"💾 Stack estimado: {stack_memory_gb:.2f} GB > {self.max_memory_gb*0.7:.2f} GB (limite)")
        
        return needs_blocks
    
    def _discover_unique_classes(self) -> List[int]:
        """Descobre classes únicas em todos os rasters."""
        all_classes = set()
        
        for i, raster in enumerate(self.raster_data):
            print(f"   Analisando raster {i+1}/{self.n_rasters}...")
            classes = self._get_raster_classes(raster)
            all_classes.update(classes)
        
        # Remover classes excluídas e nodata
        if self.nodata_value is not None:
            all_classes.discard(self.nodata_value)
        all_classes -= self.exclude_classes
        
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
            max_pixels = int((self.max_memory_gb * 0.3 * 1024**3) / 4)  # 30% da memória
            
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
        
        if array_size_gb <= self.max_memory_gb * 0.5:
            return set(np.unique(raster_array))
        else:
            # Processar em chunks
            unique_classes = set()
            flat_array = raster_array.flatten()
            chunk_size = int((self.max_memory_gb * 0.3 * 1024**3) / 4)
            
            for i in range(0, len(flat_array), chunk_size):
                chunk = flat_array[i:i + chunk_size]
                unique_classes.update(np.unique(chunk))
            
            return unique_classes
    
    def _update_class_names(self):
        """Atualiza nomes das classes."""
        for class_val in self.unique_classes:
            if class_val not in self.class_names:
                self.class_names[class_val] = f"Class_{class_val}"
    
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
        
        for row_start in range(0, self.height, self.block_size):
            for col_start in range(0, self.width, self.block_size):
                row_end = min(row_start + self.block_size, self.height)
                col_end = min(col_start + self.block_size, self.width)
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
            (flat_from != self.nodata_value) & 
            (flat_to != self.nodata_value) &
            (flat_from >= 0) & (flat_to >= 0)
        )
        
        # Aplicar exclusões
        for exclude_class in self.exclude_classes:
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
                    'class_name': self.class_names.get(class_val, f"Class_{class_val}"),
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
    def from_files(cls, file_paths: List[str], **kwargs) -> 'ContingencyTable':
        """
        Cria ContingencyTable a partir de arquivos raster.
        
        Parameters
        ----------
        file_paths : List[str]
            Caminhos para arquivos raster
        **kwargs
            Argumentos adicionais passados para __init__
            
        Returns
        -------
        ContingencyTable
            Instância configurada
        """
        # Extrair time labels dos nomes dos arquivos se não fornecidos
        if 'time_labels' not in kwargs:
            time_labels = []
            for path in file_paths:
                # Tentar extrair ano/data do nome do arquivo
                import re
                filename = Path(path).stem
                match = re.search(r'(\d{4})', filename)
                if match:
                    time_labels.append(match.group(1))
                else:
                    time_labels.append(filename)
            kwargs['time_labels'] = time_labels
        
        return cls(file_paths, **kwargs)
    
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
