from fastapi import FastAPI
import pickle
import pandas as pd
from prophet.serialize import model_to_json, model_from_json
from prophet import Prophet

app = FastAPI()

@app.get("/predict")
def predict():
    with open('./src/model/prophet_model.pkl', 'r') as fin:
        model = model_from_json(fin.read())  # Load model

    # Zukunftsdaten erzeugen (z.B. 30 Tage)
    future = model.make_future_dataframe(periods=168, freq='h')

    # # Vorhersage
    forecast = model.predict(future)

    # df = pd.DataFrame(data)
    # forecast = model.predict(df)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_dict(orient="records")

@app.post("/train")
def train(data: dict):

    df_prophet = pd.DataFrame(data)[['createdat', 'temperatur']]
    df_prophet['createdat'] = pd.to_datetime(df_prophet['createdat'], format="ISO8601", utc=True).dt.tz_localize(None)
    df_prophet["hour"] = df_prophet["createdat"].dt.to_period("h").dt.to_timestamp()
    df_prophet = df_prophet.groupby("hour").mean(numeric_only=True).reset_index().rename(columns={"hour":"ds", "temperatur":"y"})

    model = Prophet()
    model.fit(df_prophet)
    # Modell speichern nach Training
    with open('./src/model/prophet_model.pkl', 'w') as fout:
        fout.write(model_to_json(model))
    return {"message": "Model trained and saved."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)