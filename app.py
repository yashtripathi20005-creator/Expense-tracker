# filename: app.py
"""
Expense Tracker with Charts - Main Application
Run this file to start the Streamlit dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import init_db, get_all_expenses, add_expense, delete_expense, get_expenses_by_date_range
from utils import format_currency, generate_summary_stats

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for adding expenses
with st.sidebar:
    st.markdown("## ➕ Add New Expense")
    
    with st.form("add_expense_form", clear_on_submit=True):
        description = st.text_input("Description", placeholder="e.g., Grocery shopping")
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, value=10.0)
        category = st.selectbox(
            "Category",
            ["Food & Dining", "Transportation", "Shopping", "Bills & Utilities", 
             "Entertainment", "Healthcare", "Education", "Travel", "Other"]
        )
        date = st.date_input("Date", datetime.now())
        
        submitted = st.form_submit_button("Add Expense")
        if submitted and description:
            add_expense(description, amount, category, date.strftime("%Y-%m-%d"))
            st.success("✅ Expense added successfully!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Filters")
    
    # Date range filter
    filter_option = st.radio(
        "Time Period",
        ["All Time", "This Month", "Last 3 Months", "This Year", "Custom"]
    )
    
    today = datetime.now().date()
    if filter_option == "This Month":
        start_date = today.replace(day=1)
        end_date = today
    elif filter_option == "Last 3 Months":
        start_date = today - timedelta(days=90)
        end_date = today
    elif filter_option == "This Year":
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif filter_option == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", today - timedelta(days=30))
        with col2:
            end_date = st.date_input("End", today)
    else:  # All Time
        start_date = None
        end_date = None

# Main content
st.markdown('<div class="main-header">💰 Expense Tracker Dashboard</div>', unsafe_allow_html=True)

# Fetch expenses with filters
if start_date and end_date:
    df = get_expenses_by_date_range(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    date_range_text = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
else:
    df = get_all_expenses()
    date_range_text = "All Time"

# Create two columns for stats
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate statistics
    total_expenses = df['amount'].sum()
    avg_expense = df['amount'].mean()
    total_transactions = len(df)
    most_common_category = df['category'].mode().iloc[0] if not df.empty else "N/A"
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{format_currency(total_expenses)}</div>
                <div class="stat-label">Total Expenses</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{format_currency(avg_expense)}</div>
                <div class="stat-label">Average Expense</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_transactions}</div>
                <div class="stat-label">Transactions</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{most_common_category}</div>
                <div class="stat-label">Top Category</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 📈 Expense Analysis ({date_range_text})")

    # Create tabs for different charts
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Category Breakdown", "📈 Daily Trends", "📉 Monthly Trends", "📋 All Transactions"])

    with tab1:
        # Pie chart - Category breakdown
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig_pie = px.pie(
                values=category_totals.values,
                names=category_totals.index,
                title="Spending by Category",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### Category Breakdown")
            for category, amount in category_totals.items():
                percentage = (amount / total_expenses) * 100
                st.metric(
                    label=category,
                    value=format_currency(amount),
                    delta=f"{percentage:.1f}%"
                )

    with tab2:
        # Line chart - Daily trends
        daily_totals = df.groupby('date')['amount'].sum().reset_index()
        daily_totals['date'] = pd.to_datetime(daily_totals['date'])
        daily_totals = daily_totals.sort_values('date')
        
        fig_line = px.line(
            daily_totals,
            x='date',
            y='amount',
            title="Daily Spending Trend",
            labels={'amount': 'Amount ($)', 'date': 'Date'},
            markers=True
        )
        fig_line.update_traces(line_color='#1f77b4', line_width=3)
        fig_line.update_layout(hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        # Bar chart - Monthly trends
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
        monthly_totals = df.groupby('month')['amount'].sum().reset_index()
        monthly_totals = monthly_totals.sort_values('month')
        
        fig_bar = px.bar(
            monthly_totals,
            x='month',
            y='amount',
            title="Monthly Spending",
            labels={'amount': 'Total ($)', 'month': 'Month'},
            color='amount',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Add month-over-month change
        if len(monthly_totals) > 1:
            monthly_totals['change'] = monthly_totals['amount'].pct_change() * 100
            st.markdown("#### Month-over-Month Change")
            for i in range(1, len(monthly_totals)):
                change = monthly_totals['change'].iloc[i]
                if not pd.isna(change):
                    arrow = "📈" if change > 0 else "📉"
                    color = "red" if change > 0 else "green"
                    st.markdown(
                        f"**{monthly_totals['month'].iloc[i]}**: {format_currency(monthly_totals['amount'].iloc[i])} "
                        f"({arrow} {change:.1f}%)"
                    )

    with tab4:
        # Display all transactions with delete option
        st.markdown("### 📋 All Transactions")
        
        # Search/filter
        search_term = st.text_input("🔍 Search transactions", placeholder="Search by description or category...")
        
        display_df = df.copy()
        if search_term:
            display_df = display_df[
                display_df['description'].str.contains(search_term, case=False) |
                display_df['category'].str.contains(search_term, case=False)
            ]
        
        # Format for display
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
        
        # Reorder columns
        display_df = display_df[['date', 'description', 'category', 'amount']]
        display_df.columns = ['Date', 'Description', 'Category', 'Amount']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.TextColumn("Amount", width="small"),
                "Category": st.column_config.TextColumn("Category", width="medium"),
            }
        )
        
        # Delete expense (by ID)
        st.markdown("#### 🗑️ Delete an Expense")
        expense_ids = df['id'].tolist()
        if expense_ids:
            id_to_delete = st.selectbox(
                "Select expense ID to delete",
                options=expense_ids,
                format_func=lambda x: f"ID: {x} - {df[df['id']==x]['description'].iloc[0]} (${df[df['id']==x]['amount'].iloc[0]:.2f})"
            )
            if st.button("Delete Selected Expense", type="primary"):
                delete_expense(id_to_delete)
                st.success(f"✅ Expense ID {id_to_delete} deleted successfully!")
                st.rerun()

else:
    st.info("📭 No expenses found. Add your first expense from the sidebar!", icon="ℹ️")
    
    # Show sample data button
    if st.button("📊 Load Sample Data"):
        sample_expenses = [
            ("Grocery Shopping", 85.50, "Food & Dining", (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")),
            ("Uber Ride", 25.00, "Transportation", (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")),
            ("Netflix Subscription", 15.99, "Entertainment", (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")),
            ("Electric Bill", 120.00, "Bills & Utilities", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")),
            ("Dinner at Restaurant", 45.75, "Food & Dining", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")),
            ("New Shoes", 89.99, "Shopping", datetime.now().strftime("%Y-%m-%d")),
            ("Doctor Visit", 150.00, "Healthcare", (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Flight Ticket", 350.00, "Travel", (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")),
        ]
        for desc, amt, cat, dt in sample_expenses:
            add_expense(desc, amt, cat, dt)
        st.success("✅ Sample data loaded!")
        st.rerun()

# Footer
st.markdown("---")
st.caption(f"💡 Expense Tracker v1.0 | Total expenses tracked: {len(df) if not df.empty else 0} transactions")
