# Retail Sales Data Warehouse

A data engineering and analytics project that transforms raw retail sales data into a structured SQLite data warehouse and delivers business insights through SQL analytics and an interactive Power BI dashboard.

## Project Overview

This project demonstrates an end-to-end retail data workflow, from raw CSV ingestion and data cleaning to dimensional modelling, analytical SQL queries, and business intelligence reporting.

The warehouse enables analysis of sales performance across products, customers, regions, and time.

### Objectives

* Build a reliable ETL pipeline for retail sales data.
* Clean and validate source data before loading it into the warehouse.
* Design a dimensional data model for analytical queries.
* Store structured sales data in SQLite.
* Use SQL to answer business questions about revenue, transactions, products, and customers.
* Develop an interactive Power BI dashboard for business reporting.

## Technology Stack

* **Python:** ETL development and data processing.
* **SQLite:** Data warehouse storage.
* **SQL:** Data analysis and business reporting.
* **Power BI Desktop:** Interactive dashboard and visual analytics.
* **CSV:** Source data and Power BI table exports.
* **Git and GitHub:** Version control and project sharing.

## Project Structure

```text
02_sales_warehouse/
│
├── load_warehouse.py
├── queries.sql
├── run_queries.py
├── sales_warehouse.db
├── Retail_Sales_Dashboard.pbix
├── README.md
├── .gitignore
│
└── powerbi_data/
    ├── fact_sales.csv
    ├── dim_date.csv
    ├── dim_product.csv
    ├── dim_customer.csv
    └── dim_region.csv
```

The SQLite database and Power BI exports are generated project assets. The Python scripts implement the ETL and analytical workflows.

## Data Pipeline

The project follows an Extract, Transform, Load (ETL) process.

### 1. Extract

The pipeline reads the raw retail sales data from a CSV source.

### 2. Transform

The transformation process includes data quality checks and cleaning operations:

* Identifying duplicate orders.
* Handling records with missing required quantities.
* Recovering missing revenue where sufficient information is available.
* Validating revenue calculations.
* Preparing consistent keys and records for warehouse loading.

### 3. Load

The cleaned data is loaded into a SQLite database organised around a fact table and supporting dimension tables.

### 4. Analyse

SQL queries are executed against the warehouse to produce sales metrics and business insights.

### 5. Visualise

The warehouse tables are exported to CSV and imported into Power BI to create an interactive sales dashboard.

## Data Warehouse Design

The warehouse uses a dimensional model with a central fact table and four dimension tables.

### Fact Table

**`fact_sales`**

Stores sales transaction measures and references to the associated dimensions.

Key fields include:

* `order_id`
* `date_key`
* `product_key`
* `customer_key`
* `region_key`
* `quantity`
* `revenue_kes`

### Dimension Tables

| Table          | Purpose                                                        |
| -------------- | -------------------------------------------------------------- |
| `dim_date`     | Supports time-based sales analysis.                            |
| `dim_product`  | Provides product attributes for product and category analysis. |
| `dim_customer` | Supports customer segment analysis.                            |
| `dim_region`   | Provides regional information for geographical analysis.       |

The fact table connects to the dimension tables through their respective keys. This design supports analytical queries without repeatedly processing the original raw CSV.

## Data Quality and Validation

The ETL pipeline was validated against the source dataset.

| Validation Check                     | Result |
| ------------------------------------ | -----: |
| Source records                       |    500 |
| Duplicate records removed            |      1 |
| Record excluded for missing quantity |      1 |
| Missing revenue recovered            |      1 |
| Final transactions                   |    498 |
| Revenue mismatches                   |      0 |
| Foreign key violations               |      0 |

The duplicate order identified during cleaning was `O0067`. The record excluded because of a missing quantity was `O0016`. Missing revenue was recovered for `O0043`, resulting in revenue of KES 1,000.

These checks help ensure that the warehouse contains consistent transaction records and that its relationships remain valid.

## SQL Analytics

The project includes a collection of analytical SQL queries in `queries.sql`, executed through `run_queries.py`.

The analyses cover sales performance across multiple business dimensions, including:

* Total revenue and transaction counts.
* Units sold and average order value.
* Monthly revenue trends.
* Revenue by product category.
* Revenue by region.
* Sales by customer segment.
* Product performance by revenue and quantity.
* Comparisons between reporting periods.

The queries support both operational reporting and higher-level business analysis.

## Key Business Findings

