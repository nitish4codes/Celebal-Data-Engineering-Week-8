
-- BASIC QUERIES


-- 1. Total revenue per category
SELECT p.category AS "Category", 
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS "Total Revenue"
FROM cleaned_order_items oi
JOIN cleaned_products p ON oi.product_id = p.product_id
WHERE oi.quantity > 0
GROUP BY p.category;

-- 2. Top 10 customers by total order value
SELECT o.customer_id AS "Customer ID", 
       c.customer_name AS "Customer Name",
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS "Total Order Value"
FROM cleaned_orders o
JOIN cleaned_order_items oi ON o.order_id = oi.order_id
JOIN cleaned_customers c ON o.customer_id = c.customer_id
WHERE oi.quantity > 0 AND o.customer_id != 'UNKNOWN'
GROUP BY o.customer_id, c.customer_name
ORDER BY "Total Order Value" DESC
LIMIT 10;

-- 3. Month-wise order count for the last 12 months
SELECT strftime('%Y-%m', order_date) AS "Order Month",
       COUNT(order_id) AS "Total Orders"
FROM cleaned_orders
WHERE order_date >= DATE('now', '-12 months')
GROUP BY "Order Month"
ORDER BY "Order Month" DESC;


-- ==============================================================================
-- INTERMEDIATE QUERIES
-- ==============================================================================

-- 4. Find customers who placed orders but never had any item delivered
SELECT DISTINCT customer_id AS "Customer ID"
FROM cleaned_orders
WHERE customer_id != 'UNKNOWN'
EXCEPT
SELECT DISTINCT customer_id 
FROM cleaned_orders 
WHERE status = 'DELIVERED';

-- 5. Products that were ordered but had more returns than purchases
SELECT oi.product_id AS "Product ID",
       p.product_name AS "Product Name",
       SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS "Total Purchased",
       SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS "Total Returned"
FROM cleaned_order_items oi
JOIN cleaned_products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_name
HAVING "Total Returned" > "Total Purchased";

-- 6. Calculate the return rate (returned items / total items) per category
SELECT p.category AS "Category",
       SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS "Returned Items",
       SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS "Purchased Items",
       ROUND(SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) * 1.0 / 
             NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0), 4) AS "Return Rate"
FROM cleaned_order_items oi
JOIN cleaned_products p ON oi.product_id = p.product_id
GROUP BY p.category;


-- ==============================================================================
-- ADVANCED QUERIES (Window Functions, CTEs, Subqueries)
-- ==============================================================================

-- 7. Running Totals with Window Functions
WITH DailyRevenue AS (
    SELECT o.region_code, 
           DATE(o.order_date) AS order_date,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    WHERE oi.quantity > 0
    GROUP BY o.region_code, DATE(o.order_date)
)
SELECT region_code AS "Region Code", 
       order_date AS "Order Date", 
       ROUND(daily_revenue, 2) AS "Daily Revenue",
       ROUND(SUM(daily_revenue) OVER (PARTITION BY region_code ORDER BY order_date), 2) AS "Running Total"
FROM DailyRevenue;

-- 8. Ranking with DENSE_RANK
WITH ProductRevenue AS (
    SELECT p.category, 
           p.product_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM cleaned_order_items oi
    JOIN cleaned_products p ON oi.product_id = p.product_id
    WHERE oi.quantity > 0
    GROUP BY p.category, p.product_name
)
SELECT category AS "Category", 
       product_name AS "Product Name", 
       ROUND(total_revenue, 2) AS "Total Revenue",
       DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS "Rank In Category"
FROM ProductRevenue;

-- 9. LAG/LEAD Analysis
WITH OrderHistory AS (
    SELECT customer_id, 
           order_date,
           LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM cleaned_orders
    WHERE customer_id != 'UNKNOWN'
),
Gaps AS (
    SELECT customer_id, 
           order_date, 
           previous_order_date,
           JULIAN_DAY(order_date) - JULIAN_DAY(previous_order_date) AS days_gap
    FROM OrderHistory
)
SELECT customer_id AS "Customer ID", 
       order_date AS "Order Date", 
       previous_order_date AS "Previous Order Date", 
       ROUND(days_gap, 1) AS "Days Gap",
       CASE WHEN AVG(days_gap) OVER (PARTITION BY customer_id) > 30 THEN 'At Risk' ELSE 'Active' END AS "Status Flag"
FROM Gaps;

-- 10. CTE with Multiple Levels
WITH MonthlyCustRevenue AS (
    SELECT customer_id, 
           strftime('%Y-%m', order_date) AS order_month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    WHERE oi.quantity > 0 AND customer_id != 'UNKNOWN'
    GROUP BY customer_id, order_month
),
SegmentedCustomers AS (
    SELECT customer_id, 
           order_month,
           CASE WHEN revenue > 10000 THEN 'High'
                WHEN revenue BETWEEN 5000 AND 10000 THEN 'Medium'
                ELSE 'Low' END AS customer_segment
    FROM MonthlyCustRevenue
)
SELECT order_month AS "Order Month", 
       customer_segment AS "Customer Segment", 
       COUNT(customer_id) AS "Customer Count"
FROM SegmentedCustomers
GROUP BY "Order Month", "Customer Segment"
ORDER BY "Order Month" DESC, "Customer Segment" ASC;

