from sqlalchemy.engine import Engine
import pandas as pd

from backend._format_df import format_df

def get_db(engine: Engine, table_name: str) -> pd.DataFrame:
    return format_df(pd.read_sql_table(table_name, engine))
