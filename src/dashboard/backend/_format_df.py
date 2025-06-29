import pandas as pd

def format_df(df: pd.DataFrame) -> pd.DataFrame:
    # spalten namen formatieren
    df.columns = [col.lower().replace(" ", "_").replace(".", "") for col in df.columns]
    # datetime formatierung
    df["createdat"] = pd.to_datetime(df["createdat"], utc=True, format="ISO8601").dt.tz_convert("Europe/Berlin")
    # spalten formatieren
    cols_to_convert = df.columns.difference(['createdat'])
    df[cols_to_convert] = df[cols_to_convert].astype(float)
    # sortieren und indexieren
    df = df.sort_values(by="createdat").reset_index(drop=True)
    return df