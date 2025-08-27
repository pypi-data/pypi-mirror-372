"""
Test suite for Land Use Intensity Analysis package.

Tests the Pontius-Aldwaik intensity analysis methodology implementation.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add the package to path
package_path = Path(__file__).parent.parent / "landuse_intensity"
sys.path.insert(0, str(package_path))

import landuse_intensity as lui


class TestIntensityAnalysis:
    """Test the core intensity analysis functionality."""
    
    def test_demo_landscape_structure(self):
        """Test that demo landscape has correct structure."""
        demo_data = lui.demo_landscape()
        
        # Check required keys
        required_keys = ['lulc_Multistep', 'lulc_Onestep', 'tb_legend', 'totalArea', 'totalInterval']
        for key in required_keys:
            assert key in demo_data, f"Missing required key: {key}"
        
        # Check data types
        assert isinstance(demo_data['lulc_Multistep'], pd.DataFrame)
        assert isinstance(demo_data['lulc_Onestep'], pd.DataFrame)
        assert isinstance(demo_data['tb_legend'], pd.DataFrame)
        assert isinstance(demo_data['totalArea'], (int, float))
        assert isinstance(demo_data['totalInterval'], (int, float))
    
    def test_demo_landscape_columns(self):
        """Test that demo landscape has correct column structure."""
        demo_data = lui.demo_landscape()
        
        # Check lulc_Multistep columns
        expected_columns = ['Period', 'Year_from', 'Year_to', 'From', 'To', 'km2', 'QtPixel', 'Interval']
        lulc_columns = demo_data['lulc_Multistep'].columns.tolist()
        for col in expected_columns:
            assert col in lulc_columns, f"Missing column in lulc_Multistep: {col}"
        
        # Check legend columns
        legend_columns = ['CategoryValue', 'CategoryName', 'color']
        tb_columns = demo_data['tb_legend'].columns.tolist()
        for col in legend_columns:
            assert col in tb_columns, f"Missing column in tb_legend: {col}"
    
    def test_intensity_analysis_basic(self):
        """Test basic intensity analysis functionality."""
        demo_data = lui.demo_landscape()
        results = lui.intensity_analysis(demo_data)
        
        # Check result type
        assert isinstance(results, lui.IntensityAnalysis)
        
        # Check interval level
        assert hasattr(results, 'interval_level')
        assert isinstance(results.interval_level.St, pd.DataFrame)
        assert isinstance(results.interval_level.U, (int, float))
        
        # Check category levels
        assert hasattr(results, 'category_level_gain')
        assert hasattr(results, 'category_level_loss')
        assert isinstance(results.category_level_gain.data, pd.DataFrame)
        assert isinstance(results.category_level_loss.data, pd.DataFrame)
    
    def test_intensity_analysis_with_transitions(self):
        """Test intensity analysis with transition level analysis."""
        demo_data = lui.demo_landscape()
        
        # Get available categories
        categories = demo_data['tb_legend']['CategoryValue'].tolist()
        
        # Test with transition analysis
        results = lui.intensity_analysis(
            demo_data,
            category_n=categories[1],  # Second category for gains
            category_m=categories[0]   # First category for losses
        )
        
        # Check that results include transition levels (may be None if no data)
        assert hasattr(results, 'transition_level_gain')
        assert hasattr(results, 'transition_level_loss')


class TestUtilities:
    """Test utility functions."""
    
    def test_demo_landscape_reproducible(self):
        """Test that demo landscape is reproducible."""
        data1 = lui.demo_landscape()
        data2 = lui.demo_landscape()
        
        # Should be identical
        pd.testing.assert_frame_equal(data1['lulc_Multistep'], data2['lulc_Multistep'])
        pd.testing.assert_frame_equal(data1['tb_legend'], data2['tb_legend'])
        assert data1['totalArea'] == data2['totalArea']
        assert data1['totalInterval'] == data2['totalInterval']
    
    def test_get_transition_matrix(self):
        """Test transition matrix extraction."""
        demo_data = lui.demo_landscape()
        periods = demo_data['lulc_Multistep']['Period'].unique()
        
        for period in periods:
            matrix = lui.get_transition_matrix(demo_data, period)
            assert isinstance(matrix, pd.DataFrame)
            assert matrix.shape[0] == matrix.shape[1]  # Should be square
    
    def test_calculate_change_metrics(self):
        """Test change metrics calculation."""
        demo_data = lui.demo_landscape()
        periods = demo_data['lulc_Multistep']['Period'].unique()
        
        for period in periods:
            metrics = lui.calculate_change_metrics(demo_data, period)
            assert isinstance(metrics, pd.DataFrame)
            assert 'Category' in metrics.columns
            assert 'TotalChange' in metrics.columns


class TestVisualization:
    """Test visualization functions."""
    
    def test_plot_bar(self):
        """Test bar plot creation."""
        demo_data = lui.demo_landscape()
        
        fig = lui.plot_bar(
            demo_data['lulc_Multistep'],
            demo_data['tb_legend']
        )
        
        # Should return a matplotlib figure
        assert hasattr(fig, 'savefig')
    
    def test_netgross_plot(self):
        """Test net/gross plot creation."""
        demo_data = lui.demo_landscape()
        
        fig = lui.netgross_plot(
            demo_data['lulc_Multistep'],
            demo_data['tb_legend']
        )
        
        # Should return a matplotlib figure
        assert hasattr(fig, 'savefig')
    
    @pytest.mark.skipif(not hasattr(lui, 'plot_sankey'), reason="Sankey requires plotly")
    def test_plot_sankey(self):
        """Test Sankey plot creation (requires plotly)."""
        demo_data = lui.demo_landscape()
        
        try:
            fig = lui.plot_sankey(
                demo_data['lulc_Multistep'],
                demo_data['tb_legend']
            )
            # Should return a plotly figure
            assert hasattr(fig, 'write_html')
        except ImportError:
            pytest.skip("Plotly not available")


class TestDataValidation:
    """Test data validation and error handling."""
    
    def test_empty_dataset(self):
        """Test handling of empty datasets."""
        empty_dataset = {
            'lulc_Multistep': pd.DataFrame(),
            'tb_legend': pd.DataFrame(),
            'totalArea': 0,
            'totalInterval': 0
        }
        
        with pytest.raises((ValueError, IndexError)):
            lui.intensity_analysis(empty_dataset)
    
    def test_missing_keys(self):
        """Test handling of datasets with missing keys."""
        incomplete_dataset = {
            'lulc_Multistep': pd.DataFrame(),
            # Missing other required keys
        }
        
        with pytest.raises(KeyError):
            lui.intensity_analysis(incomplete_dataset)


if __name__ == "__main__":
    pytest.main([__file__])
