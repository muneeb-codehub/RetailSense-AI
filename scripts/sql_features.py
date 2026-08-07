from sqlalchemy import create_engine, text
import pandas as pd
import os

engine = create_engine("postgresql://postgres:admin123@localhost:5432/retailsense")
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'features'), exist_ok=True)
FEAT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'features')

queries = {

    "rolling_avg_sales": """
        SELECT 
            date, store_nbr, family, sales,
            AVG(sales) OVER (
                PARTITION BY store_nbr, family 
                ORDER BY date 
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS rolling_7day_avg,
            SUM(sales) OVER (
                PARTITION BY store_nbr, family 
                ORDER BY date 
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS rolling_30day_sum
        FROM train
        ORDER BY store_nbr, family, date
        LIMIT 100000
    """,

    "mom_growth": """
        WITH monthly AS (
            SELECT 
                store_nbr,
                DATE_TRUNC('month', date) AS month,
                SUM(sales)::numeric AS total_sales
            FROM train
            GROUP BY store_nbr, DATE_TRUNC('month', date)
        )
        SELECT 
            store_nbr, month, total_sales,
            LAG(total_sales) OVER (
                PARTITION BY store_nbr ORDER BY month
            ) AS prev_month_sales,
            ROUND(
                (total_sales - LAG(total_sales) OVER (
                    PARTITION BY store_nbr ORDER BY month)
                ) / NULLIF(LAG(total_sales) OVER (
                    PARTITION BY store_nbr ORDER BY month), 0) * 100, 2
            ) AS mom_growth_pct
        FROM monthly
        ORDER BY store_nbr, month
    """,

    "top_stores": """
        SELECT 
            t.store_nbr,
            s.city, s.state, s.type, s.cluster,
            ROUND(SUM(t.sales)::numeric, 2) AS total_sales,
            RANK() OVER (ORDER BY SUM(t.sales) DESC) AS sales_rank
        FROM train t
        JOIN stores s ON t.store_nbr = s.store_nbr
        GROUP BY t.store_nbr, s.city, s.state, s.type, s.cluster
        ORDER BY sales_rank
    """,

    "holiday_impact": """
        SELECT 
            CASE WHEN h.date IS NOT NULL 
                 THEN 'Holiday' 
                 ELSE 'Non-Holiday' 
            END AS day_type,
            ROUND(AVG(t.sales)::numeric, 2) AS avg_sales,
            COUNT(*) AS record_count
        FROM train t
        LEFT JOIN holidays h ON t.date = h.date
        GROUP BY day_type
    """,

    "family_rank_per_store": """
        SELECT 
            store_nbr, family,
            ROUND(SUM(sales)::numeric, 2) AS total_sales,
            RANK() OVER (
                PARTITION BY store_nbr 
                ORDER BY SUM(sales) DESC
            ) AS family_rank
        FROM train
        GROUP BY store_nbr, family
        ORDER BY store_nbr, family_rank
    """
}

print("🚀 Running SQL feature queries...\n")

for name, query in queries.items():
    print(f"⚙️  Running: {name}...")
    df = pd.read_sql(text(query), engine)
    out_path = os.path.join(FEAT_DIR, f"{name}.csv")
    df.to_csv(out_path, index=False)
    print(f"✅ {name}: {len(df):,} rows → saved\n")

print("🎉 All SQL features generated!")