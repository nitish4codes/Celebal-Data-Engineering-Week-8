# E-Commerce Data Pipeline & Warehouse Analytics

## Overview
An end-to-end data engineering pipeline that automates the generation, cleaning, warehousing, and reporting of transactional e-commerce data. The system generates synthetic raw data containing deliberate quality anomalies, resolves them via a Python/Pandas ETL layer, loads the structured tables into an SQLite database, and exposes an operational reporting portal through a custom Command-Line Interface (CLI).

---

## Repository Architecture
Celebal-Data-Engineering-Week-8/
│
├── .gitignore                   # Excludes data files, binary caches, and databases
│
└── my-intern-mini-project/
    ├── scripts/
    │   ├── __pycache__/
    │   ├── clean_data.py        # Stage 2: Programmatic Pandas ETL pipeline
    │   ├── generate_data.py     # Stage 1: Ingestion & data simulation engine
    │   ├── load_to_sql.py       # Stage 3a: Initializes database & loads CSV data
    │   ├── report_tool.py       # Stage 4: Native SQLite interactive reporting app
    │   └── test_cases.py        # Stage 5: Rigorous edge-case validation suite
    │
    ├── sql/
    │   └── analysis.sql         # Stage 3b: Core analytical warehouse queries
    │
    ├── pipeline_demo.ipynb      # Step-by-step interactive visual notebook
    └── README.md                # Project documentation and execution guide



## Data Pipeline Lifecycle

### 1. Data Generation & Ingestion
The engine (scripts/generate_data.py) simulates standard transaction workflows by creating 4 source entity files: customers.csv, products.csv, orders.csv, and order_items.csv. To evaluate pipeline resilience, it intentionally embeds standard production data-quality challenges:

Null Keys: 5% of orders omit vital customer relationships.

Varying Formats: 5% of order dates are injected as malformed string types (DD-MM-YYYY).

Data Outliers: 3% of item records possess negative quantity values representing returns.

String Noise: 10% of product data features irregular spacing and mismatched text casing.

Validation Issues: 2% of customer emails are intentionally generated with missing domains.

### 2. Programmatic Transformation (ETL)
The automation pipeline (scripts/clean_data.py) leverages Pandas vectorized operations to process clean, high-integrity target extractions:

clean_orders(): Standardizes unstructured datetime blocks and captures missing keys into a safe UNKNOWN classification.

clean_products(): Trims whitespace padding and applies Title Case formatting to normalize text fields.

validate_emails(): Trims out and logs records that break standard string matching validations.

check_referential_integrity(): Programmatically identifies and isolates orphaned child records before database injection.

### 3. Relational Warehousing & Core Analytics
Cleaned datasets are loaded into a local database instance (ecommerce_analytics.db) using the loading automation script (scripts/load_to_sql.py). The production script sql/analysis.sql handles all 16 business analytics requirements structured across distinct difficulties:

Basic: Aggregated category revenues and running trailing month tallies.

Intermediate: Isolating specific product catalog IDs maintaining high return-to-purchase distributions.

Advanced Warehouse Analytics: Complex querying architectures utilizing window functions (DENSE_RANK(), NTILE(4)), sequential time-offset tracking (LAG()), group cohort retention models, and cumulative distribution summaries.

### 4. Interactive Reporting Interface
The executive reporting portal (scripts/report_tool.py) provides an operational interface built natively without external dependencies. It processes runtime command arguments (daily, weekly, monthly) alongside custom tracking bounds to output immediate performance summaries, executing comparative percentage metrics against equivalent historical periods.

## Execution Guide for Mentors
Run the pipeline sequentially using your terminal inside the my-intern-mini-project directory:

### 1. Generate the raw, anomalous source datasets
python scripts/generate_data.py

### 2. Execute the Pandas ETL script to resolve quality constraints
python scripts/clean_data.py

### 3. Load the clean files into the SQLite database instance
python scripts/load_to_sql.py

### 4. Open the operational executive reporting application
python scripts/report_tool.py

### 5. Execute the edge-case pipeline validation test suite
python scripts/test_cases.py
Key Assets for Evaluation
pipeline_demo.ipynb: Review this notebook directly on GitHub for a fast, visual step-by-step walkthrough of the pipeline outputs.

sql/analysis.sql: Contains clean SQL code for all 16 data warehouse requirements completely organized with standard formatting.

.gitignore: Configured with strict production rules (*.csv, *.db) to keep heavy data files untracked, ensuring the repository remains lightweight and clean.