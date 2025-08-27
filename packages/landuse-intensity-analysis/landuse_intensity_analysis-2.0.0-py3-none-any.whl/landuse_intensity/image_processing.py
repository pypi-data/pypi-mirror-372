"""
Advanced Image Processing for Land Use and Land Cover Analysis

This module provides cutting-edge image processing techniques for LULC analysis:
- Spatial filtering and enhancement
- Pattern detection and classification
- Landscape connectivity analysis
- Multi-scale analysis
- Temporal consistency checking
- Edge detection and boundary analysis

Features:
- Integration with scikit-image, OpenCV, and scipy
- GPU acceleration support
- Memory-efficient processing for large rasters
- Batch processing capabilities
- Quality assessment metrics
"""

import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from scipy.ndimage import binary_erosion, label

# Optional dependencies for advanced processing
HAS_SKIMAGE = False
HAS_CV2 = False
HAS_RASTERIO = False
HAS_NETWORKX = False

try:
    from skimage import feature, filters, measure, morphology, segmentation
    from skimage.filters import gaussian, median, sobel
    from skimage.measure import label as sk_label
    from skimage.measure import regionprops
    from skimage.morphology import closing, disk, opening, square
    from skimage.segmentation import slic, watershed

    HAS_SKIMAGE = True
except ImportError:
    pass

try:
    import cv2

    HAS_CV2 = True
except ImportError:
    pass

try:
    import rasterio
    from rasterio.features import shapes
    from rasterio.transform import from_bounds

    HAS_RASTERIO = True
except ImportError:
    pass

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    pass


class FilterType(Enum):
    """Types of spatial filters available."""

    GAUSSIAN = "gaussian"
    MEDIAN = "median"
    SOBEL = "sobel"
    LAPLACIAN = "laplacian"
    BILATERAL = "bilateral"
    OPENING = "opening"
    CLOSING = "closing"


@dataclass
class LandscapeMetrics:
    """Container for landscape-level metrics."""

    total_area: float
    n_patches: int
    mean_patch_size: float
    patch_density: float
    edge_density: float
    shannon_diversity: float
    simpson_diversity: float
    contagion: float
    fragmentation_index: float


@dataclass
class ConnectivityMetrics:
    """Container for connectivity analysis results."""

    connectivity_matrix: np.ndarray
    clustering_coefficient: float
    path_lengths: Dict[str, float]
    centrality_measures: Dict[str, np.ndarray]
    community_structure: List[List[int]]


@dataclass
class ChangeDetectionResults:
    """Results from change detection analysis."""

    change_map: np.ndarray
    change_magnitude: np.ndarray
    change_direction: np.ndarray
    hotspots: List[Tuple[int, int]]
    change_statistics: Dict[str, float]


