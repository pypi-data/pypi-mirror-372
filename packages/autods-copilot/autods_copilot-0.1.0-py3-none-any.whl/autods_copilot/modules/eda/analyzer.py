"""
EDA Analyzer - Exploratory Data Analysis for AutoDS.

This module provides comprehensive exploratory data analysis capabilities
including statistical summaries, data quality assessment, and insights generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from ...utils.logger import get_logger


class EDAAnalyzer:
    """
    Comprehensive Exploratory Data Analysis analyzer.
    
    This class provides methods for analyzing datasets to generate
    insights, identify patterns, and assess data quality.
    """
    
    def __init__(self):
        """Initialize the EDA Analyzer."""
        self.logger = get_logger(__name__)
    
    def analyze_dataset(self, df: pd.DataFrame, 
                       target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive EDA on a dataset.
        
        Args:
            df: DataFrame to analyze
            target_column: Optional target column for supervised learning analysis
            
        Returns:
            Dictionary containing comprehensive EDA results
        """
        try:
            self.logger.info("Starting comprehensive EDA analysis")
            
            results = {
                'basic_info': self._get_basic_info(df),
                'data_quality': self._assess_data_quality(df),
                'statistical_summary': self._get_statistical_summary(df),
                'correlation_analysis': self._analyze_correlations(df),
                'feature_analysis': self._analyze_features(df),
                'recommendations': []
            }
            
            # Target-specific analysis if target column is provided
            if target_column and target_column in df.columns:
                results['target_analysis'] = self._analyze_target(df, target_column)
                results['feature_target_relationships'] = self._analyze_feature_target_relationships(df, target_column)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            self.logger.info("EDA analysis completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in EDA analysis: {str(e)}")
            raise
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset."""
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality metrics."""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        return {
            'missing_values': {
                'total_missing_cells': missing_counts.sum(),
                'columns_with_missing': missing_counts[missing_counts > 0].to_dict(),
                'missing_percentages': missing_percentages[missing_percentages > 0].to_dict()
            },
            'completeness_score': (1 - missing_counts.sum() / (df.shape[0] * df.shape[1])) * 100,
            'columns_mostly_missing': missing_percentages[missing_percentages > 50].index.tolist(),
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _get_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical summary for numerical and categorical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        summary = {
            'numerical_summary': {},
            'categorical_summary': {}
        }
        
        # Numerical columns summary
        if len(numerical_cols) > 0:
            numerical_stats = df[numerical_cols].describe()
            
            for col in numerical_cols:
                col_data = df[col].dropna()
                summary['numerical_summary'][col] = {
                    'count': len(col_data),
                    'mean': float(col_data.mean()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'median': float(col_data.median()),
                    'skewness': float(col_data.skew()),
                    'kurtosis': float(col_data.kurtosis()),
                    'unique_values': int(col_data.nunique()),
                    'zeros_count': int((col_data == 0).sum()),
                    'outliers_iqr': self._count_outliers_iqr(col_data)
                }
        
        # Categorical columns summary
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                col_data = df[col].dropna()
                value_counts = col_data.value_counts()
                
                summary['categorical_summary'][col] = {
                    'count': len(col_data),
                    'unique_values': int(col_data.nunique()),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'cardinality': int(col_data.nunique()),
                    'top_categories': value_counts.head(10).to_dict()
                }
        
        return summary
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numerical features."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'message': 'Insufficient numerical columns for correlation analysis'}
        
        # Calculate correlation matrix
        corr_matrix = df[numerical_cols].corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.8:  # High correlation threshold
                    high_corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlations': high_corr_pairs,
            'avg_correlation': float(np.abs(corr_matrix.values).mean()),
            'max_correlation': float(np.abs(corr_matrix.values).max())
        }
    
    def _analyze_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual features for patterns and issues."""
        feature_analysis = {}
        
        for col in df.columns:
            col_data = df[col]
            analysis = {
                'dtype': str(col_data.dtype),
                'missing_count': int(col_data.isnull().sum()),
                'missing_percentage': float((col_data.isnull().sum() / len(col_data)) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float((col_data.nunique() / len(col_data)) * 100)
            }
            
            if col_data.dtype in [np.number]:
                # Numerical feature analysis
                col_clean = col_data.dropna()
                if len(col_clean) > 0:
                    analysis.update({
                        'mean': float(col_clean.mean()),
                        'std': float(col_clean.std()),
                        'skewness': float(col_clean.skew()),
                        'is_highly_skewed': abs(col_clean.skew()) > 2,
                        'outliers_count': self._count_outliers_iqr(col_clean),
                        'zeros_percentage': float((col_clean == 0).sum() / len(col_clean) * 100)
                    })
            else:
                # Categorical feature analysis
                analysis.update({
                    'cardinality': int(col_data.nunique()),
                    'is_high_cardinality': col_data.nunique() > 50,
                    'mode': col_data.mode().iloc[0] if len(col_data.mode()) > 0 else None,
                    'mode_frequency': float(col_data.value_counts().iloc[0] / len(col_data)) if len(col_data) > 0 else 0
                })
            
            feature_analysis[col] = analysis
        
        return feature_analysis
    
    def _analyze_target(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Analyze the target variable specifically."""
        target_series = df[target_column]
        
        analysis = {
            'column_name': target_column,
            'dtype': str(target_series.dtype),
            'missing_count': int(target_series.isnull().sum()),
            'unique_count': int(target_series.nunique())
        }
        
        # Determine task type
        if target_series.dtype in ['object', 'category', 'bool']:
            task_type = 'classification'
        elif target_series.nunique() / len(target_series.dropna()) < 0.05:
            task_type = 'classification'
        else:
            task_type = 'regression'
        
        analysis['task_type'] = task_type
        
        if task_type == 'classification':
            value_counts = target_series.value_counts()
            analysis.update({
                'num_classes': len(value_counts),
                'class_distribution': value_counts.to_dict(),
                'class_balance': {
                    'balanced': value_counts.max() / value_counts.min() < 3 if len(value_counts) > 1 else True,
                    'imbalance_ratio': float(value_counts.max() / value_counts.min()) if len(value_counts) > 1 else 1.0
                }
            })
        else:
            clean_target = target_series.dropna()
            analysis.update({
                'mean': float(clean_target.mean()),
                'std': float(clean_target.std()),
                'min': float(clean_target.min()),
                'max': float(clean_target.max()),
                'skewness': float(clean_target.skew()),
                'distribution_type': self._identify_distribution(clean_target)
            })
        
        return analysis
    
    def _analyze_feature_target_relationships(self, df: pd.DataFrame, 
                                            target_column: str) -> Dict[str, Any]:
        """Analyze relationships between features and target."""
        target_series = df[target_column]
        feature_cols = [col for col in df.columns if col != target_column]
        
        relationships = {}
        
        for feature in feature_cols:
            feature_series = df[feature]
            
            # Skip if too many missing values
            if feature_series.isnull().sum() / len(feature_series) > 0.5:
                continue
            
            relationship = {
                'feature_name': feature,
                'relationship_strength': 'weak'  # Default
            }
            
            # For numerical features
            if feature_series.dtype in [np.number] and target_series.dtype in [np.number]:
                # Calculate correlation
                corr = feature_series.corr(target_series)
                relationship.update({
                    'correlation': float(corr) if not np.isnan(corr) else 0.0,
                    'relationship_type': 'linear_correlation',
                    'relationship_strength': self._categorize_correlation(corr)
                })
            
            # For categorical feature vs numerical target
            elif feature_series.dtype in ['object', 'category'] and target_series.dtype in [np.number]:
                # ANOVA F-statistic
                try:
                    groups = [target_series[feature_series == cat].dropna() 
                             for cat in feature_series.unique() if pd.notna(cat)]
                    groups = [g for g in groups if len(g) > 1]  # Remove empty groups
                    
                    if len(groups) > 1:
                        f_stat, p_value = stats.f_oneway(*groups)
                        relationship.update({
                            'f_statistic': float(f_stat),
                            'p_value': float(p_value),
                            'relationship_type': 'categorical_vs_numerical',
                            'relationship_strength': 'strong' if p_value < 0.05 else 'weak'
                        })
                except:
                    pass
            
            # For categorical feature vs categorical target
            elif feature_series.dtype in ['object', 'category'] and target_series.dtype in ['object', 'category']:
                # Chi-square test
                try:
                    contingency_table = pd.crosstab(feature_series, target_series)
                    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                    
                    relationship.update({
                        'chi2_statistic': float(chi2),
                        'p_value': float(p_value),
                        'relationship_type': 'categorical_vs_categorical',
                        'relationship_strength': 'strong' if p_value < 0.05 else 'weak'
                    })
                except:
                    pass
            
            relationships[feature] = relationship
        
        return relationships
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on EDA results."""
        recommendations = []
        
        # Data quality recommendations
        data_quality = analysis_results.get('data_quality', {})
        missing_values = data_quality.get('missing_values', {})
        
        if missing_values.get('total_missing_cells', 0) > 0:
            recommendations.append("Handle missing values before modeling")
        
        if data_quality.get('duplicate_rows', 0) > 0:
            recommendations.append("Remove duplicate rows to improve data quality")
        
        # Feature analysis recommendations
        feature_analysis = analysis_results.get('feature_analysis', {})
        
        high_cardinality_features = [
            col for col, info in feature_analysis.items() 
            if info.get('is_high_cardinality', False)
        ]
        
        if high_cardinality_features:
            recommendations.append(f"Consider feature engineering for high cardinality features: {high_cardinality_features}")
        
        skewed_features = [
            col for col, info in feature_analysis.items() 
            if info.get('is_highly_skewed', False)
        ]
        
        if skewed_features:
            recommendations.append(f"Consider transformation for highly skewed features: {skewed_features}")
        
        # Correlation recommendations
        correlation_analysis = analysis_results.get('correlation_analysis', {})
        high_correlations = correlation_analysis.get('high_correlations', [])
        
        if high_correlations:
            recommendations.append("Consider removing highly correlated features to reduce multicollinearity")
        
        # Target analysis recommendations
        target_analysis = analysis_results.get('target_analysis', {})
        if target_analysis:
            if target_analysis.get('task_type') == 'classification':
                class_balance = target_analysis.get('class_balance', {})
                if not class_balance.get('balanced', True):
                    recommendations.append("Consider handling class imbalance using sampling techniques")
            elif target_analysis.get('task_type') == 'regression':
                if target_analysis.get('skewness', 0) > 2:
                    recommendations.append("Consider log transformation for the target variable")
        
        return recommendations
    
    def _count_outliers_iqr(self, series: pd.Series) -> int:
        """Count outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        return int(outliers)
    
    def _categorize_correlation(self, corr: float) -> str:
        """Categorize correlation strength."""
        if pd.isna(corr):
            return 'none'
        
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return 'strong'
        elif abs_corr >= 0.3:
            return 'moderate'
        else:
            return 'weak'
    
    def _identify_distribution(self, series: pd.Series) -> str:
        """Identify the likely distribution of a numerical series."""
        # Simple heuristic-based distribution identification
        skewness = series.skew()
        
        if abs(skewness) < 0.5:
            return 'normal'
        elif skewness > 1:
            return 'right_skewed'
        elif skewness < -1:
            return 'left_skewed'
        else:
            return 'slightly_skewed'
