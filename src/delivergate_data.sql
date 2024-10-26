CREATE DATABASE IF NOT EXISTS delivergate;

USE delivergate;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT NOT NULL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT NOT NULL PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL COMMENT 'Amount in USD',
    order_date DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);


SELECT * FROM orders;
SELECT * FROM customers;

-- These insert into statements have placed in the data_import.py file within codes
INSERT INTO customers (customer_id, customer_name) 
VALUES (:customer_id, :customer_name);
INSERT INTO orders (order_id, customer_id, total_amount, order_date) 
VALUES (:order_id, :customer_id, :total_amount, :order_date);


SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM customers;


drop table orders;
drop table customers;