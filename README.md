# streamlit-app
Streamlit App consists of data preparations, app setup and data analysis using python. 

## DeliverGate Streamlit Application

## Overview
This application provides a data engineering solution that imports customer and order data from CSV files into a MySQL database and visualizes the data using a Streamlit web application.
Also, included a machine learning model (logistic regression) that predicts whether a customer is a repeat purchaser based on their total orders and revenue.

## Project Structure
```
STREAMLIT APP
├── src
│   ├── data
│   │   ├── customers.csv
│   │   └── order.csv
│   ├── data_import.py
│   ├── delivergate_data.sql
│   ├── prediction_model.ipynb
│   ├── streamlit_app.py
│   ├── README.md
│   └── requirements.txt
```

## Requirements 
All requirements for database setup, streamlit-app setup, and model setup are icluded in the "requirements.txt" file.


## Support
For any issues or questions, please open an issue in the repository.