-- dim_date
CREATE TABLE IF NOT EXISTS dim_date (
  date_sk      INT PRIMARY KEY,          -- yyyymmdd
  date_actual  DATE NOT NULL,
  day_of_month TINYINT,
  month_num    TINYINT,
  month_name   VARCHAR(20),
  quarter_num  TINYINT,
  year_num     INT,
  is_weekend   TINYINT(1)
) ENGINE=InnoDB;

-- dim_customer (SCD1 for now)
CREATE TABLE IF NOT EXISTS dim_customer (
  customer_sk   BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id   VARCHAR(20) NOT NULL UNIQUE,
  customer_name VARCHAR(45),
  segment       VARCHAR(20),
  KEY idx_customer_id (customer_id)
) ENGINE=InnoDB;

-- dim_product (SCD1)
CREATE TABLE IF NOT EXISTS dim_product (
  product_sk    BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_id    VARCHAR(20) NOT NULL UNIQUE,
  product_name  VARCHAR(150),
  category      VARCHAR(35),
  sub_category  VARCHAR(35),
  KEY idx_product_id (product_id),
  KEY idx_product_cat (category, sub_category)
) ENGINE=InnoDB;

-- dim_geography
CREATE TABLE IF NOT EXISTS dim_geography (
  geo_sk      BIGINT AUTO_INCREMENT PRIMARY KEY,
  postal_code VARCHAR(20),
  city        VARCHAR(35),
  _state      VARCHAR(20),
  region      VARCHAR(10),
  country     VARCHAR(15),
  KEY idx_geo_city (city, _state, country),
  KEY idx_geo_postal (postal_code)
) ENGINE=InnoDB;

