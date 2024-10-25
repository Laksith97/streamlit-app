import pandas as pd
from sqlalchemy import create_engine, exc, text
import urllib.parse

"""
This script imports customer and order data from CSV files into a MySQL database.
It handles data cleaning, validation, and ensures referential integrity between customers and orders.
"""

def create_database_connection(user, password, host, db_name):
    """
    Creates a database connection using the provided credentials.
    Returns connection and transaction objects.
    """
    try:
        # Encode password to handle special characters
        encoded_password = urllib.parse.quote_plus(password)
        connection_string = f"mysql+pymysql://{user}:{encoded_password}@{host}/{db_name}"
        engine = create_engine(connection_string)
        connection = engine.connect()
        transaction = connection.begin()
        return connection, transaction
    except exc.SQLAlchemyError as e:
        print(f"Failed to connect to database: {str(e)}")
        raise

def get_table_counts(connection):
    """
    Retrieves current record counts from customers and orders tables.
    """
    customer_count = connection.execute(text("SELECT COUNT(*) FROM customers")).scalar()
    order_count = connection.execute(text("SELECT COUNT(*) FROM orders")).scalar()
    return customer_count, order_count

def process_customer_data(df):
    """
    Cleans and processes customer data:
    - Selects required columns
    - Removes records with null names
    - Converts customer_id to integer
    """
    processed_df = df[['customer_id', 'name']].rename(columns={'name': 'customer_name'})
    processed_df = processed_df.dropna(subset=['customer_name'])
    processed_df['customer_id'] = processed_df['customer_id'].astype(int)
    return processed_df

def process_order_data(df):
    """
    Cleans and processes order data:
    - Selects required columns
    - Converts date strings to datetime
    - Removes records with null values
    - Converts customer_id to integer
    """
    # Select and rename columns
    processed_df = df[['id', 'total_amount', 'created_at', 'customer_id']]
    processed_df.rename(columns={'id': 'order_id', 'created_at': 'order_date'}, inplace=True)
    
    # Convert and clean data
    processed_df['order_date'] = pd.to_datetime(processed_df['order_date'], errors='coerce')
    processed_df = processed_df.dropna(subset=['order_date', 'customer_id', 'total_amount'])
    processed_df['customer_id'] = processed_df['customer_id'].astype(int)
    return processed_df

def insert_customers(connection, customers_df):
    """
    Inserts customer records into the database.
    Returns count of successful and failed insertions.
    """
    successful = 0
    failed = 0

    for _, row in customers_df.iterrows():
        try:
            customer_data = {
                "customer_id": int(row['customer_id']),
                "customer_name": row['customer_name']
            }
            query = text("INSERT INTO customers (customer_id, customer_name) VALUES (:customer_id, :customer_name)")
            connection.execute(query, customer_data)
            successful += 1
        except exc.SQLAlchemyError as e:
            if "Duplicate entry" in str(e):
                print(f"Customer ID {row['customer_id']} already exists, skipping...")
            else:
                print(f"Error inserting customer ID {row['customer_id']}: {e}")
            failed += 1
    
    return successful, failed

def insert_orders(connection, orders_df):
    """
    Inserts order records into the database.
    Returns count of successful and failed insertions.
    """
    successful = 0
    failed = 0

    for _, row in orders_df.iterrows():
        try:
            order_data = {
                "order_id": int(row['order_id']),
                "customer_id": int(row['customer_id']),
                "total_amount": float(row['total_amount']),
                "order_date": row['order_date']
            }
            query = text("INSERT INTO orders (order_id, customer_id, total_amount, order_date) VALUES (:order_id, :customer_id, :total_amount, :order_date)")
            connection.execute(query, order_data)
            successful += 1
        except exc.SQLAlchemyError as e:
            print(f"Error inserting order ID {row['order_id']}: {e}")
            failed += 1
    
    return successful, failed

def main():
    """
    Main function to orchestrate the data import process.
    """
    # Database credentials
    DB_CONFIG = {
        'user': 'root',
        'password': 'La&Ra@97',
        'host': 'localhost',
        'db_name': 'delivergate'
    }

    connection = None
    transaction = None

    try:
        # Establish database connection
        connection, transaction = create_database_connection(**DB_CONFIG)
        print("Database connection successful.")
        
        # Get initial table counts
        initial_customer_count, initial_order_count = get_table_counts(connection)
        print(f"\nInitial counts - Customers: {initial_customer_count}, Orders: {initial_order_count}")

        # Read CSV files
        customers_df = pd.read_csv("data/customers.csv")
        orders_df = pd.read_csv("data/order.csv")
        
        print(f"\nData from CSV files:")
        print(f"Customers in CSV: {len(customers_df)}")
        print(f"Orders in CSV: {len(orders_df)}")

        # Process data
        customers_df = process_customer_data(customers_df)
        orders_df = process_order_data(orders_df)

        # Filter valid orders (orders with existing customer IDs)
        valid_customer_ids = set(customers_df['customer_id'].unique())
        valid_orders_df = orders_df[orders_df['customer_id'].isin(valid_customer_ids)]
        invalid_orders_df = orders_df[~orders_df['customer_id'].isin(valid_customer_ids)]

        print(f"\nProcessed data:")
        print(f"Valid customers to insert: {len(customers_df)}")
        print(f"Valid orders to insert: {len(valid_orders_df)}")
        print(f"Invalid orders (skipped): {len(invalid_orders_df)}")

        # Insert data
        successful_customers, failed_customers = insert_customers(connection, customers_df)
        successful_orders, failed_orders = insert_orders(connection, valid_orders_df)

        # Commit changes
        transaction.commit()
        print("\nTransaction committed successfully.")

        # Verify final counts
        final_customer_count, final_order_count = get_table_counts(connection)
        
        # Print summary
        print(f"\nFinal Database Counts:")
        print(f"Customers: {final_customer_count} (Added: {final_customer_count - initial_customer_count})")
        print(f"Orders: {final_order_count} (Added: {final_order_count - initial_order_count})")

        print(f"\nImport Summary:")
        print(f"Customers - Successful: {successful_customers}, Failed: {failed_customers}")
        print(f"Orders - Successful: {successful_orders}, Failed: {failed_orders}, Skipped: {len(invalid_orders_df)}")

    except exc.SQLAlchemyError as e:
        if transaction:
            transaction.rollback()
            print("\nTransaction rolled back due to error!")
        print("Database error:", str(e))
    except Exception as e:
        if transaction:
            transaction.rollback()
            print("\nTransaction rolled back due to error!")
        print("General error:", str(e))
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()