The validated warehouse produced the following results.

### Overall Performance

| Metric              |        Result |
| ------------------- | ------------: |
| Total Revenue       | KES 3,560,990 |
| Total Transactions  |           498 |
| Units Sold          |         2,287 |
| Average Order Value |  KES 7,150.58 |

Average order value is calculated by dividing total revenue by the number of distinct transactions.

### Revenue by Product Category

| Category    |       Revenue |
| ----------- | ------------: |
| Electronics | KES 2,257,580 |
| Accessories |   KES 910,080 |
| Lifestyle   |   KES 271,980 |
| Stationery  |   KES 121,350 |

Electronics generated the highest revenue among the four product categories.

### Revenue by Month

| Month         |        Revenue |
| ------------- | -------------: |
| January 2026  |    KES 598,100 |
| February 2026 |    KES 472,015 |
| March 2026    | KES 565,762.50 |
| April 2026    |    KES 610,055 |
| May 2026      |    KES 777,420 |
| June 2026     | KES 537,637.50 |

May recorded the highest monthly revenue in the reporting period.

### Quarterly Comparison

| Quarter |          Revenue |
| ------- | ---------------: |
| Q1 2026 | KES 1,635,877.50 |
| Q2 2026 | KES 1,925,112.50 |

Revenue increased by approximately 17.7% from Q1 to Q2 2026.

### Additional Findings

* Nairobi generated the highest regional revenue at KES 866,212.50.
* Western recorded the highest transaction count, with 104 transactions.
* USB-C Hub generated the highest product revenue at KES 1,193,440.
* Notebook recorded the highest units sold, with 514 units.
* The Corporate customer segment generated the highest revenue at KES 1,521,447.50.

These findings describe the processed dataset and should not automatically be interpreted as forecasts of future sales.

## Power BI Dashboard

The project includes an interactive Power BI report built using the warehouse data.

**Dashboard file:** `Retail_Sales_Dashboard.pbix`

Open this file using Power BI Desktop.

### Dashboard Features

The report includes KPI cards for:

* Total Revenue.
* Total Transactions.
* Units Sold.
* Average Order Value.

It also includes visual analysis of:

* Revenue by product category.
* Revenue by region.
* Revenue by customer segment.

Interactive slicers allow users to filter the report by:

* Region.
* Product category.
* Date.

The slicers allow users to explore the data under different filtering conditions and examine how sales performance changes across the selected dimensions.

### Power BI Data Exports

The `powerbi_data/` directory contains CSV exports of the warehouse tables:

* `fact_sales.csv`
* `dim_date.csv`
* `dim_product.csv`
* `dim_customer.csv`
* `dim_region.csv`

These files provide the data used by the Power BI report.

They are exported snapshots rather than live connections to the SQLite database. If the warehouse data changes, regenerate the exports and refresh the Power BI report to reflect the updated data.

## Running the Project

Run these commands from the project directory in PowerShell.

### 1. Run the ETL Pipeline

If the project's virtual environment is located in the parent directory, run:

```powershell
& "..\.venv\Scripts\python.exe" .\load_warehouse.py
```

This runs the warehouse loading process. Review the script's output to confirm that processing and validation complete successfully.

### 2. Execute the SQL Analytics

```powershell
& "..\.venv\Scripts\python.exe" .\run_queries.py
```

This runs the analytical queries defined in `queries.sql`.

### 3. Open the Power BI Dashboard

Open `Retail_Sales_Dashboard.pbix` in Power BI Desktop.

To refresh the report after regenerating the CSV exports, use Power BI Desktop's refresh functionality and confirm that the imported files point to the correct `powerbi_data/` directory.

**Note:** These commands assume the Python virtual environment is located in the parent directory as `.venv`.
## Repository Notes

* `.gitignore` excludes virtual environments, Python cache files, temporary files, and selected local backup files.
* The Power BI report and CSV exports are included as project deliverables.
* The SQLite database is the local warehouse used by the analytical workflow.
* Regenerate dependent exports and refresh the report when the underlying warehouse data changes.

## Future Improvements

Potential extensions to the project include:

* Automating ETL execution and data refreshes.
* Adding automated data quality tests.
* Expanding the analytical SQL library.
* Adding incremental loading for new sales records.
* Improving documentation of the warehouse schema.
* Introducing scheduled Power BI refreshes through a suitable deployment setup.

## Author

**GitHub:** [mr-wes](https://github.com/mr-wes)