-- dim_shipping (from ship_mode only)
CREATE TABLE IF NOT EXISTS dim_shipping (
  shipping_sk  BIGINT AUTO_INCREMENT PRIMARY KEY,
  ship_mode    VARCHAR(20) UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS fact_order_items (
  order_item_sk   BIGINT AUTO_INCREMENT PRIMARY KEY,
  -- degenerate/business keys
  order_id        VARCHAR(20) NOT NULL,
  row_id          INT NOT NULL,
  -- dates (role-playing)
  order_date_sk   INT NOT NULL,
  ship_date_sk    INT,
  -- FKs
  customer_sk     BIGINT NOT NULL,
  product_sk      BIGINT NOT NULL,
  geo_sk          BIGINT,
  shipping_sk     BIGINT,
  -- measures straight from source
  quantity        INT,
  sales           DECIMAL(19,4),
  discount        DECIMAL(5,2),
  profit          DECIMAL(19,4),
  -- indexes
  KEY idx_order (order_id),
  KEY idx_row (row_id),
  KEY idx_dates (order_date_sk, ship_date_sk),
  KEY idx_fk_customer (customer_sk),
  KEY idx_fk_product (product_sk),
  KEY idx_fk_geo (geo_sk),
  KEY idx_fk_shipping (shipping_sk),
  CONSTRAINT fk_fact_order_date  FOREIGN KEY (order_date_sk) REFERENCES dim_date(date_sk),
  CONSTRAINT fk_fact_ship_date   FOREIGN KEY (ship_date_sk)  REFERENCES dim_date(date_sk),
  CONSTRAINT fk_fact_customer    FOREIGN KEY (customer_sk)   REFERENCES dim_customer(customer_sk),
  CONSTRAINT fk_fact_product     FOREIGN KEY (product_sk)    REFERENCES dim_product(product_sk),
  CONSTRAINT fk_fact_geo         FOREIGN KEY (geo_sk)        REFERENCES dim_geography(geo_sk),
  CONSTRAINT fk_fact_shipping    FOREIGN KEY (shipping_sk)   REFERENCES dim_shipping(shipping_sk)
) ENGINE=InnoDB;


-- Distinct dates staging (optional temp table)
INSERT INTO dim_date (
  date_sk, date_actual, day_of_month, month_num, month_name, quarter_num, year_num, is_weekend
)
SELECT
  CAST(DATE_FORMAT(d, '%Y%m%d') AS UNSIGNED) AS date_sk,
  d AS date_actual,
  DAY(d)        AS day_of_month,
  MONTH(d)      AS month_num,
  MONTHNAME(d)  AS month_name,
  QUARTER(d)    AS quarter_num,
  YEAR(d)       AS year_num,
  CASE WHEN DAYOFWEEK(d) IN (1,7) THEN 1 ELSE 0 END AS is_weekend
FROM (
  SELECT DISTINCT order_date AS d FROM superstore
  UNION
  SELECT DISTINCT ship_date  AS d FROM superstore
) all_dates
LEFT JOIN dim_date dd ON dd.date_actual = all_dates.d
WHERE all_dates.d IS NOT NULL
  AND dd.date_actual IS NULL;


INSERT INTO dim_customer (customer_id, customer_name, segment)
SELECT DISTINCT
  s.customer_id,        -- from superstore
  s.customer_name,
  s.segment
FROM superstore s
LEFT JOIN dim_customer dc ON dc.customer_id = s.customer_id
WHERE dc.customer_id IS NULL
  AND s.customer_id IS NOT NULL;


INSERT INTO dim_product (product_id, product_name, category, sub_category)
SELECT DISTINCT
  s.product_id, 
  s.product_name, 
  s.category, 
  s.sub_category
FROM superstore s
WHERE s.product_id IS NOT NULL
ON DUPLICATE KEY UPDATE
  product_name = VALUES(product_name),
  category     = VALUES(category),
  sub_category = VALUES(sub_category);


INSERT INTO dim_geography (postal_code, city, _state, region, country)
SELECT DISTINCT
  CAST(s.postal_code AS CHAR) COLLATE utf8mb4_0900_ai_ci,
  s.city,
  s._state,
  s.region,
  s.country
FROM superstore s
LEFT JOIN dim_geography dg
  ON dg.postal_code = CAST(s.postal_code AS CHAR) COLLATE utf8mb4_0900_ai_ci
 AND dg.city        = s.city  COLLATE utf8mb4_0900_ai_ci
 AND dg._state      = s._state COLLATE utf8mb4_0900_ai_ci
 AND dg.region      = s.region COLLATE utf8mb4_0900_ai_ci
 AND dg.country     = s.country COLLATE utf8mb4_0900_ai_ci
WHERE dg.geo_sk IS NULL;


INSERT INTO dim_shipping (ship_mode)
SELECT DISTINCT s.ship_mode
FROM superstore s
LEFT JOIN dim_shipping ds ON ds.ship_mode = s.ship_mode
WHERE ds.ship_mode IS NULL
  AND s.ship_mode IS NOT NULL;


INSERT INTO fact_order_items (
  order_id, row_id,
  order_date_sk, ship_date_sk,
  customer_sk, product_sk, geo_sk, shipping_sk,
  quantity, sales, discount, profit
)
SELECT
  s.order_id,
  s.row_id,
  CAST(DATE_FORMAT(s.order_date, '%Y%m%d') AS UNSIGNED) AS order_date_sk,
  CASE WHEN s.ship_date IS NOT NULL
       THEN CAST(DATE_FORMAT(s.ship_date, '%Y%m%d') AS UNSIGNED)
       ELSE NULL END AS ship_date_sk,
  dc.customer_sk,
  dp.product_sk,
  dg.geo_sk,
  ds.shipping_sk,
  s.quantity,
  s.sales,
  s.discount,
  s.profit
FROM superstore s
JOIN dim_customer  dc 
  ON dc.customer_id = s.customer_id COLLATE utf8mb4_0900_ai_ci
JOIN dim_product   dp 
  ON dp.product_id  = s.product_id  COLLATE utf8mb4_0900_ai_ci
LEFT JOIN dim_geography dg
  ON dg.postal_code = CAST(s.postal_code AS CHAR) COLLATE utf8mb4_0900_ai_ci
 AND dg.city        = s.city    COLLATE utf8mb4_0900_ai_ci
 AND dg._state      = s._state  COLLATE utf8mb4_0900_ai_ci
 AND dg.region      = s.region  COLLATE utf8mb4_0900_ai_ci
 AND dg.country     = s.country COLLATE utf8mb4_0900_ai_ci
LEFT JOIN dim_shipping ds 
  ON ds.ship_mode   = s.ship_mode COLLATE utf8mb4_0900_ai_ci;



-- row counts
SELECT COUNT(*) superstore_rows FROM superstore;
SELECT COUNT(*) fact_rows FROM fact_order_items;

-- unmatched keys sanity (should be zero or explainable)
SELECT COUNT(*) FROM superstore s
LEFT JOIN dim_customer dc ON dc.customer_id = s.customer_id
WHERE dc.customer_sk IS NULL;

SELECT COUNT(*) FROM superstore s
LEFT JOIN dim_product dp ON dp.product_id = s.product_id
WHERE dp.product_sk IS NULL;


SELECT d.year_num, d.month_num, d.month_name,
       SUM(f.sales) AS total_sales
FROM fact_order_items f
JOIN dim_date d ON f.order_date_sk = d.date_sk
GROUP BY d.year_num, d.month_num, d.month_name
ORDER BY d.year_num, d.month_num;


SELECT p.category, p.sub_category,
       SUM(f.profit) AS profit_total
FROM fact_order_items f
JOIN dim_product p ON f.product_sk = p.product_sk
GROUP BY p.category, p.sub_category
ORDER BY profit_total DESC
LIMIT 10;
