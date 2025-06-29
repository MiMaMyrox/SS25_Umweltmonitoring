import pandas as pd


def hourly_df(input: pd.DataFrame) -> pd.DataFrame:
    df = input.copy()
    
    # Monatszeitstempel erzeugen
    df["stunde"] = df["createdat"].dt.to_period("h").dt.to_timestamp()

    # Nur numerische Spalten mitteln
    df = df.groupby("stunde").mean(numeric_only=True).reset_index()

    # Optional: Umbenennen für Klarheit
    df.rename(columns={"stunde": "zeit"}, inplace=True)

    return df

def daily_df(input: pd.DataFrame) -> pd.DataFrame:
    df = input.copy()
    
    # Monatszeitstempel erzeugen
    df["tag"] = df["createdat"].dt.to_period("D").dt.to_timestamp()

    # Nur numerische Spalten mitteln
    df = df.groupby("tag").mean(numeric_only=True).reset_index()

    # Optional: Umbenennen für Klarheit
    df.rename(columns={"tag": "zeit"}, inplace=True)

    return df

def monthly_df(input: pd.DataFrame) -> pd.DataFrame:
    df = input.copy()
    
    # Monatszeitstempel erzeugen
    df["monat"] = df["createdat"].dt.to_period("M").dt.to_timestamp()

    # Nur numerische Spalten mitteln
    df = df.groupby("monat").mean(numeric_only=True).reset_index()

    # Optional: Umbenennen für Klarheit
    df.rename(columns={"monat": "zeit"}, inplace=True)

    return df

def yearly_df(input: pd.DataFrame) -> pd.DataFrame:
    df = input.copy()
    
    # Monatszeitstempel erzeugen
    df["jahr"] = df["createdat"].dt.to_period("Y").dt.to_timestamp()

    # Nur numerische Spalten mitteln
    df = df.groupby("jahr").mean(numeric_only=True).reset_index()

    # Optional: Umbenennen für Klarheit
    df.rename(columns={"jahr": "zeit"}, inplace=True)

    return df