from sqlalchemy.engine import Engine
from sqlalchemy import text
from backend import SenseBox
from backend._format_df import format_df
import pandas as pd

def update_db(engine: Engine, sensebox: SenseBox, table_name: str) -> dict:
    last_day = _last_day(engine, table_name)

    data = []
    try:
        data.append(sensebox.fetch_archive(last_day["createdat"].max().date()))
    except ValueError:
        print("No data from archive.")


    data.append(sensebox.fetch_buffer())

    data = pd.concat(data).drop_duplicates(subset=["createdat"])

    data = format_df(data)

    data = data[
        (data["createdat"] > last_day["createdat"].min()) & 
        (~data["createdat"].isin(last_day["createdat"]))
    ].reset_index(drop=True)
    data = format_df(data)
    data.to_sql(table_name, engine, if_exists="append", index=False)
    return data


def _last_day(engine: Engine, table_name: str) -> pd.DataFrame:
    # Step 1: Get latest date in the table (based on createdat column)
    with engine.connect() as conn:
        last_date_query = text(f"SELECT MAX(createdat)::date AS last_day FROM {table_name}")
        last_day = conn.execute(last_date_query).scalar()

    if last_day is None:
        return pd.DataFrame()  # Table is empty

    # Step 2: Get all rows from that date using pandas
    query = f"""
        SELECT * FROM {table_name}
        WHERE createdat::date = '{last_day}'
        ORDER BY createdat ASC
    """

    df = pd.read_sql_query(query, engine)
    return format_df(df)