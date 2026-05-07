"""
Enhanced Chart Generation for FinOps Reports
Includes environment comparisons, trends, pie charts, and anomaly highlights.
"""
from pathlib import Path
from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

from core.logger import setup_logger


logger = setup_logger(__name__)


class EnhancedChartGenerator:
    """Generate enhanced charts for cost analysis reports."""
    
    def __init__(self, output_dir: Path):
        """Initialize enhanced chart generator."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style to dark theme matching frontend
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': '#0f1115',
            'axes.facecolor': '#181b21',
            'axes.edgecolor': '#333333',
            'grid.color': '#333333',
            'text.color': '#e2e8f0',
            'axes.labelcolor': '#e2e8f0',
            'xtick.color': '#94a3b8',
            'ytick.color': '#94a3b8'
        })
        
        # Color palette
        self.colors = {
            'prod': '#2E86AB',
            'uat': '#A23B72',
            'dev': '#F18F01',
            'UNLABELED': '#C73E1D',
            'default': '#6C757D'
        }
    
    def create_env_comparison_chart(
        self,
        env_summary: pd.DataFrame,
        filename: str = "env_comparison.png"
    ) -> Path:
        """Create environment cost comparison bar chart."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            colors = [self.colors.get(env, self.colors['default']) 
                     for env in env_summary['env']]
            
            bars = ax.bar(env_summary['env'], env_summary['total_cost'], color=colors)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{height:,.0f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_title('Cost by Environment', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Environment', fontsize=11)
            ax.set_ylabel('Cost (₹)', fontsize=11)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Environment comparison chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating environment comparison chart: {e}")
            raise
    
    def create_7day_trend_chart(
        self,
        trends_df: pd.DataFrame,
        filename: str = "7day_trend.png"
    ) -> Path:
        """Create 7-day cost trend line chart by environment."""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for env in trends_df['env'].unique():
                env_data = trends_df[trends_df['env'] == env].sort_values('date')
                color = self.colors.get(env, self.colors['default'])
                ax.plot(env_data['date'], env_data['cost'], 
                       marker='o', label=env, color=color, linewidth=2)
            
            ax.set_title('7-Day Cost Trend by Environment', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=11)
            ax.set_ylabel('Cost (₹)', fontsize=11)
            ax.legend(loc='best', frameon=True, shadow=True)
            ax.grid(alpha=0.3)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"7-day trend chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating 7-day trend chart: {e}")
            raise

    
    def create_service_breakdown_pie(
        self,
        daily_df: pd.DataFrame,
        env: str,
        top_n: int = 8,
        filename: str = None
    ) -> Path:
        """Create service breakdown pie chart for specific environment."""
        try:
            if filename is None:
                filename = f"service_pie_{env}.png"
            
            env_data = daily_df[daily_df['env'] == env]
            service_costs = env_data.groupby('service')['cost'].sum().sort_values(ascending=False)
            
            # Top N + Others
            top_services = service_costs.head(top_n)
            if len(service_costs) > top_n:
                others = pd.Series({'Others': service_costs[top_n:].sum()})
                plot_data = pd.concat([top_services, others])
            else:
                plot_data = top_services
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors_list = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
            wedges, texts, autotexts = ax.pie(
                plot_data, 
                labels=plot_data.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors_list,
                textprops={'fontsize': 9}
            )
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'Service Cost Breakdown - {env}', 
                        fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Service pie chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating service pie chart: {e}")
            raise
    
    def create_top_resources_chart(
        self,
        daily_df: pd.DataFrame,
        top_n: int = 10,
        filename: str = "top_resources.png"
    ) -> Path:
        """Create top resources bar chart across all environments."""
        try:
            # Create resource identifier
            daily_df['resource'] = daily_df['app'] + ' (' + daily_df['env'] + ')'
            top_resources = daily_df.nlargest(top_n, 'cost')
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = [self.colors.get(env, self.colors['default']) 
                     for env in top_resources['env']]
            
            bars = ax.barh(range(len(top_resources)), top_resources['cost'], color=colors)
            ax.set_yticks(range(len(top_resources)))
            ax.set_yticklabels(top_resources['resource'], fontsize=9)
            
            # Add value labels
            for i, (bar, cost) in enumerate(zip(bars, top_resources['cost'])):
                ax.text(cost, i, f' ₹{cost:,.0f}', 
                       va='center', fontsize=9, fontweight='bold')
            
            ax.set_title(f'Top {top_n} Resources by Cost', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Cost (₹)', fontsize=11)
            ax.grid(axis='x', alpha=0.3)
            
            # Add legend for environments
            legend_patches = [mpatches.Patch(color=self.colors.get(env, self.colors['default']), 
                                            label=env) 
                            for env in top_resources['env'].unique()]
            ax.legend(handles=legend_patches, loc='lower right')
            
            plt.tight_layout()
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Top resources chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating top resources chart: {e}")
            raise
    
    def create_dod_change_chart(
        self,
        trends_df: pd.DataFrame,
        target_date: str,
        filename: str = "dod_changes.png"
    ) -> Path:
        """Create day-over-day change chart with anomaly highlights."""
        try:
            yesterday_data = trends_df[trends_df['date'] == target_date].copy()
            yesterday_data = yesterday_data.sort_values('dod_percent', ascending=True)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Color bars based on change (red for increase, green for decrease)
            colors = ['#27AE60' if x < 0 else '#E74C3C' if x > 10 else '#F39C12' 
                     for x in yesterday_data['dod_percent']]
            
            bars = ax.barh(yesterday_data['env'], yesterday_data['dod_percent'], color=colors)
            
            # Add value labels
            for bar, val in zip(bars, yesterday_data['dod_percent']):
                x_pos = val + (1 if val > 0 else -1)
                ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
                       f'{val:+.1f}%',
                       va='center', fontsize=10, fontweight='bold')
            
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax.set_title('Day-over-Day Cost Change by Environment', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Change (%)', fontsize=11)
            ax.grid(axis='x', alpha=0.3)
            
            # Add legend
            green_patch = mpatches.Patch(color='#27AE60', label='Decreased')
            orange_patch = mpatches.Patch(color='#F39C12', label='Increased (<10%)')
            red_patch = mpatches.Patch(color='#E74C3C', label='Increased (>10%)')
            ax.legend(handles=[green_patch, orange_patch, red_patch], loc='best')
            
            plt.tight_layout()
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"DoD change chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating DoD change chart: {e}")
            raise
    
    def create_budget_tracking_chart(
        self,
        env_summary: pd.DataFrame,
        budgets: dict,
        days_in_month: int,
        current_day: int,
        filename: str = "budget_tracking.png"
    ) -> Path:
        """Create budget tracking chart showing actual vs expected spend."""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = np.arange(len(env_summary))
            width = 0.25
            
            actual_costs = env_summary['total_cost'].values
            
            # Extract monthly budgets - handle both old format (float) and new format (dict)
            expected_costs = []
            monthly_budgets = []
            for env in env_summary['env']:
                env_budget = budgets.get(env, 0)
                if isinstance(env_budget, (int, float)):
                    monthly_budget = float(env_budget)
                elif isinstance(env_budget, dict):
                    monthly_budget = float(env_budget.get('monthly', 0))
                else:
                    monthly_budget = 0.0
                
                monthly_budgets.append(monthly_budget)
                expected_costs.append((monthly_budget / days_in_month) * current_day)
            
            bars1 = ax.bar(x - width, actual_costs, width, label='Actual (Today)', 
                          color='#2E86AB')
            bars2 = ax.bar(x, expected_costs, width, label='Expected (MTD)', 
                          color='#F39C12')
            bars3 = ax.bar(x + width, monthly_budgets, width, label='Monthly Budget', 
                          color='#27AE60', alpha=0.6)
            
            ax.set_xlabel('Environment', fontsize=11)
            ax.set_ylabel('Cost (₹)', fontsize=11)
            ax.set_title('Budget Tracking by Environment', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(env_summary['env'])
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Budget tracking chart saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating budget tracking chart: {e}")
            raise
