import pandas as pd
from sqlalchemy.engine import Engine
from backend import SenseBox
from backend._format_df import format_df


def create_db(engine: Engine, sensebox: SenseBox, table_name: str) -> pd.DataFrame:

    data = []
    data.append(sensebox.fetch_archive())
    data.append(sensebox.fetch_buffer())
    data.append(sensebox.fetch_last_measurement())

    data = pd.concat(data).drop_duplicates(subset=["createdat"])
    data = format_df(data)
    data.to_sql(table_name, engine, if_exists='replace', index=False)
    return {
        "from":data["createdat"].min().strftime("%Y-%m-%d %H:%M:%S"),
        "to":data["createdat"].max().strftime("%Y-%m-%d %H:%M:%S"),
        "total_measurements":len(data)
    }