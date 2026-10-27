-- ============================================================
-- SALES DATA WAREHOUSE: BUSINESS ANALYTICS
-- Database: SQLite
-- Revenue currency: KES
-- ============================================================


-- 1. OVERALL SALES PERFORMANCE
-- Summary of revenue, orders, units sold, and average order value.

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(revenue_kes), 2) AS total_revenue_kes,
    ROUND(SUM(quantity), 0) AS total_units_sold,
    ROUND(AVG(revenue_kes), 2) AS average_order_value_kes
FROM fact_sales;


-- 2. MONTHLY REVENUE TRENDS
-- Revenue, order volume, and units sold by month.

SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes,
    ROUND(SUM(f.quantity), 0) AS units_sold
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- 3. REVENUE BY PRODUCT CATEGORY
-- Identifies the highest-revenue product categories.

SELECT
    p.category,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.quantity), 0) AS units_sold,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.category
ORDER BY
    revenue_kes DESC;


-- 4. REVENUE BY REGION
-- Compares sales performance across regions.

SELECT
    r.region_name,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes,
    ROUND(AVG(f.revenue_kes), 2) AS average_order_value_kes
FROM fact_sales f
JOIN dim_region r
    ON f.region_key = r.region_key
GROUP BY
    r.region_name
ORDER BY
    revenue_kes DESC;


-- 5. BEST-SELLING PRODUCTS BY UNITS
-- Ranks products by total quantity sold.

SELECT
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(f.quantity), 0) AS units_sold,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY
    units_sold DESC,
    revenue_kes DESC;


-- 6. TOP PRODUCTS BY REVENUE
-- Identifies products generating the most revenue.

SELECT
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes,
    ROUND(SUM(f.quantity), 0) AS units_sold
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY
    revenue_kes DESC
LIMIT 10;


-- 7. CUSTOMER SEGMENT PERFORMANCE
-- Compares revenue and order value by customer segment.

SELECT
    c.customer_segment,
    COUNT(*) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes,
    ROUND(AVG(f.revenue_kes), 2) AS average_order_value_kes
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_segment
ORDER BY
    revenue_kes DESC;


-- 8. INDIVIDUAL CUSTOMER PERFORMANCE
-- Ranks customers by lifetime revenue within the available dataset.

SELECT
    c.customer_id,
    c.customer_segment,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.revenue_kes), 2) AS total_revenue_kes,
    ROUND(AVG(f.revenue_kes), 2) AS average_order_value_kes
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_id,
    c.customer_segment
ORDER BY
    total_revenue_kes DESC;


-- 9. QUARTERLY REVENUE
-- Summarizes performance by calendar quarter.

SELECT
    d.year,
    d.quarter,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes,
    ROUND(SUM(f.quantity), 0) AS units_sold
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.quarter
ORDER BY
    d.year,
    d.quarter;


-- 10. DATA QUALITY: TRANSACTION COUNTS BY REGION
-- Confirms that the Unknown region is retained in the warehouse.

SELECT
    r.region_name,
    COUNT(*) AS total_orders,
    ROUND(SUM(f.revenue_kes), 2) AS revenue_kes
FROM fact_sales f
JOIN dim_region r
    ON f.region_key = r.region_key
GROUP BY
    r.region_name
ORDER BY
    total_orders DESC;


-- 11. REVENUE RECONCILIATION
-- Compares stored revenue against quantity, price, and discount.
-- A result of zero indicates no mismatches within the 0.01 tolerance.

SELECT
    COUNT(*) AS total_orders,
    SUM(
        CASE
            WHEN ABS(
                f.revenue_kes -
                (f.quantity * f.unit_price_kes * (1 - f.discount_pct))
            ) > 0.01
            THEN 1
            ELSE 0
        END
    ) AS revenue_mismatches
FROM fact_sales f;


-- 12. FOREIGN-KEY VALIDATION
-- Run separately in SQLite; PRAGMA is not a SELECT query.

PRAGMA foreign_key_check;
