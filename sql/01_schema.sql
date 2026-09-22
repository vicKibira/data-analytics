-- ============================================================================
-- 01_schema.sql
-- Plato's Pizza Analytics — Database Schema
-- ============================================================================
-- WHY A SCHEMA (NOT JUST TABLES IN `public`)?
-- A schema is a namespace inside a database. As the analytics team adds more
-- data sources later (marketing, inventory, ...) a dedicated `pizza` schema
-- keeps this project's tables clearly grouped and avoids name collisions.
--
-- WHY FOUR TABLES INSTEAD OF ONE FLAT TABLE?
-- The source file (data/raw/pizza_sales.csv) is a single flat export. We
-- normalize it into four related tables that mirror how this data is
-- actually structured (see data/README.md "Normalization decision" for the
-- full justification). This is what makes real JOIN and CTE practice
-- possible instead of just querying one wide table.
--
-- This script is idempotent: it can be re-run safely (DROP ... IF EXISTS).
-- It is executed automatically by src/load_data.py, but you can also run it
-- by hand with: psql -f sql/01_schema.sql
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS pizza;

-- Run DDL in the pizza schema without needing to prefix every statement.
SET search_path TO pizza;

DROP TABLE IF EXISTS order_details CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS pizzas CASCADE;
DROP TABLE IF EXISTS pizza_types CASCADE;

-- ----------------------------------------------------------------------------
-- pizza_types: one row per pizza FLAVOR (32 rows).
-- category and ingredients never change across sizes of the same flavor.
-- ----------------------------------------------------------------------------
CREATE TABLE pizza_types (
    pizza_type_id  VARCHAR(30)   PRIMARY KEY,   -- e.g. 'hawaiian'
    name           VARCHAR(100)  NOT NULL,      -- e.g. 'The Hawaiian Pizza'
    category       VARCHAR(20)   NOT NULL,      -- Classic / Veggie / Supreme / Chicken
    ingredients    TEXT          NOT NULL        -- comma-separated ingredient list
);

-- ----------------------------------------------------------------------------
-- pizzas: one row per (flavor, size) combination (91 rows).
-- This is where price lives, because price varies by size, not by flavor.
-- ----------------------------------------------------------------------------
CREATE TABLE pizzas (
    pizza_name_id  VARCHAR(30)   PRIMARY KEY,          -- e.g. 'hawaiian_m'
    pizza_type_id  VARCHAR(30)   NOT NULL REFERENCES pizza_types(pizza_type_id),
    size           VARCHAR(4)    NOT NULL,             -- S, M, L, XL, XXL
    price          NUMERIC(6,2)  NOT NULL CHECK (price > 0)
);

-- ----------------------------------------------------------------------------
-- orders: one row per customer order (21,350 rows).
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    order_id    INTEGER  PRIMARY KEY,
    order_date  DATE     NOT NULL,
    order_time  TIME     NOT NULL
);

-- ----------------------------------------------------------------------------
-- order_details: one row per pizza line-item within an order (48,620 rows).
-- This is the fact table — the grain analysts will aggregate most often.
-- ----------------------------------------------------------------------------
CREATE TABLE order_details (
    order_details_id  INTEGER       PRIMARY KEY,       -- from raw pizza_id
    order_id          INTEGER       NOT NULL REFERENCES orders(order_id),
    pizza_name_id     VARCHAR(30)   NOT NULL REFERENCES pizzas(pizza_name_id),
    quantity          INTEGER       NOT NULL CHECK (quantity > 0),
    total_price        NUMERIC(8,2) NOT NULL CHECK (total_price > 0)
);

-- Indexes on foreign key columns: every JOIN in Phase 2 (Level 8+) filters
-- or joins on these columns, so we index them now rather than waiting for a
-- slow-query lesson later.
CREATE INDEX idx_order_details_order_id      ON order_details(order_id);
CREATE INDEX idx_order_details_pizza_name_id ON order_details(pizza_name_id);
CREATE INDEX idx_pizzas_pizza_type_id        ON pizzas(pizza_type_id);
CREATE INDEX idx_orders_order_date           ON orders(order_date);

COMMENT ON TABLE  pizza_types           IS 'Pizza flavor dimension: name, category, ingredients.';
COMMENT ON TABLE  pizzas                IS 'Pizza flavor x size dimension: one row per sellable SKU, with price.';
COMMENT ON TABLE  orders                IS 'One row per customer order (order_date, order_time).';
COMMENT ON TABLE  order_details         IS 'Fact table: one row per pizza line-item sold. Grain = order_details_id.';
COMMENT ON COLUMN order_details.total_price IS 'Stored and validated equal to quantity * pizzas.price at load time.';
