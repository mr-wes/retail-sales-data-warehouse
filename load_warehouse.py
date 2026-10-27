import argparse
import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = PROJECT_DIR.parent / "shared_sample_sales.csv"
DEFAULT_DB = PROJECT_DIR / "sales_warehouse.db"

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_segment",
    "product_id", "product_name", "category", "region",
    "quantity", "unit_price_kes", "discount_pct", "revenue_kes"
]

DDL = """
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    customer_segment TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE dim_region (
    region_key INTEGER PRIMARY KEY,
    region_name TEXT NOT NULL UNIQUE
);

CREATE TABLE fact_sales (
    sales_key INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    region_key INTEGER NOT NULL REFERENCES dim_region(region_key),
    quantity REAL NOT NULL CHECK(quantity >= 0),
    unit_price_kes REAL NOT NULL CHECK(unit_price_kes >= 0),
    discount_pct REAL NOT NULL CHECK(discount_pct BETWEEN 0 AND 1),
    revenue_kes REAL NOT NULL CHECK(revenue_kes >= 0)
);
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build the Retail Sales SQLite data warehouse."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    return parser.parse_args()


def load_source(input_path):
    if not input_path.is_file():
        raise FileNotFoundError(
            f"Source CSV not found: {input_path.resolve()}"
        )

    df = pd.read_csv(input_path)
    source_rows = len(df)

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    df = df[REQUIRED_COLUMNS].copy()

    text_columns = [
        "order_id", "customer_id", "customer_segment",
        "product_id", "product_name", "category", "region"
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    numeric_columns = [
        "quantity", "unit_price_kes", "discount_pct", "revenue_kes"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove exact duplicate records before further validation.
    exact_duplicate_mask = df.duplicated(keep="first")
    exact_duplicates_removed = int(exact_duplicate_mask.sum())
    df = df.loc[~exact_duplicate_mask].copy()

    # Recover missing revenue only when every input is available.
    revenue_inputs_valid = (
        df["quantity"].notna()
        & df["unit_price_kes"].notna()
        & df["discount_pct"].notna()
    )

    missing_revenue = df["revenue_kes"].isna()
    recoverable_revenue = missing_revenue & revenue_inputs_valid

    df.loc[recoverable_revenue, "revenue_kes"] = (
        df.loc[recoverable_revenue, "quantity"]
        * df.loc[recoverable_revenue, "unit_price_kes"]
        * (1 - df.loc[recoverable_revenue, "discount_pct"])
    ).round(2)

    required_keys = [
        "order_id", "order_date", "customer_id", "product_id"
    ]

    invalid_key_mask = df[required_keys].isna().any(axis=1)

    # Keep no ambiguous order IDs. All rows for a repeated ID are excluded.
    duplicate_id_mask = df["order_id"].notna() & df["order_id"].duplicated(
        keep=False
    )
    duplicate_id_rows = int(duplicate_id_mask.sum())

    invalid_numeric_mask = df[numeric_columns].isna().any(axis=1)
    invalid_numeric_mask |= df["quantity"] < 0
    invalid_numeric_mask |= df["unit_price_kes"] < 0
    invalid_numeric_mask |= ~df["discount_pct"].between(0, 1)

    invalid_mask = (
        invalid_key_mask | duplicate_id_mask | invalid_numeric_mask
    )
    invalid_rows_removed = int(invalid_mask.sum())
    df = df.loc[~invalid_mask].copy()

    # Preserve valid transactions with missing descriptive values.
    for column in [
        "customer_segment", "product_name", "category", "region"
    ]:
        df[column] = df[column].fillna("Unknown")

    expected_revenue = (
        df["quantity"]
        * df["unit_price_kes"]
        * (1 - df["discount_pct"])
    ).round(2)

    mismatch_mask = (df["revenue_kes"] - expected_revenue).abs() > 0.01
    revenue_mismatches = int(mismatch_mask.sum())

    if revenue_mismatches:
        raise ValueError(
            f"{revenue_mismatches} revenue mismatches detected. "
            "The warehouse was not rebuilt."
        )

    df["revenue_kes"] = expected_revenue

    report = {
        "source_rows": source_rows,
        "exact_duplicates_removed": exact_duplicates_removed,
        "duplicate_id_rows_excluded": duplicate_id_rows,
        "invalid_rows_removed": invalid_rows_removed,
        "revenue_mismatches": revenue_mismatches,
        "rows_loaded": len(df),
        "rows_not_loaded": source_rows - len(df),
    }

    return df, report


def build_dimensions(df):
    dates = pd.DataFrame({
        "full_date": sorted(
            df["order_date"].dt.strftime("%Y-%m-%d").unique()
        )
    })

    date_values = pd.to_datetime(dates["full_date"])
    dates["date_key"] = date_values.dt.strftime("%Y%m%d").astype(int)
    dates["year"] = date_values.dt.year
    dates["month"] = date_values.dt.month
    dates["month_name"] = date_values.dt.month_name()
    dates["quarter"] = date_values.dt.quarter

    dates = dates[
        ["date_key", "full_date", "year", "month", "month_name", "quarter"]
    ]

    customers = (
        df[["customer_id", "customer_segment"]]
        .drop_duplicates("customer_id")
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    customers.insert(0, "customer_key", range(1, len(customers) + 1))

    products = (
        df[["product_id", "product_name", "category"]]
        .drop_duplicates("product_id")
        .sort_values("product_id")
        .reset_index(drop=True)
    )
    products.insert(0, "product_key", range(1, len(products) + 1))

    regions = pd.DataFrame({
        "region_name": sorted(df["region"].unique())
    })
    regions.insert(0, "region_key", range(1, len(regions) + 1))

    maps = {
        "date": dict(zip(dates["full_date"], dates["date_key"])),
        "customer": dict(zip(customers.customer_id, customers.customer_key)),
        "product": dict(zip(products.product_id, products.product_key)),
        "region": dict(zip(regions.region_name, regions.region_key)),
    }

    facts = pd.DataFrame({
        "order_id": df["order_id"],
        "date_key": (
            df["order_date"].dt.strftime("%Y-%m-%d").map(maps["date"])
        ),
        "customer_key": df["customer_id"].map(maps["customer"]),
        "product_key": df["product_id"].map(maps["product"]),
        "region_key": df["region"].map(maps["region"]),
        "quantity": df["quantity"],
        "unit_price_kes": df["unit_price_kes"],
        "discount_pct": df["discount_pct"],
        "revenue_kes": df["revenue_kes"],
    })

    return dates, customers, products, regions, facts


def rebuild_warehouse(db_path, dimensions):
    dates, customers, products, regions, facts = dimensions
    db_path.parent.mkdir(parents=True, exist_ok=True)

    temp_db = db_path.with_name(
        db_path.stem + ".tmp" + db_path.suffix
    )

    if temp_db.exists():
        temp_db.unlink()

    conn = None

    try:
        conn = sqlite3.connect(temp_db)
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript(DDL)

        dates.to_sql(
            "dim_date", conn, index=False, if_exists="append"
        )
        customers.to_sql(
            "dim_customer", conn, index=False, if_exists="append"
        )
        products.to_sql(
            "dim_product", conn, index=False, if_exists="append"
        )
        regions.to_sql(
            "dim_region", conn, index=False, if_exists="append"
        )
        facts.to_sql(
            "fact_sales", conn, index=False, if_exists="append"
        )

        violations = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise RuntimeError(
                f"Foreign-key violations: {violations}"
            )

        actual_count = conn.execute(
            "SELECT COUNT(*) FROM fact_sales"
        ).fetchone()[0]

        if actual_count != len(facts):
            raise RuntimeError(
                f"Expected {len(facts)} fact rows; found {actual_count}"
            )

        conn.commit()

    except Exception:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if conn is not None:
            conn.close()

    # The SQLite connection is now closed before the rename.
    try:
        os.replace(temp_db, db_path)
    finally:
        if temp_db.exists():
            try:
                temp_db.unlink()
            except PermissionError:
                print(
                    f"Warning: Could not remove temporary database: {temp_db}"
                )

    return actual_count

def main():
    args = parse_args()

    try:
        df, report = load_source(args.input.resolve())

        if df.empty:
            raise ValueError("No valid records remain after validation.")

        dimensions = build_dimensions(df)
        fact_count = rebuild_warehouse(args.db.resolve(), dimensions)

        print("\nETL DATA QUALITY REPORT")
        print("-" * 40)
        print(f"Source rows:                  {report['source_rows']}")
        print(
            "Exact duplicates removed:     "
            f"{report['exact_duplicates_removed']}"
        )
        print(
            "Rows with duplicate IDs:      "
            f"{report['duplicate_id_rows_excluded']}"
        )
        print(
            "Invalid rows removed:         "
            f"{report['invalid_rows_removed']}"
        )
        print(
            "Revenue mismatches:           "
            f"{report['revenue_mismatches']}"
        )
        print(f"Rows loaded:                   {report['rows_loaded']}")
        print(f"Rows not loaded:               {report['rows_not_loaded']}")
        print(f"Fact rows verified:            {fact_count}")
        print(f"Database:                      {args.db.resolve()}")
        print("\nETL completed successfully.")

    except (FileNotFoundError, ValueError, RuntimeError, sqlite3.Error) as exc:
        print(f"\nETL FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