class AdvancedImageProcessor:
    """
    Advanced image processing for LULC analysis.

    Provides comprehensive spatial analysis tools including filtering,
    pattern detection, connectivity analysis, and change detection.
    """

    def __init__(
        self, chunk_size: int = 1024, use_gpu: bool = False, memory_limit: str = "4GB"
    ):
        """
        Initialize advanced image processor.

        Parameters
        ----------
        chunk_size : int
            Size of processing chunks for large rasters
        use_gpu : bool
            Enable GPU acceleration if available
        memory_limit : str
            Maximum memory usage for processing
        """
        self.chunk_size = chunk_size
        self.use_gpu = use_gpu
        self.memory_limit = memory_limit

        # Check available libraries
        self._check_dependencies()

    def _check_dependencies(self):
        """Check and warn about missing dependencies."""
        if not HAS_SKIMAGE:
            warnings.warn("scikit-image not available. Some features will be limited.")
        if not HAS_CV2:
            warnings.warn("OpenCV not available. Some features will be limited.")
        if not HAS_RASTERIO:
            warnings.warn("rasterio not available. Some features will be limited.")

    def apply_spatial_filter(
        self,
        raster: np.ndarray,
        filter_type: FilterType,
        kernel_size: int = 3,
        sigma: float = 1.0,
        **kwargs,
    ) -> np.ndarray:
        """
        Apply spatial filter to raster data.

        Parameters
        ----------
        raster : np.ndarray
            Input raster data
        filter_type : FilterType
            Type of filter to apply
        kernel_size : int
            Size of filter kernel
        sigma : float
            Standard deviation for Gaussian filters

        Returns
        -------
        np.ndarray
            Filtered raster
        """
        if not HAS_SKIMAGE:
            raise ImportError("scikit-image required for spatial filtering")

        # Convert to float for processing
        raster_float = raster.astype(np.float64)

        if filter_type == FilterType.GAUSSIAN:
            return gaussian(raster_float, sigma=sigma)

        elif filter_type == FilterType.MEDIAN:
            kernel = disk(kernel_size)
            return median(raster_float, kernel)

        elif filter_type == FilterType.SOBEL:
            return sobel(raster_float)

        elif filter_type == FilterType.LAPLACIAN:
            return ndimage.laplace(raster_float)

        elif filter_type == FilterType.OPENING:
            kernel = disk(kernel_size)
            return opening(raster_float, kernel)

        elif filter_type == FilterType.CLOSING:
            kernel = disk(kernel_size)
            return closing(raster_float, kernel)

        elif filter_type == FilterType.BILATERAL:
            if HAS_CV2:
                # Convert to uint8 for OpenCV
                raster_uint8 = (
                    (raster_float - raster_float.min())
                    / (raster_float.max() - raster_float.min())
                    * 255
                ).astype(np.uint8)
                filtered = cv2.bilateralFilter(
                    raster_uint8, kernel_size, sigma * 10, sigma * 10
                )
                return filtered.astype(np.float64) / 255.0
            else:
                warnings.warn("OpenCV not available, using Gaussian filter instead")
                return gaussian(raster_float, sigma=sigma)

        else:
            raise ValueError(f"Unknown filter type: {filter_type}")

    def detect_patterns(
        self,
        raster: np.ndarray,
        pattern_type: str = "edges",
        threshold: Optional[float] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Detect spatial patterns in raster data.

        Parameters
        ----------
        raster : np.ndarray
            Input raster data
        pattern_type : str
            Type of pattern to detect ('edges', 'blobs', 'corners')
        threshold : float, optional
            Detection threshold

        Returns
        -------
        np.ndarray
            Pattern detection results
        """
        if not HAS_SKIMAGE:
            raise ImportError("scikit-image required for pattern detection")

        if pattern_type == "edges":
            # Edge detection using Sobel operator
            edges = sobel(raster.astype(np.float64))
            if threshold is not None:
                edges = edges > threshold
            return edges

        elif pattern_type == "blobs":
            # Blob detection using Laplacian of Gaussian
            log_result = ndimage.gaussian_laplace(raster.astype(np.float64), sigma=2)
            if threshold is not None:
                return np.abs(log_result) > threshold
            return np.abs(log_result)

        elif pattern_type == "corners":
            # Corner detection using Harris corner detector
            if HAS_CV2:
                raster_uint8 = raster.astype(np.uint8)
                corners = cv2.cornerHarris(raster_uint8, 2, 3, 0.04)
                if threshold is not None:
                    corners = corners > threshold
                return corners
            else:
                warnings.warn("OpenCV not available for corner detection")
                return np.zeros_like(raster)

        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")

    def calculate_landscape_metrics(
        self, raster: np.ndarray, category_values: Optional[List[int]] = None
    ) -> LandscapeMetrics:
        """
        Calculate comprehensive landscape metrics.

        Parameters
        ----------
        raster : np.ndarray
            Input categorical raster
        category_values : List[int], optional
            Specific categories to analyze

        Returns
        -------
        LandscapeMetrics
            Computed landscape metrics
        """
        if category_values is None:
            category_values = np.unique(raster)

        total_area = raster.size
        n_patches = 0
        patch_sizes = []
        edge_pixels = 0

        # Calculate metrics for each category
        for category in category_values:
            # Create binary mask for this category
            mask = raster == category

            if not np.any(mask):
                continue

            # Label connected components (patches)
            labeled_patches, n_cat_patches = label(mask)
            n_patches += n_cat_patches

            # Calculate patch sizes
            for patch_id in range(1, n_cat_patches + 1):
                patch_mask = labeled_patches == patch_id
                patch_size = np.sum(patch_mask)
                patch_sizes.append(patch_size)

                # Calculate edge pixels for this patch
                eroded = binary_erosion(patch_mask)
                edge_pixels += np.sum(patch_mask) - np.sum(eroded)

        # Calculate diversity indices
        category_counts = [np.sum(raster == cat) for cat in category_values]
        proportions = np.array(category_counts) / total_area
        proportions = proportions[proportions > 0]  # Remove zeros

        # Shannon diversity
        shannon_diversity = -np.sum(proportions * np.log(proportions))

        # Simpson diversity
        simpson_diversity = 1 - np.sum(proportions**2)

        # Contagion index (simplified)
        contagion = self._calculate_contagion(raster, category_values)

        # Fragmentation index
        mean_patch_size = np.mean(patch_sizes) if patch_sizes else 0
        fragmentation_index = n_patches / total_area if total_area > 0 else 0

        return LandscapeMetrics(
            total_area=total_area,
            n_patches=n_patches,
            mean_patch_size=mean_patch_size,
            patch_density=n_patches / total_area if total_area > 0 else 0,
            edge_density=edge_pixels / total_area if total_area > 0 else 0,
            shannon_diversity=shannon_diversity,
            simpson_diversity=simpson_diversity,
            contagion=contagion,
            fragmentation_index=fragmentation_index,
        )

    def _calculate_contagion(
        self, raster: np.ndarray, category_values: List[int]
    ) -> float:
        """Calculate contagion index."""
        # Simplified contagion calculation
        n_categories = len(category_values)
        total_adjacencies = 0
        like_adjacencies = 0

        # Check horizontal and vertical adjacencies
        for i in range(raster.shape[0] - 1):
            for j in range(raster.shape[1] - 1):
                # Horizontal adjacency
                if raster[i, j] == raster[i, j + 1]:
                    like_adjacencies += 1
                total_adjacencies += 1

                # Vertical adjacency
                if raster[i, j] == raster[i + 1, j]:
                    like_adjacencies += 1
                total_adjacencies += 1

        if total_adjacencies == 0:
            return 0

        observed_contagion = like_adjacencies / total_adjacencies
        expected_contagion = 1 / n_categories

        return (observed_contagion - expected_contagion) / (1 - expected_contagion)

    def analyze_connectivity(
        self,
        raster: np.ndarray,
        target_category: int,
        connectivity_rule: str = "8-connected",
    ) -> ConnectivityMetrics:
        """
        Analyze landscape connectivity for specific category.

        Parameters
        ----------
        raster : np.ndarray
            Input categorical raster
        target_category : int
            Category to analyze connectivity
        connectivity_rule : str
            Connectivity rule ('4-connected' or '8-connected')

        Returns
        -------
        ConnectivityMetrics
            Connectivity analysis results
        """
        if not HAS_NETWORKX:
            warnings.warn(
                "NetworkX not available. Using simplified connectivity analysis."
            )
            return self._simple_connectivity_analysis(raster, target_category)

        # Create binary mask for target category
        mask = raster == target_category

        # Label connected components
        structure = (
            np.ones((3, 3))
            if connectivity_rule == "8-connected"
            else np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
        )
        labeled_patches, n_patches = label(mask, structure=structure)

        # Create graph of patch connectivity
        G = nx.Graph()

        # Add patches as nodes
        for patch_id in range(1, n_patches + 1):
            G.add_node(patch_id)

        # Calculate distances between patch centroids
        patch_centroids = {}
        for patch_id in range(1, n_patches + 1):
            coords = np.where(labeled_patches == patch_id)
            if len(coords[0]) > 0:
                centroid = (np.mean(coords[0]), np.mean(coords[1]))
                patch_centroids[patch_id] = centroid

        # Add edges based on distance threshold
        max_distance = min(raster.shape) * 0.1  # 10% of image dimension

        for i in range(1, n_patches + 1):
            for j in range(i + 1, n_patches + 1):
                if i in patch_centroids and j in patch_centroids:
                    distance = np.sqrt(
                        (patch_centroids[i][0] - patch_centroids[j][0]) ** 2
                        + (patch_centroids[i][1] - patch_centroids[j][1]) ** 2
                    )
                    if distance <= max_distance:
                        G.add_edge(i, j, weight=1 / distance if distance > 0 else 1)

        # Calculate connectivity metrics
        if len(G.nodes()) > 0:
            clustering_coeff = nx.average_clustering(G)

            # Path lengths
            if nx.is_connected(G):
                avg_path_length = nx.average_shortest_path_length(G)
                diameter = nx.diameter(G)
            else:
                # For disconnected graphs
                components = list(nx.connected_components(G))
                path_lengths = []
                for component in components:
                    subgraph = G.subgraph(component)
                    if len(subgraph) > 1:
                        path_lengths.append(nx.average_shortest_path_length(subgraph))
                avg_path_length = np.mean(path_lengths) if path_lengths else 0
                diameter = 0

            path_length_dict = {"average": avg_path_length, "diameter": diameter}

            # Centrality measures
            centrality_dict = {
                "betweenness": np.array(list(nx.betweenness_centrality(G).values())),
                "closeness": np.array(list(nx.closeness_centrality(G).values())),
                "degree": np.array(list(dict(G.degree()).values())),
            }

            # Community detection
            try:
                communities = list(nx.community.greedy_modularity_communities(G))
                community_structure = [list(community) for community in communities]
            except:
                community_structure = []

        else:
            clustering_coeff = 0
            path_length_dict = {"average": 0, "diameter": 0}
            centrality_dict = {
                "betweenness": np.array([]),
                "closeness": np.array([]),
                "degree": np.array([]),
            }
            community_structure = []

        # Create connectivity matrix
        connectivity_matrix = (
            nx.adjacency_matrix(G).todense() if len(G.nodes()) > 0 else np.array([[]])
        )

        return ConnectivityMetrics(
            connectivity_matrix=connectivity_matrix,
            clustering_coefficient=clustering_coeff,
            path_lengths=path_length_dict,
            centrality_measures=centrality_dict,
            community_structure=community_structure,
        )

    def _simple_connectivity_analysis(
        self, raster: np.ndarray, target_category: int
    ) -> ConnectivityMetrics:
        """Simplified connectivity analysis without NetworkX."""
        mask = raster == target_category
        labeled_patches, n_patches = label(mask)

        # Simple connectivity matrix (identity matrix for isolated analysis)
        connectivity_matrix = np.eye(n_patches) if n_patches > 0 else np.array([[]])

        return ConnectivityMetrics(
            connectivity_matrix=connectivity_matrix,
            clustering_coefficient=0.0,
            path_lengths={"average": 0, "diameter": 0},
            centrality_measures={
                "betweenness": np.array([]),
                "closeness": np.array([]),
                "degree": np.array([]),
            },
            community_structure=[],
        )

    def detect_change_hotspots(
        self,
        raster_t1: np.ndarray,
        raster_t2: np.ndarray,
        method: str = "difference",
        threshold: float = 0.1,
    ) -> ChangeDetectionResults:
        """
        Detect change hotspots between two time periods.

        Parameters
        ----------
        raster_t1, raster_t2 : np.ndarray
            Rasters for two time periods
        method : str
            Change detection method ('difference', 'ratio', 'chi_square')
        threshold : float
            Change detection threshold

        Returns
        -------
        ChangeDetectionResults
            Change detection results
        """
        if raster_t1.shape != raster_t2.shape:
            raise ValueError("Rasters must have the same dimensions")

        # Calculate change map
        if method == "difference":
            change_map = np.abs(raster_t2.astype(float) - raster_t1.astype(float))
            change_magnitude = change_map
            change_direction = np.sign(
                raster_t2.astype(float) - raster_t1.astype(float)
            )

        elif method == "ratio":
            # Avoid division by zero
            raster_t1_safe = np.where(raster_t1 == 0, 1e-10, raster_t1.astype(float))
            ratio = raster_t2.astype(float) / raster_t1_safe
            change_map = np.abs(ratio - 1)
            change_magnitude = change_map
            change_direction = np.sign(ratio - 1)

        elif method == "chi_square":
            # Chi-square test for categorical data
            contingency = np.zeros(
                (
                    np.max([raster_t1.max(), raster_t2.max()]) + 1,
                    np.max([raster_t1.max(), raster_t2.max()]) + 1,
                )
            )

            for i in range(raster_t1.shape[0]):
                for j in range(raster_t1.shape[1]):
                    contingency[raster_t1[i, j], raster_t2[i, j]] += 1

            # Simple change detection based on diagonal vs off-diagonal
            change_map = (raster_t1 != raster_t2).astype(float)
            change_magnitude = change_map
            change_direction = np.zeros_like(change_map)

        else:
            raise ValueError(f"Unknown change detection method: {method}")

        # Identify hotspots
        binary_change = change_magnitude > threshold

        # Find change hotspot locations
        hotspots = []
        if HAS_SKIMAGE:
            # Use connected component analysis to find hotspot clusters
            labeled_hotspots, n_hotspots = sk_label(binary_change)

            for hotspot_id in range(1, n_hotspots + 1):
                hotspot_mask = labeled_hotspots == hotspot_id
                coords = np.where(hotspot_mask)
                if len(coords[0]) > 0:
                    # Use centroid as hotspot location
                    centroid = (int(np.mean(coords[0])), int(np.mean(coords[1])))
                    hotspots.append(centroid)
        else:
            # Simple approach: find all change pixels
            coords = np.where(binary_change)
            hotspots = list(zip(coords[0], coords[1]))

        # Calculate change statistics
        total_area = raster_t1.size
        changed_area = np.sum(binary_change)
        change_percentage = (changed_area / total_area) * 100

        mean_change_magnitude = (
            np.mean(change_magnitude[binary_change]) if changed_area > 0 else 0
        )
        max_change_magnitude = np.max(change_magnitude)

        change_stats = {
            "total_area": total_area,
            "changed_area": changed_area,
            "change_percentage": change_percentage,
            "mean_change_magnitude": mean_change_magnitude,
            "max_change_magnitude": max_change_magnitude,
            "n_hotspots": len(hotspots),
        }

        return ChangeDetectionResults(
            change_map=binary_change,
            change_magnitude=change_magnitude,
            change_direction=change_direction,
            hotspots=hotspots,
            change_statistics=change_stats,
        )

    def process_large_raster(
        self,
        raster: np.ndarray,
        processing_function: Callable,
        overlap: int = 50,
        **kwargs,
    ) -> np.ndarray:
        """
        Process large raster in chunks to manage memory usage.

        Parameters
        ----------
        raster : np.ndarray
            Large input raster
        processing_function : Callable
            Function to apply to each chunk
        overlap : int
            Overlap between chunks in pixels

        Returns
        -------
        np.ndarray
            Processed raster
        """
        if raster.size <= self.chunk_size**2:
            # Small enough to process directly
            return processing_function(raster, **kwargs)

        # Calculate chunk dimensions
        chunk_height = chunk_width = self.chunk_size

        # Initialize output raster
        output_raster = np.zeros_like(raster)

        # Process in chunks
        for i in range(0, raster.shape[0], chunk_height - overlap):
            for j in range(0, raster.shape[1], chunk_width - overlap):
                # Define chunk boundaries
                i_start = i
                i_end = min(i + chunk_height, raster.shape[0])
                j_start = j
                j_end = min(j + chunk_width, raster.shape[1])

                # Extract chunk
                chunk = raster[i_start:i_end, j_start:j_end]

                # Process chunk
                processed_chunk = processing_function(chunk, **kwargs)

                # Handle overlap regions
                if overlap > 0 and (i > 0 or j > 0):
                    # Blend overlapping regions
                    output_start_i = i_start + (overlap // 2 if i > 0 else 0)
                    output_end_i = i_end - (
                        overlap // 2 if i_end < raster.shape[0] else 0
                    )
                    output_start_j = j_start + (overlap // 2 if j > 0 else 0)
                    output_end_j = j_end - (
                        overlap // 2 if j_end < raster.shape[1] else 0
                    )

                    chunk_start_i = overlap // 2 if i > 0 else 0
                    chunk_end_i = processed_chunk.shape[0] - (
                        overlap // 2 if i_end < raster.shape[0] else 0
                    )
                    chunk_start_j = overlap // 2 if j > 0 else 0
                    chunk_end_j = processed_chunk.shape[1] - (
                        overlap // 2 if j_end < raster.shape[1] else 0
                    )

                    output_raster[
                        output_start_i:output_end_i, output_start_j:output_end_j
                    ] = processed_chunk[
                        chunk_start_i:chunk_end_i, chunk_start_j:chunk_end_j
                    ]
                else:
                    output_raster[i_start:i_end, j_start:j_end] = processed_chunk

        return output_raster
