"""
Complete Intensity Analysis Implementation

This module provides a comprehensive implementation of the Pontius-Aldwaik
intensity analysis methodology, ported from the R function intensityAnalysis.

The analysis includes three levels:
1. Interval level: Examines change size and speed across time intervals
2. Category level: Examines gross gains and losses for each category
3. Transition level: Examines transition intensities between specific categories

Equations implemented:
- St: Interval change intensity
- U: Uniform intensity
- Gtj: Category gain intensity
- Lti: Category loss intensity
- Rtin: Transition gain intensity (from i to n)
- Wtn: Uniform intensity for gains to n
- Qtmj: Transition loss intensity (from m to j)
- Vtm: Uniform intensity for losses from m
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .core import ContingencyTable


@dataclass
class IntensityAnalysisResults:
    """Container for complete intensity analysis results."""
    
    lulc_table: pd.DataFrame
    interval_lvl: pd.DataFrame
    category_lvlGain: pd.DataFrame
    category_lvlLoss: pd.DataFrame
    transition_lvlGain_n: pd.DataFrame
    transition_lvlLoss_m: pd.DataFrame
    metadata: Dict[str, any]


def intensity_analysis(
    dataset: Dict,
    category_n: Union[str, int],
    category_m: Union[str, int], 
    area_km2: bool = True
) -> IntensityAnalysisResults:
    """
    Performs the intensity analysis based on cross-tabulation matrices of each time step.
    
    This function implements an Intensity Analysis (IA) according to Aldwaik & Pontius (2012),
    a quantitative method to analyze time series of land use and cover (LUC) maps.
    
    Parameters
    ----------
    dataset : dict
        Dataset containing contingency table data with structure:
        - dataset['transitions']: DataFrame with columns [Period, From, To, km2, QtPixel, Interval]
        - dataset['legend']: DataFrame with columns [categoryValue, categoryName, color]
        - dataset['total_area']: Total study area in km2
        - dataset['total_interval']: Total time interval in years
    category_n : str or int
        The gaining category for transition analysis
    category_m : str or int
        The losing category for transition analysis
    area_km2 : bool, default True
        If True, analysis in km2; if False, in pixel counts
        
    Returns
    -------
    IntensityAnalysisResults
        Complete intensity analysis results with all levels
    """
    
    # Extract data from dataset
    lulc_raw = dataset['transitions'].copy()
    legend = dataset['legend'].copy()
    AE = dataset['total_area']  # Study area in km2
    allinterval = dataset['total_interval']  # Total interval in years
    
    # Prepare LULC table with category names
    lulc = _prepare_lulc_table(lulc_raw, legend)
    
    # Choose area column based on area_km2 parameter
    area_col = 'km2' if area_km2 else 'QtPixel'
    pixel_col = 'QtPixel' if area_km2 else 'km2'  # For metadata
    
    if area_km2:
        # ==================== INTERVAL LEVEL ====================
        # EQ1 - St (Interval change intensity)
        eq1 = (lulc[lulc['From'] != lulc['To']]
               .groupby(['Period', 'Interval'])
               .agg(intch_km2=('km2', 'sum'))
               .reset_index())
        
        eq1['PercentChange'] = (eq1['intch_km2'] / AE) * 100
        eq1['St'] = (eq1['intch_km2'] / (eq1['Interval'] * AE)) * 100
        
        # EQ2 - U (Uniform intensity)
        total_change_all_periods = lulc[lulc['From'] != lulc['To']]['km2'].sum()
        eq2_value = (total_change_all_periods / (allinterval * AE)) * 100
        
        level01 = eq1.copy()
        level01['U'] = eq2_value
        
        # ==================== CATEGORY LEVEL ====================
        # EQ3 - Gtj (Category gain intensity)
        changed_data = lulc[lulc['From'] != lulc['To']]
        
        # Gross gains by period and category
        eq3_num = (changed_data
                  .groupby(['Period', 'To', 'Interval'])
                  .agg(GG_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area by period and category (end of period)
        eq3_denom = (lulc
                    .groupby(['Period', 'To'])
                    .agg(total_area=('km2', 'sum'))
                    .reset_index())
        
        eq3 = (eq3_num
              .merge(eq3_denom, on=['Period', 'To'], how='left')
              .merge(eq1[['Period', 'St']], on='Period', how='left'))
        
        eq3['Gtj'] = (eq3['GG_km2'] / (eq3['total_area'] * eq3['Interval'])) * 100
        
        # EQ4 - Lti (Category loss intensity)
        eq4_num = (changed_data
                  .groupby(['Period', 'From', 'Interval'])
                  .agg(GL_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area by period and category (beginning of period)
        eq4_denom = (lulc
                    .groupby(['Period', 'From'])
                    .agg(total_area=('km2', 'sum'))
                    .reset_index())
        
        eq4 = (eq4_num
              .merge(eq4_denom, on=['Period', 'From'], how='left')
              .merge(eq1[['Period', 'St']], on='Period', how='left'))
        
        eq4['Lti'] = (eq4['GL_km2'] / (eq4['total_area'] * eq4['Interval'])) * 100
        
        # ==================== TRANSITION LEVEL ====================
        # EQ5 - Rtin (Transition gain intensity from i to n)
        eq5_num = (changed_data[changed_data['To'] == category_n]
                  .groupby(['Period', 'From', 'Interval'])
                  .agg(T_i2n_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area of non-n categories at beginning of period
        eq5_denom = (lulc[(lulc['From'] != category_n)]
                    .groupby(['Period', 'From'])
                    .agg(total_non_n=('km2', 'sum'))
                    .reset_index())
        
        eq5 = eq5_num.merge(eq5_denom, on=['Period', 'From'], how='left')
        eq5['Rtin'] = (eq5['T_i2n_km2'] / (eq5['Interval'] * eq5['total_non_n'])) * 100
        
        # EQ6 - Wtn (Uniform intensity for gains to n)
        eq6_num = (changed_data[changed_data['To'] == category_n]
                  .groupby(['Period', 'To', 'Interval'])
                  .agg(GG_n_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area of non-n categories at beginning of period (all non-n)
        eq6_denom = (changed_data[changed_data['From'] != category_n]
                    .groupby('Period')
                    .agg(total_non_n_all=('km2', 'sum'))
                    .reset_index())
        
        eq6 = eq6_num.merge(eq6_denom, on='Period', how='left')
        eq6['Wtn'] = (eq6['GG_n_km2'] / (eq6['Interval'] * eq6['total_non_n_all'])) * 100
        
        # Combine EQ5 and EQ6 for gain analysis
        plot03ganho_n = (eq5
                        .merge(eq6[['Period', 'Wtn']], on='Period', how='left')
                        .merge(eq1[['Period', 'St']], on='Period', how='left'))
        
        # EQ7 - Qtmj (Transition loss intensity from m to j)
        eq7_num = (changed_data[changed_data['From'] == category_m]
                  .groupby(['Period', 'To', 'Interval'])
                  .agg(T_m2j_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area of non-m categories at end of period
        eq7_denom = (lulc[(lulc['To'] != category_m)]
                    .groupby(['Period', 'To'])
                    .agg(total_non_m=('km2', 'sum'))
                    .reset_index())
        
        eq7 = eq7_num.merge(eq7_denom, on=['Period', 'To'], how='left')
        eq7['Qtmj'] = (eq7['T_m2j_km2'] / (eq7['Interval'] * eq7['total_non_m'])) * 100
        
        # EQ8 - Vtm (Uniform intensity for losses from m)
        eq8_num = (changed_data[changed_data['From'] == category_m]
                  .groupby(['Period', 'From', 'Interval'])
                  .agg(GL_m_km2=('km2', 'sum'))
                  .reset_index())
        
        # Total area of non-m categories at end of period (all non-m)
        eq8_denom = (changed_data[changed_data['To'] != category_m]
                    .groupby('Period')
                    .agg(total_non_m_all=('km2', 'sum'))
                    .reset_index())
        
        eq8 = eq8_num.merge(eq8_denom, on='Period', how='left')
        eq8['Vtm'] = (eq8['GL_m_km2'] / (eq8['Interval'] * eq8['total_non_m_all'])) * 100
        
        # Combine EQ7 and EQ8 for loss analysis
        plot03perda_m = (eq7
                        .merge(eq8[['Period', 'Vtm']], on='Period', how='left')
                        .merge(eq1[['Period', 'St']], on='Period', how='left'))
        
    else:
        # Pixel-based analysis (similar structure but using QtPixel)
        # Implementation would be similar but using pixel counts
        # For brevity, using km2 version as default
        raise NotImplementedError("Pixel-based analysis not yet implemented")
    
    # ==================== STATIONARITY TESTS ====================
    # Level 2: Category stationarity
    st_lv2_gain = _calculate_category_stationarity(eq3, 'gain')
    st_lv2_loss = _calculate_category_stationarity(eq4, 'loss')
    
    # Level 3: Transition stationarity
    st_gain_n = _calculate_transition_stationarity(plot03ganho_n, 'gain', category_n)
    st_loss_m = _calculate_transition_stationarity(plot03perda_m, 'loss', category_m)
    
    # Create lookup color dictionary
    lookupcolor = dict(zip(legend['categoryName'], legend['color']))
    
    # Create results object
    results = IntensityAnalysisResults(
        lulc_table=lulc,
        interval_lvl=level01,
        category_lvlGain=eq3,
        category_lvlLoss=eq4,
        transition_lvlGain_n=plot03ganho_n,
        transition_lvlLoss_m=plot03perda_m,
        metadata={
            'category_n': category_n,
            'category_m': category_m,
            'area_km2': area_km2,
            'total_area_km2': AE,
            'total_interval_years': allinterval,
            'uniform_intensity_U': eq2_value,
            'lookup_colors': lookupcolor,
            'category_stationarity_gain': st_lv2_gain,
            'category_stationarity_loss': st_lv2_loss,
            'transition_stationarity_gain_n': st_gain_n,
            'transition_stationarity_loss_m': st_loss_m
        }
    )
    
    return results


def _prepare_lulc_table(lulc_raw: pd.DataFrame, legend: pd.DataFrame) -> pd.DataFrame:
    """Prepare LULC table with category names instead of codes."""
    
    # Create lookup dictionaries
    code_to_name = dict(zip(legend['categoryValue'], legend['categoryName']))
    
    # Replace codes with names
    lulc = lulc_raw.copy()
    lulc['From'] = lulc['From'].map(code_to_name)
    lulc['To'] = lulc['To'].map(code_to_name)
    
    # Ensure Period is treated as ordered factor (sort by period)
    lulc['Period'] = pd.Categorical(lulc['Period'], 
                                   categories=sorted(lulc['Period'].unique(), reverse=True),
                                   ordered=True)
    
    return lulc


def _calculate_category_stationarity(eq_data: pd.DataFrame, analysis_type: str) -> pd.DataFrame:
    """Calculate stationarity for category level analysis."""
    
    category_col = 'To' if analysis_type == 'gain' else 'From'
    intensity_col = 'Gtj' if analysis_type == 'gain' else 'Lti'
    
    # Group by category and calculate stationarity
    stationarity = []
    
    for category in eq_data[category_col].unique():
        cat_data = eq_data[eq_data[category_col] == category]
        
        # Active: intensity > uniform intensity (St)
        active_periods = (cat_data[intensity_col] > cat_data['St']).sum()
        
        # Dormant: intensity < uniform intensity (St)  
        dormant_periods = (cat_data[intensity_col] < cat_data['St']).sum()
        
        n_periods = len(cat_data)
        
        stationarity.append({
            'Category': category,
            'Active': active_periods,
            'Dormant': dormant_periods,
            'N_Periods': n_periods,
            'Stationarity_Type': analysis_type.title(),
            'Test_Stationary': 'Y' if active_periods == n_periods or dormant_periods == n_periods else 'N'
        })
    
    return pd.DataFrame(stationarity)


def _calculate_transition_stationarity(eq_data: pd.DataFrame, analysis_type: str, target_category) -> pd.DataFrame:
    """Calculate stationarity for transition level analysis."""
    
    intensity_cols = {
        'gain': ('Rtin', 'Wtn'),
        'loss': ('Qtmj', 'Vtm')
    }
    
    intensity_col, uniform_col = intensity_cols[analysis_type]
    from_col = 'From' if analysis_type == 'gain' else 'To'
    
    # Group by source category and calculate stationarity
    stationarity = []
    
    for category in eq_data[from_col].unique():
        cat_data = eq_data[eq_data[from_col] == category]
        
        # Targeted: intensity > uniform intensity
        targeted_periods = (cat_data[intensity_col] > cat_data[uniform_col]).sum()
        
        # Avoided: intensity < uniform intensity
        avoided_periods = (cat_data[intensity_col] < cat_data[uniform_col]).sum()
        
        n_periods = len(cat_data)
        
        stationarity.append({
            'Category': category,
            'Targeted': targeted_periods,
            'Avoided': avoided_periods,
            'N_Periods': n_periods,
            'Target_Category': target_category,
            'Stationarity_Type': f'{analysis_type.title()} from/to {target_category}',
            'Test_Stationary': 'Y' if targeted_periods == n_periods or avoided_periods == n_periods else 'N'
        })
    
    return pd.DataFrame(stationarity)


# Convenience function for quick analysis
def analyze_intensity_from_contingency_table(
    ct: 'ContingencyTable',
    category_n: Union[str, int],
    category_m: Union[str, int],
    area_km2: bool = True
) -> IntensityAnalysisResults:
    """
    Convenience function to perform intensity analysis from ContingencyTable object.
    
    Parameters
    ----------
    ct : ContingencyTable
        ContingencyTable object with analysis data
    category_n : str or int
        The gaining category for transition analysis
    category_m : str or int
        The losing category for transition analysis
    area_km2 : bool, default True
        If True, analysis in km2; if False, in pixel counts
        
    Returns
    -------
    IntensityAnalysisResults
        Complete intensity analysis results
    """
    
    # Convert ContingencyTable to dataset format expected by intensity_analysis
    if ct.get_summary_stats()['is_onestep_only']:
        transitions = ct.lulc_Onestep.copy()
    else:
        # For multistep, use the overall transitions
        transitions = ct.lulc_Onestep.copy()
    
    # Prepare legend
    legend = ct.tb_legend.copy() if hasattr(ct, 'tb_legend') else pd.DataFrame()
    
    # Prepare dataset
    dataset = {
        'transitions': transitions,
        'legend': legend,
        'total_area': ct.totalArea['area_km2'].iloc[0] if hasattr(ct, 'totalArea') else transitions['km2'].sum(),
        'total_interval': ct.totalInterval if hasattr(ct, 'totalInterval') else 1
    }
    
    return intensity_analysis(dataset, category_n, category_m, area_km2)
