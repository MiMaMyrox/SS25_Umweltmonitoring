import os
import pandas as pd
import numpy as np

from fastapi import FastAPI

from sqlalchemy import create_engine

from dotenv import load_dotenv

from backend import SenseBox, create_db, update_db, get_db


load_dotenv()
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
box_id = os.getenv("BOX_ID")
table_name = os.getenv("TABLE_NAME")

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

sensebox = SenseBox(box_id)

app = FastAPI()

@app.get("/create-db")
def create():
    info = create_db(engine, sensebox, table_name)
    return {
        "status": "created",
        "info":info
    }

@app.get("/update-db")
def update():
    data = update_db(engine, sensebox, table_name)
    if data.empty:
        return {
        "status": "no updates",
        "data":None
    }
    
    return {
        "status": "updated",
        "data":data
    }

@app.get("/get-db")
def get():
    data = get_db(engine, table_name)

    # Replace NaN and Inf/-Inf with None, which is JSON-serializable
    data = data.replace([np.nan, np.inf, -np.inf], None)

    return {
        "status": "OK",
        "data": data.to_dict(orient="records")
    }

# @app.post("/load-api")
# def load_api():
#     fetch_api_data()
#     return {"status": "api data loaded"}

# @app.post("/load-archive")
# def load_archive():
#     fetch_archive()
#     return {"status": "archive loaded"}

# @app.post("/start-live")
# def start_live():
#     start_live_stream()
#     return {"status": "live stream started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)