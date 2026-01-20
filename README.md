# Sales Analytics System

**Student Name:** Preethi Ravisankar  
**Student ID:** BITSoM_BA_25071894  
**Email:** preethiravisankar@gmail.com  
**Date:** 20.01.2026  

## Project Overview

This project involves a Python-based Sales Analytics System that processes sales transaction data, performs validation and analysis, enriches data using an external product API, and generates a detailed analytics report.

## Repository Structure
sales-analytics-system/  
├── README.md  
├── main.py  
├── utils/  
│ ├── file_handler.py  
│ ├── data_processor.py  
│ └── api_handler.py  
├── data/  
│ └── sales_data.txt  
├── output/  
│ └── (generated reports and enriched files)  
└── requirements.txt  

## Technologies Used

- Python 3.x

## Generated outputs

- Enriched Sales Data  
data/enriched_sales_data.txt

- Sales Analytics Report  
output/sales_report.txt

## Note to reviewer

- In the provided sales data, the product id starts with 101,102... The json data has products with ids from 1 to 3. Hence the API match returns false in the enrichedsalesdata.txt. 

## Run Instructions

```bash
# Run main.py
python main.py
