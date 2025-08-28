"""
EDA Visualizer - Creates visualizations for exploratory data analysis.

This module provides comprehensive visualization capabilities for EDA,
including statistical plots, distribution analysis, and correlation visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union
from ...utils.logger import get_logger


class EDAVisualizer:
    """
    Creates visualizations for exploratory data analysis.
    
    This class provides methods for generating various types of plots
    and visualizations to support data exploration and analysis.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (10, 6)):
        """
        Initialize the EDA Visualizer.
        
        Args:
            style: Matplotlib style to use
            figsize: Default figure size for plots
        """
        self.logger = get_logger(__name__)
        self.style = style
        self.figsize = figsize
        
        # Set plot style
        try:
            plt.style.use(style)
        except:
            self.logger.warning(f"Style '{style}' not available, using default")
        
        # Set seaborn defaults
        sns.set_palette("husl")
    
    def create_distribution_plots(self, df: pd.DataFrame, 
                                columns: Optional[List[str]] = None,
                                max_plots: int = 12) -> Dict[str, Any]:
        """
        Create distribution plots for numerical columns.
        
        Args:
            df: DataFrame to analyze
            columns: Specific columns to plot (default: all numerical)
            max_plots: Maximum number of plots to create
            
        Returns:
            Dictionary containing plot information
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            columns = columns[:max_plots]  # Limit number of plots
            
            if not columns:
                return {'message': 'No numerical columns found for distribution plots'}
            
            n_cols = min(3, len(columns))
            n_rows = (len(columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            plots_created = []
            
            for i, col in enumerate(columns):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                
                # Create histogram with KDE
                df[col].hist(bins=30, alpha=0.7, ax=ax, density=True)
                
                # Add KDE if possible
                try:
                    df[col].plot.kde(ax=ax, color='red', linewidth=2)
                except:
                    pass
                
                ax.set_title(f'Distribution of {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Density')
                ax.grid(True, alpha=0.3)
                
                plots_created.append(col)
            
            # Hide empty subplots
            for i in range(len(columns), len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'distribution',
                'columns_plotted': plots_created,
                'figure': fig
            }
            
        except Exception as e:
            self.logger.error(f"Error creating distribution plots: {str(e)}")
            return {'error': str(e)}
    
    def create_correlation_heatmap(self, df: pd.DataFrame, 
                                 columns: Optional[List[str]] = None,
                                 method: str = 'pearson') -> Dict[str, Any]:
        """
        Create correlation heatmap for numerical columns.
        
        Args:
            df: DataFrame to analyze
            columns: Specific columns to include
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Dictionary containing plot information
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(columns) < 2:
                return {'message': 'Need at least 2 numerical columns for correlation analysis'}
            
            # Calculate correlation matrix
            corr_matrix = df[columns].corr(method=method)
            
            # Create heatmap
            plt.figure(figsize=(max(8, len(columns)), max(6, len(columns) * 0.8)))
            
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            
            sns.heatmap(corr_matrix, 
                       mask=mask,
                       annot=True, 
                       cmap='coolwarm', 
                       center=0,
                       square=True,
                       fmt='.2f',
                       cbar_kws={"shrink": .8})
            
            plt.title(f'Correlation Heatmap ({method.title()})')
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'correlation_heatmap',
                'correlation_matrix': corr_matrix.to_dict(),
                'method': method,
                'columns_analyzed': columns
            }
            
        except Exception as e:
            self.logger.error(f"Error creating correlation heatmap: {str(e)}")
            return {'error': str(e)}
    
    def create_categorical_plots(self, df: pd.DataFrame,
                               columns: Optional[List[str]] = None,
                               max_plots: int = 8) -> Dict[str, Any]:
        """
        Create bar plots for categorical columns.
        
        Args:
            df: DataFrame to analyze
            columns: Specific columns to plot
            max_plots: Maximum number of plots to create
            
        Returns:
            Dictionary containing plot information
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            columns = columns[:max_plots]
            
            if not columns:
                return {'message': 'No categorical columns found'}
            
            n_cols = min(2, len(columns))
            n_rows = (len(columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 6, n_rows * 4))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            plots_created = []
            
            for i, col in enumerate(columns):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                
                # Get value counts
                value_counts = df[col].value_counts().head(10)  # Top 10 categories
                
                # Create bar plot
                value_counts.plot(kind='bar', ax=ax, color='skyblue', alpha=0.8)
                ax.set_title(f'Distribution of {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Count')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
                
                plots_created.append(col)
            
            # Hide empty subplots
            for i in range(len(columns), len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'categorical',
                'columns_plotted': plots_created,
                'figure': fig
            }
            
        except Exception as e:
            self.logger.error(f"Error creating categorical plots: {str(e)}")
            return {'error': str(e)}
    
    def create_scatter_plots(self, df: pd.DataFrame,
                           x_cols: Optional[List[str]] = None,
                           y_cols: Optional[List[str]] = None,
                           target_col: Optional[str] = None,
                           max_plots: int = 6) -> Dict[str, Any]:
        """
        Create scatter plots for numerical columns.
        
        Args:
            df: DataFrame to analyze
            x_cols: X-axis columns
            y_cols: Y-axis columns
            target_col: Target column for coloring
            max_plots: Maximum number of plots
            
        Returns:
            Dictionary containing plot information
        """
        try:
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if x_cols is None:
                x_cols = numerical_cols[:3]  # First 3 numerical columns
            if y_cols is None:
                y_cols = numerical_cols[1:4]  # Second to fourth numerical columns
            
            # Create pairs
            pairs = []
            for x_col in x_cols:
                for y_col in y_cols:
                    if x_col != y_col and (x_col, y_col) not in pairs and (y_col, x_col) not in pairs:
                        pairs.append((x_col, y_col))
            
            pairs = pairs[:max_plots]
            
            if not pairs:
                return {'message': 'No valid column pairs found for scatter plots'}
            
            n_cols = min(3, len(pairs))
            n_rows = (len(pairs) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            plots_created = []
            
            for i, (x_col, y_col) in enumerate(pairs):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                
                # Create scatter plot
                if target_col and target_col in df.columns:
                    # Color by target
                    if df[target_col].dtype in ['object', 'category']:
                        # Categorical target
                        for category in df[target_col].unique():
                            mask = df[target_col] == category
                            ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col], 
                                     label=str(category), alpha=0.6)
                        ax.legend()
                    else:
                        # Numerical target
                        scatter = ax.scatter(df[x_col], df[y_col], c=df[target_col], 
                                           alpha=0.6, cmap='viridis')
                        plt.colorbar(scatter, ax=ax, label=target_col)
                else:
                    ax.scatter(df[x_col], df[y_col], alpha=0.6, color='blue')
                
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f'{x_col} vs {y_col}')
                ax.grid(True, alpha=0.3)
                
                plots_created.append((x_col, y_col))
            
            # Hide empty subplots
            for i in range(len(pairs), len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'scatter',
                'pairs_plotted': plots_created,
                'target_column': target_col,
                'figure': fig
            }
            
        except Exception as e:
            self.logger.error(f"Error creating scatter plots: {str(e)}")
            return {'error': str(e)}
    
    def create_box_plots(self, df: pd.DataFrame,
                        numerical_cols: Optional[List[str]] = None,
                        categorical_col: Optional[str] = None,
                        max_plots: int = 6) -> Dict[str, Any]:
        """
        Create box plots for numerical columns grouped by categorical column.
        
        Args:
            df: DataFrame to analyze
            numerical_cols: Numerical columns to plot
            categorical_col: Categorical column for grouping
            max_plots: Maximum number of plots
            
        Returns:
            Dictionary containing plot information
        """
        try:
            if numerical_cols is None:
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if categorical_col is None:
                cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                categorical_col = cat_cols[0] if cat_cols else None
            
            if categorical_col is None:
                return {'message': 'No categorical column available for grouping'}
            
            numerical_cols = numerical_cols[:max_plots]
            
            n_cols = min(3, len(numerical_cols))
            n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            plots_created = []
            
            for i, num_col in enumerate(numerical_cols):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                
                # Create box plot
                df.boxplot(column=num_col, by=categorical_col, ax=ax)
                ax.set_title(f'{num_col} by {categorical_col}')
                ax.set_xlabel(categorical_col)
                ax.set_ylabel(num_col)
                
                plots_created.append(num_col)
            
            # Hide empty subplots
            for i in range(len(numerical_cols), len(axes)):
                axes[i].set_visible(False)
            
            plt.suptitle('')  # Remove default title
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'box',
                'columns_plotted': plots_created,
                'grouping_column': categorical_col,
                'figure': fig
            }
            
        except Exception as e:
            self.logger.error(f"Error creating box plots: {str(e)}")
            return {'error': str(e)}
    
    def create_missing_data_plot(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create visualization for missing data patterns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing plot information
        """
        try:
            # Calculate missing data
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
            
            if len(missing_data) == 0:
                return {'message': 'No missing data found'}
            
            # Create bar plot
            plt.figure(figsize=(10, 6))
            missing_data.plot(kind='bar', color='coral', alpha=0.8)
            plt.title('Missing Data by Column')
            plt.xlabel('Columns')
            plt.ylabel('Number of Missing Values')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            return {
                'plot_type': 'missing_data',
                'missing_counts': missing_data.to_dict(),
                'total_missing': missing_data.sum()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating missing data plot: {str(e)}")
            return {'error': str(e)}
    
    def create_comprehensive_eda_plots(self, df: pd.DataFrame,
                                     target_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a comprehensive set of EDA plots.
        
        Args:
            df: DataFrame to analyze
            target_col: Target column for supervised learning analysis
            
        Returns:
            Dictionary containing all plot information
        """
        try:
            self.logger.info("Creating comprehensive EDA plots")
            
            results = {}
            
            # Distribution plots
            dist_result = self.create_distribution_plots(df)
            results['distributions'] = dist_result
            
            # Correlation heatmap
            corr_result = self.create_correlation_heatmap(df)
            results['correlations'] = corr_result
            
            # Categorical plots
            cat_result = self.create_categorical_plots(df)
            results['categorical'] = cat_result
            
            # Missing data plot
            missing_result = self.create_missing_data_plot(df)
            results['missing_data'] = missing_result
            
            # Target-specific plots if target is provided
            if target_col and target_col in df.columns:
                # Scatter plots with target coloring
                scatter_result = self.create_scatter_plots(df, target_col=target_col)
                results['scatter_plots'] = scatter_result
                
                # Box plots grouped by target (if categorical) or vs numerical features
                if df[target_col].dtype in ['object', 'category']:
                    box_result = self.create_box_plots(df, categorical_col=target_col)
                    results['box_plots'] = box_result
            
            self.logger.info("Comprehensive EDA plots created successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error creating comprehensive EDA plots: {str(e)}")
            return {'error': str(e)}
