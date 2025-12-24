#!/usr/bin/env python3
"""
Data Analysis Script

Performs comprehensive data analysis on CSV/Excel files including:
- Data exploration and profiling
- Statistical analysis
- Visualizations
- Automated insights

Usage:
    python analyze.py --file data.csv [OPTIONS]

Examples:
    # Basic analysis
    python analyze.py --file sales_data.csv
    
    # With custom output
    python analyze.py --file sales_data.csv --output report.html
    
    # Specify date column
    python analyze.py --file timeseries.csv --date-column date
"""

import argparse
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def load_data(file_path: str) -> pd.DataFrame:
    """Load data from CSV or Excel file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f"Loading data from {file_path}...")
    
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    print(f"✓ Loaded {len(df):,} rows and {len(df.columns)} columns\n")
    return df


def explore_data(df: pd.DataFrame) -> dict:
    """Perform initial data exploration."""
    print("="*60)
    print("DATA EXPLORATION")
    print("="*60)
    
    exploration = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum()
    }
    
    print(f"\nShape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Duplicate rows: {exploration['duplicates']:,}")
    
    # Missing values
    missing = pd.Series(exploration['missing'])
    missing = missing[missing > 0]
    if len(missing) > 0:
        print("\nMissing values:")
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count:,} ({pct:.1f}%)")
    else:
        print("\n✓ No missing values")
    
    # Data types
    print("\nData types:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")
    
    return exploration


def statistical_summary(df: pd.DataFrame) -> dict:
    """Generate statistical summaries."""
    print("\n" + "="*60)
    print("STATISTICAL SUMMARY")
    print("="*60 + "\n")
    
    # Numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print("Numeric columns:")
        print(df[numeric_cols].describe())
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print("\n\nCategorical columns:")
        for col in categorical_cols:
            unique_count = df[col].nunique()
            print(f"\n  {col}: {unique_count} unique values")
            if unique_count <= 10:
                value_counts = df[col].value_counts()
                for val, count in value_counts.items():
                    pct = (count / len(df)) * 100
                    print(f"    {val}: {count:,} ({pct:.1f}%)")
    
    return {
        'numeric_summary': df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
        'categorical_summary': {col: df[col].value_counts().to_dict() for col in categorical_cols}
    }


def create_visualizations(df: pd.DataFrame, output_dir: Path):
    """Create visualizations."""
    print("\n" + "="*60)
    print("CREATING VISUALIZATIONS")
    print("="*60 + "\n")
    
    output_dir.mkdir(exist_ok=True)
    
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        print("No numeric columns to visualize")
        return
    
    # Distribution plots for numeric columns
    for col in numeric_cols[:5]:  # Limit to first 5 columns
        plt.figure()
        df[col].hist(bins=30, edgecolor='black')
        plt.title(f'Distribution of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        filename = output_dir / f'dist_{col.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Created {filename}")
    
    # Correlation heatmap
    if len(numeric_cols) > 1:
        plt.figure(figsize=(12, 8))
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Correlation Matrix')
        filename = output_dir / 'correlation_heatmap.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Created {filename}")
    
    # Box plots for numeric columns
    if len(numeric_cols) <= 5:
        plt.figure(figsize=(12, 6))
        df[numeric_cols].boxplot()
        plt.title('Box Plots of Numeric Variables')
        plt.xticks(rotation=45, ha='right')
        filename = output_dir / 'boxplots.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Created {filename}")


def generate_insights(df: pd.DataFrame, exploration: dict, stats: dict) -> list:
    """Generate automated insights."""
    insights = []
    
    # Dataset size insights
    row_count = df.shape[0]
    if row_count < 100:
        insights.append(f"⚠️  Small dataset ({row_count:,} rows) - results may not be statistically significant")
    elif row_count > 1_000_000:
        insights.append(f"📊 Large dataset ({row_count:,} rows) - consider sampling for faster analysis")
    
    # Missing data insights
    missing = pd.Series(exploration['missing'])
    missing_pct = (missing / len(df) * 100)
    high_missing = missing_pct[missing_pct > 20]
    if len(high_missing) > 0:
        insights.append(f"⚠️  {len(high_missing)} column(s) have >20% missing data: {', '.join(high_missing.index)}")
    
    # Duplicate insights
    if exploration['duplicates'] > 0:
        pct = (exploration['duplicates'] / len(df)) * 100
        insights.append(f"⚠️  Found {exploration['duplicates']:,} duplicate rows ({pct:.1f}%)")
    
    # Correlation insights
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        high_corr = []
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                if abs(corr.iloc[i, j]) > 0.7:
                    high_corr.append((corr.columns[i], corr.columns[j], corr.iloc[i, j]))
        
        if high_corr:
            insights.append(f"📈 Found {len(high_corr)} strong correlation(s):")
            for col1, col2, val in high_corr[:3]:  # Show top 3
                insights.append(f"   • {col1} ↔ {col2}: {val:.2f}")
    
    return insights


def generate_report(df: pd.DataFrame, exploration: dict, stats: dict, 
                   insights: list, output_file: Path):
    """Generate HTML report."""
    print("\n" + "="*60)
    print("GENERATING REPORT")
    print("="*60 + "\n")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .insight {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
            .warning {{ border-left-color: #ff9800; }}
            img {{ max-width: 100%; height: auto; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>Data Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Dataset Overview</h2>
        <ul>
            <li><strong>Rows:</strong> {df.shape[0]:,}</li>
            <li><strong>Columns:</strong> {df.shape[1]}</li>
            <li><strong>Memory Usage:</strong> {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB</li>
            <li><strong>Duplicate Rows:</strong> {exploration['duplicates']:,}</li>
        </ul>
        
        <h2>Key Insights</h2>
    """
    
    for insight in insights:
        warning_class = 'warning' if '⚠️' in insight else ''
        html += f'<div class="insight {warning_class}">{insight}</div>\n'
    
    html += """
        <h2>Statistical Summary</h2>
        <h3>Numeric Columns</h3>
    """
    
    if stats['numeric_summary']:
        html += df.describe().to_html()
    
    html += """
        <h2>Visualizations</h2>
        <p>See the 'visualizations' folder for generated charts.</p>
    </body>
    </html>
    """
    
    output_file.write_text(html)
    print(f"✓ Report saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze CSV/Excel data files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--file', '-f', required=True, help='Input data file (CSV or Excel)')
    parser.add_argument('--output', '-o', default='analysis_report.html', help='Output report file')
    parser.add_argument('--date-column', help='Name of date column for time series analysis')
    parser.add_argument('--viz-dir', default='visualizations', help='Directory for visualizations')
    
    args = parser.parse_args()
    
    try:
        # Load data
        df = load_data(args.file)
        
        # Convert date column if specified
        if args.date_column and args.date_column in df.columns:
            df[args.date_column] = pd.to_datetime(df[args.date_column])
            print(f"✓ Converted '{args.date_column}' to datetime\n")
        
        # Explore data
        exploration = explore_data(df)
        
        # Statistical summary
        stats = statistical_summary(df)
        
        # Create visualizations
        viz_dir = Path(args.viz_dir)
        create_visualizations(df, viz_dir)
        
        # Generate insights
        print("\n" + "="*60)
        print("KEY INSIGHTS")
        print("="*60 + "\n")
        insights = generate_insights(df, exploration, stats)
        for insight in insights:
            print(insight)
        
        # Generate report
        output_file = Path(args.output)
        generate_report(df, exploration, stats, insights, output_file)
        
        print("\n" + "="*60)
        print("✓ ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nResults:")
        print(f"  Report: {output_file}")
        print(f"  Visualizations: {viz_dir}/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
