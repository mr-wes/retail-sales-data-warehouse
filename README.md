# Retail Sales Data Warehouse



## Project Overview



This project builds a relational sales data warehouse using SQLite and Python. It transforms raw retail transaction data into a structured star schema to support business intelligence, sales analysis, and data-driven decision-making.



The warehouse contains customer, product, region, and date dimensions connected to a central sales fact table. An ETL pipeline cleans and validates source data before loading the warehouse, while SQL queries provide analytical insights into sales performance.



## Objectives



* Build a dimensional data warehouse using a star schema.

* Develop a reproducible ETL pipeline using Python and pandas.

* Implement data-quality checks and revenue reconciliation.

* Preserve valid transactions when descriptive fields are missing.

* Analyse revenue, product performance, customer segments, and regional sales.

* Validate warehouse integrity using SQLite constraints and foreign-key checks.



## Technology Stack



* **Python** â€” ETL development and data validation.

* **pandas** â€” CSV processing, data cleaning, and transformation.

* **SQLite** â€” relational data warehouse.

* **SQL** â€” analytical queries and business reporting.

* **PowerShell** â€” project execution and validation on Windows.



## Data Warehouse Architecture



The warehouse follows a star schema consisting of one fact table and four dimension tables.



```text

&#x20;                   dim\_date

&#x20;                      |

&#x20;                      |

dim\_customer ---- fact\_sales ---- dim\_product

&#x20;                      |

&#x20;                      |

&#x20;                  dim\_region

```



### Fact Table



**`fact\_sales`**



Stores transaction-level sales measures and foreign keys to the dimensions.



Key columns:



* `sales\_key`

* `order\_id`

* `date\_key`

* `customer\_key`

* `product\_key`

* `region\_key`

* `quantity`

* `unit\_price\_kes`

* `discount\_pct`

* `revenue\_kes`



Each order is uniquely identified by `order\_id`.



### Dimension Tables



| Table          | Purpose                                                          |

| -------------- | ---------------------------------------------------------------- |

| `dim\_date`     | Calendar date, year, month, month name, and quarter              |

| `dim\_customer` | Customer identifiers and customer segments                       |

| `dim\_product`  | Product identifiers, names, and categories                       |

| `dim\_region`   | Sales region names, including `Unknown` when a region is missing |



## Source Data



The pipeline reads the sample sales dataset from:



`../shared\_sample\_sales.csv`



The source includes order dates, customer details, product information, regions, quantities, unit prices, discounts, and revenue values in Kenyan shillings (KES).



The ETL process validates the required columns and converts dates and numeric fields to appropriate types.



## ETL Pipeline



The pipeline is implemented in `load\_warehouse.py`.



Its main stages are:



1\. **Extract** â€” read the source CSV file.

2\. **Validate** â€” check required columns, dates, transaction identifiers, and numeric values.

3\. **Deduplicate** â€” remove exact duplicate records.

4\. **Handle missing data** â€” replace missing descriptive values with `Unknown` where appropriate.

5\. **Recover revenue** â€” calculate missing revenue when quantity, unit price, and discount are available.

6\. **Validate calculations** â€” compare stored revenue against quantity multiplied by unit price and adjusted for discount.

7\. **Transform** â€” construct the date, customer, product, and region dimensions and map their keys into the fact table.

8\. **Load** â€” create a new SQLite warehouse and populate the dimension and fact tables.

9\. **Verify** â€” check fact-table row counts and foreign-key integrity before replacing the existing database.



The warehouse is rebuilt through a temporary database file. The temporary database is validated and closed before it replaces the destination database.



### Data-Quality Rules



* Exact duplicate records are removed.

* Transactions with missing required identifiers or invalid numeric values are excluded.

* Missing descriptive values, such as region, are replaced with `Unknown`.

* Missing revenue is recalculated only when the required inputs are available.

* Transactions with missing quantity are excluded when the quantity cannot be reliably recovered.

* Revenue mismatches greater than the configured tolerance cause the pipeline to fail.

* Foreign-key constraints are checked before the warehouse is accepted.



### Observed Data-Quality Results



| Check                                      | Result |

| ------------------------------------------ | -----: |

| Source records                             |    500 |

| Exact duplicate copies removed             |      1 |

| Transactions excluded for missing quantity |      1 |

| Missing revenue recovered                  |      1 |

| Transactions loaded                        |    498 |

| Revenue mismatches                         |      0 |

| Foreign-key violations                     |      0 |



The source contains one transaction with a missing region. Its transaction is retained using the `Unknown` region rather than discarded.



The duplicate order `O0067` is retained once. Order `O0016` is excluded because its quantity is missing and cannot be reliably determined from the available data. The missing revenue for `O0043` is recovered as KES 1,000.