-- 11. NTILE for Segmentation
WITH LifetimeValue AS (
    SELECT o.customer_id, 
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id != 'UNKNOWN' AND oi.quantity > 0
    GROUP BY o.customer_id
),
Quartiles AS (
    SELECT customer_id, 
           total_value,
           NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM LifetimeValue
)
SELECT customer_id AS "Customer ID", 
       ROUND(total_value, 2) AS "Total Value", 
       quartile AS "Quartile",
       CASE WHEN quartile = 1 THEN 'Platinum'
            WHEN quartile = 2 THEN 'Gold'
            WHEN quartile = 3 THEN 'Silver'
            ELSE 'Bronze' END AS "Quartile Label"
FROM Quartiles;

-- 12. Year-over-Year Comparison
WITH MonthlyRev AS (
    SELECT CAST(strftime('%Y', o.order_date) AS INTEGER) AS r_year,
           CAST(strftime('%m', o.order_date) AS INTEGER) AS r_month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    WHERE oi.quantity > 0
    GROUP BY r_year, r_month
)
SELECT curr.r_year AS "Year", 
       curr.r_month AS "Month", 
       ROUND(curr.revenue, 2) AS "Revenue",
       ROUND(prev.revenue, 2) AS "Prev Year Revenue",
       ROUND(((curr.revenue - COALESCE(prev.revenue, 0)) / NULLIF(prev.revenue, 0)) * 100, 2) AS "YoY Growth Percent"
FROM MonthlyRev curr
LEFT JOIN MonthlyRev prev ON curr.r_year = prev.r_year + 1 AND curr.r_month = prev.r_month;

-- 13. First/Last Value Analysis
WITH OrderedCategories AS (
    SELECT o.customer_id, 
           p.category, 
           o.order_date,
           FIRST_VALUE(p.category) OVER (PARTITION BY o.customer_id ORDER BY o.order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_cat,
           LAST_VALUE(p.category) OVER (PARTITION BY o.customer_id ORDER BY o.order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_cat
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    JOIN cleaned_products p ON oi.product_id = p.product_id
    WHERE o.customer_id != 'UNKNOWN'
)
SELECT DISTINCT customer_id AS "Customer ID", 
                first_cat AS "First Purchased Category", 
                last_cat AS "Most Recent Purchased Category",
                CASE WHEN first_cat != last_cat THEN 'Yes' ELSE 'No' END AS "Category Shift"
FROM OrderedCategories;

-- 14. Cumulative Distribution
WITH CustRevenue AS (
    SELECT o.customer_id, 
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM cleaned_orders o
    JOIN cleaned_order_items oi ON o.order_id = oi.order_id
    WHERE oi.quantity > 0 AND o.customer_id != 'UNKNOWN'
    GROUP BY o.customer_id
),
Total AS (
    SELECT SUM(revenue) AS global_revenue FROM CustRevenue
),
RunningCalculations AS (
    SELECT c.customer_id, 
           c.revenue,
           SUM(c.revenue) OVER (ORDER BY c.revenue DESC) AS cumulative_revenue
    FROM CustRevenue c
)
SELECT r.customer_id AS "Customer ID", 
       ROUND(r.revenue, 2) AS "Revenue", 
       ROUND(r.cumulative_revenue, 2) AS "Cumulative Revenue",
       ROUND((r.cumulative_revenue / t.global_revenue) * 100, 2) AS "Cumulative Percent"
FROM RunningCalculations r, Total t;

-- 15. Complex CTE: Cohort Analysis
WITH Cohorts AS (
    SELECT customer_id, 
           strftime('%Y-%m', registration_date) AS cohort_month
    FROM cleaned_customers
),
Activity AS (
    SELECT o.customer_id,
           (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', c.registration_date) AS INTEGER)) * 12 +
           (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', c.registration_date) AS INTEGER)) AS month_number
    FROM cleaned_orders o
    JOIN cleaned_customers c ON o.customer_id = c.customer_id
),
CohortSizes AS (
    SELECT cohort_month, 
           COUNT(customer_id) AS cohort_size 
    FROM Cohorts 
    GROUP BY cohort_month
)
SELECT c.cohort_month AS "Cohort Month",
       cs.cohort_size AS "Cohort Size",
       COUNT(DISTINCT CASE WHEN a.month_number = 0 THEN a.customer_id END) AS "Month 0 Active",
       COUNT(DISTINCT CASE WHEN a.month_number = 1 THEN a.customer_id END) AS "Month 1 Active",
       COUNT(DISTINCT CASE WHEN a.month_number = 2 THEN a.customer_id END) AS "Month 2 Active",
       COUNT(DISTINCT CASE WHEN a.month_number = 3 THEN a.customer_id END) AS "Month 3 Active"
FROM Cohorts c
JOIN CohortSizes cs ON c.cohort_month = cs.cohort_month
LEFT JOIN Activity a ON c.customer_id = a.customer_id
GROUP BY c.cohort_month, cs.cohort_size;       

-- 16. Self-Join with Window Function
SELECT a.product_id AS "Product A", 
       b.product_id AS "Product B",
       COUNT(*) AS "Times Bought Together"
FROM cleaned_order_items a
JOIN cleaned_order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY "Product A", "Product B"
ORDER BY "Times Bought Together" DESC;

