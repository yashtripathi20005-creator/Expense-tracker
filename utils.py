# filename: utils.py
"""
Utility functions for Expense Tracker
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:,.2f}"

def calculate_percentage(part, whole):
    """Calculate percentage with proper handling"""
    if whole == 0:
        return 0
    return (part / whole) * 100

def generate_summary_stats(df):
    """
    Generate summary statistics from expense DataFrame
    Returns dictionary with various statistics
    """
    if df.empty:
        return {
            'total_expenses': 0,
            'average_expense': 0,
            'max_expense': 0,
            'min_expense': 0,
            'total_transactions': 0,
            'categories': [],
            'most_common_category': 'None',
            'total_by_category': {},
            'daily_avg': 0,
            'weekly_avg': 0,
            'monthly_avg': 0
        }
    
    # Basic stats
    total = df['amount'].sum()
    avg = df['amount'].mean()
    max_exp = df['amount'].max()
    min_exp = df['amount'].min()
    count = len(df)
    
    # Category stats
    category_totals = df.groupby('category')['amount'].sum().to_dict()
    most_common = df['category'].mode().iloc[0] if not df.empty else 'None'
    
    # Time-based stats
    df['date'] = pd.to_datetime(df['date'])
    date_range = (df['date'].max() - df['date'].min()).days if len(df) > 1 else 1
    daily_avg = total / max(date_range, 1)
    weekly_avg = total / max((date_range / 7), 1)
    monthly_avg = total / max((date_range / 30), 1)
    
    return {
        'total_expenses': total,
        'average_expense': avg,
        'max_expense': max_exp,
        'min_expense': min_exp,
        'total_transactions': count,
        'categories': list(category_totals.keys()),
        'most_common_category': most_common,
        'total_by_category': category_totals,
        'daily_avg': daily_avg,
        'weekly_avg': weekly_avg,
        'monthly_avg': monthly_avg
    }

def add_custom_category(category_name, existing_categories):
    """Add a custom category if it doesn't exist"""
    if category_name not in existing_categories:
        return list(existing_categories) + [category_name]
    return existing_categories

def parse_date_range(date_string):
    """Parse common date range strings"""
    today = datetime.now().date()
    
    if date_string == 'today':
        start = today
        end = today
    elif date_string == 'week':
        start = today - timedelta(days=7)
        end = today
    elif date_string == 'month':
        start = today.replace(day=1)
        end = today
    elif date_string == 'quarter':
        month = today.month
        quarter_start_month = ((month - 1) // 3) * 3 + 1
        start = today.replace(month=quarter_start_month, day=1)
        end = today
    elif date_string == 'year':
        start = today.replace(month=1, day=1)
        end = today
    else:
        start = today - timedelta(days=30)
        end = today
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def export_to_csv(df, filename=None):
    """Export expense data to CSV"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_{timestamp}.csv"
    
    df.to_csv(filename, index=False)
    return filename

def import_from_csv(filename):
    """Import expense data from CSV"""
    try:
        df = pd.read_csv(filename)
        required_columns = ['description', 'amount', 'category', 'date']
        if all(col in df.columns for col in required_columns):
            return df
        else:
            raise ValueError("CSV must contain columns: description, amount, category, date")
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return None

def get_category_colors():
    """Get consistent color mapping for categories"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85929E', '#73C6B6'
    ]
    return colors

def calculate_budget_variance(actual, budget):
    """Calculate budget variance"""
    if budget == 0:
        return 0
    return ((actual - budget) / budget) * 100

def get_most_expensive_transactions(df, n=5):
    """Get the n most expensive transactions"""
    return df.nlargest(n, 'amount')[['date', 'description', 'category', 'amount']]

def get_frequent_categories(df, n=5):
    """Get the n most frequently used categories"""
    return df['category'].value_counts().head(n)