## SQL Analytics



Analytical queries are stored in `queries.sql`.



The current query collection covers:



1\. Overall sales performance.

2\. Monthly revenue trends.

3\. Revenue by product category.

4\. Revenue by region.

5\. Best-selling products by units sold.

6\. Top products by revenue.

7\. Customer segment performance.

8\. Individual customer performance.

9\. Quarterly revenue.

10\. Regional transaction counts.

11\. Revenue reconciliation.

12\. Foreign-key validation.



## Business Insights



The following findings were calculated from the 498 transactions in the warehouse.



### Overall Sales Performance



| Metric              |           Result |

| ------------------- | ---------------: |

| Transactions        |              498 |

| Total revenue       | KES 3,560,990.00 |

| Units sold          |            2,287 |

| Average order value |     KES 7,150.58 |



### Monthly Performance



May was the strongest month in the available Januaryâ€“June 2026 data.



| Month    |        Revenue |

| -------- | -------------: |

| January  | KES 598,100.00 |

| February | KES 472,015.00 |

| March    | KES 565,762.50 |

| April    | KES 610,055.00 |

| May      | KES 777,420.00 |

| June     | KES 537,637.50 |



May generated KES 777,420 in revenue from 100 orders. June revenue declined compared with May, warranting further investigation into order volume and order values.



### Product Category Performance



| Category    |          Revenue |

| ----------- | ---------------: |

| Electronics | KES 2,257,580.00 |

| Accessories |   KES 910,080.00 |

| Lifestyle   |   KES 271,980.00 |

| Stationery  |   KES 121,350.00 |



Electronics was the leading category, contributing approximately 63.4% of total revenue.



### Product Performance



* **Highest revenue:** USB-C Hub â€” KES 1,193,440.

* **Second-highest revenue:** Keyboard â€” KES 1,064,140.

* **Highest units sold:** Notebook â€” 514 units.



These results demonstrate that the product with the highest unit sales is not necessarily the product with the highest revenue.



### Regional Performance



Nairobi generated the highest regional revenue at KES 866,212.50. Western had the highest number of orders, with 104 transactions.



### Customer Segment Performance



| Segment        |          Revenue |

| -------------- | ---------------: |

| Corporate      | KES 1,521,447.50 |

| Retail         | KES 1,367,947.50 |

| Small Business |   KES 671,595.00 |



Corporate customers generated the highest revenue and had the highest average order value among the three segments.



### Quarterly Performance



| Quarter |          Revenue |

| ------- | ---------------: |

| Q1 2026 | KES 1,635,877.50 |

| Q2 2026 | KES 1,925,112.50 |



Revenue increased by approximately 17.7% from Q1 to Q2. The available data covers January through June 2026, so these results do not represent the full calendar year.



## Project Structure



```text

02\_sales\_warehouse/

â”œâ”€â”€ load\_warehouse.py

â”œâ”€â”€ queries.sql

â”œâ”€â”€ README.md

â””â”€â”€ sales\_warehouse.db

```



The source CSV and shared Python virtual environment are located in the parent project directory.



## Running the Project



Run these commands from the `02\_sales\_warehouse` directory in PowerShell.



### 1. Build the warehouse



```powershell

\& "..\\.venv\\Scripts\\python.exe" .\\load\_warehouse.py

```



The script reads the source CSV, validates the records, and rebuilds `sales\_warehouse.db`.



### 2. Execute the analytical queries



Use the Python SQLite execution script to run the statements in `queries.sql` and display their results.



### 3. Validate the database



Check the fact-table row count:



```powershell

@'

import sqlite3



with sqlite3.connect("sales\_warehouse.db") as conn:

&#x20;   print("Fact rows:", conn.execute(

&#x20;       "SELECT COUNT(*) FROM fact\_sales"

&#x20;   ).fetchone()\[0])



&#x20;   print("Foreign-key violations:",

&#x20;         conn.execute("PRAGMA foreign\_key\_check").fetchall())

'@ | \& "..\\.venv\\Scripts\\python.exe" -

```



The validated database contains 498 fact rows and no foreign-key violations.



## Future Improvements



Potential extensions include:



* Automating scheduled ETL execution.

* Adding incremental loading instead of rebuilding the warehouse.

* Creating automated data-quality tests.

* Building a dashboard for monthly and regional performance.

* Adding more source data to support longer-term trend analysis.

* Introducing logging and structured ETL run reports.



## Conclusion



This project demonstrates an end-to-end data engineering workflow: extracting and cleaning raw sales data, applying data-quality rules, transforming it into a dimensional model, loading a SQLite warehouse, validating data integrity, and using SQL to generate actionable business insights.





