# filename: database.py
"""
Database operations for Expense Tracker
Uses SQLite for local storage
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "expenses.db"

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the expenses table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date ON expenses(date)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_category ON expenses(category)
    ''')
    
    conn.commit()
    conn.close()

def add_expense(description, amount, category, date):
    """Add a new expense to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (description, amount, category, date))
    
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return expense_id

def get_all_expenses():
    """Get all expenses as a pandas DataFrame"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    return df

def get_expenses_by_date_range(start_date, end_date):
    """Get expenses within a date range"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC",
        conn,
        params=(start_date, end_date)
    )
    conn.close()
    return df

def delete_expense(expense_id):
    """Delete an expense by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    return affected_rows > 0

def get_summary_stats():
    """Get summary statistics from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total expenses
    cursor.execute("SELECT COUNT(*) as total_transactions, SUM(amount) as total_amount, AVG(amount) as avg_amount FROM expenses")
    stats = cursor.fetchone()
    
    # Category breakdown
    cursor.execute("""
        SELECT category, COUNT(*) as count, SUM(amount) as total, AVG(amount) as avg
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)
    category_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_transactions': stats[0] or 0,
        'total_amount': stats[1] or 0.0,
        'avg_amount': stats[2] or 0.0,
        'category_stats': category_stats
    }

def clear_all_expenses():
    """Clear all expenses from the database (use with caution)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()

def get_monthly_trends():
    """Get monthly spending trends"""
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(amount) as total,
            COUNT(*) as count,
            AVG(amount) as avg
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
    """, conn)
    conn.close()
    return df

if __name__ == "__main__":
    # Test database operations
    init_db()
    print("Database initialized successfully!")
    
    # Add a test expense
    add_expense("Test Expense", 10.50, "Other", datetime.now().strftime("%Y-%m-%d"))
    print("Test expense added!")
    
    # Get all expenses
    df = get_all_expenses()
    print(f"Total expenses: {len(df)}")
    print(df.head())
