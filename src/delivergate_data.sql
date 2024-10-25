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

SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM customers;


drop table orders;
drop table customers;