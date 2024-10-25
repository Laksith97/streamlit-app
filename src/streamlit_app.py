import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import urllib.parse  # For URL encoding

# Database connection configuration
DB_CONFIG = {
    'user': 'root',
    'password': urllib.parse.quote_plus('La&Ra@97'),  # Safely encode the password
    'host': 'localhost',
    'db_name': 'delivergate'
}

def create_database_connection():
    """
    Creates a database connection using SQLAlchemy.
    """
    connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['db_name']}"
    engine = create_engine(connection_string)
    return engine

# Load data from the database
@st.cache_data
def load_data(_engine):
    customers_query = "SELECT * FROM customers"
    orders_query = """
        SELECT orders.order_id, orders.customer_id, orders.total_amount, orders.order_date, customers.customer_name 
        FROM orders JOIN customers ON orders.customer_id = customers.customer_id
    """
    customers = pd.read_sql(customers_query, _engine)
    orders = pd.read_sql(orders_query, _engine)
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    return customers, orders

# Main app function
def main():
    st.title("DeliverGate Customer and Order Dashboard")
    
    # Establish connection to the database
    engine = create_database_connection()
    
    # Load data
    customers, orders = load_data(engine)
    
    # Sidebar Filters
    st.sidebar.header("Filters")

    # Date Range Filter
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=[orders['order_date'].min(), orders['order_date'].max()]
    )
    
    # Filter orders by the selected date range
    if len(date_range) == 2 and date_range[0] <= date_range[1]:
        filtered_orders = orders[
            (orders['order_date'] >= pd.to_datetime(date_range[0])) & 
            (orders['order_date'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        filtered_orders = orders  # Show all orders if dates are not valid

    # Total Amount Slider Filters
    max_total_amount = filtered_orders['total_amount'].max()

    # Slider to filter orders by the range of total amount per order within the selected date range
    min_total_amount, max_spent = st.sidebar.slider(
        "Filter by order amount range:",
        min_value=0,
        max_value=int(max_total_amount),
        value=(0, int(max_total_amount)),  # Default to the full range
        format="$%d"
    )

    # Filter orders based on per-order total amount within the selected range
    filtered_orders = filtered_orders[
        (filtered_orders['total_amount'] >= min_total_amount) &
        (filtered_orders['total_amount'] <= max_spent)
    ]

    # Dropdown Filter: Customers with More Than X Orders
    order_count_threshold = st.sidebar.selectbox(
        "Filter customers with more than X orders:",
        options=range(1, 21),  # Range from 1 to 20
        index=4  # Default to 5
    )
    # Filter customers based on the number of orders within the filtered dataset
    customer_order_counts = filtered_orders['customer_id'].value_counts()
    eligible_customers = customer_order_counts[customer_order_counts > order_count_threshold].index
    filtered_orders = filtered_orders[filtered_orders['customer_id'].isin(eligible_customers)]

    # Check if any orders are left after filtering
    if filtered_orders.empty:
        st.warning("No orders match the selected filters.")
    else:
        # Main Dashboard Display
        st.header("Filtered Data")
        st.dataframe(filtered_orders)

        # Bar Chart - Top 10 Customers by Revenue
        st.header("Top 10 Customers by Total Revenue (Filtered)")
        top_customers = filtered_orders.groupby('customer_name')['total_amount'].sum().nlargest(10)
        st.bar_chart(top_customers)

        # Line Chart - Total Revenue Over Time (Filtered)
        st.header("Total Revenue Over Time (Filtered)")
        revenue_over_time = filtered_orders.resample('M', on='order_date')['total_amount'].sum()
        st.line_chart(revenue_over_time)

        # Updated Summary Metrics with a Modern View
        st.header("Summary Metrics")

        # Calculate metrics
        total_revenue = filtered_orders['total_amount'].sum()
        unique_customers = filtered_orders['customer_id'].nunique()
        total_orders = filtered_orders['order_id'].count()

        # Display metrics with gaps
        col1, spacer1, col2, spacer2, col3 = st.columns([1.2, 0.1, 0.8, 0.1, 0.8])
        
        col1.metric(label="💰 Total Revenue", value=f"${total_revenue:,.2f}")
        col2.metric(label="👥 Unique Customers", value=unique_customers)
        col3.metric(label="📦 Total Orders", value=total_orders)

if __name__ == "__main__":
    main()
