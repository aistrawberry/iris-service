import logging
from functools import lru_cache
from logging.config import fileConfig
import mlflow
import mlflow.sklearn
import numpy as np
import argparse

import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseSettings
from starlette_exporter import PrometheusMiddleware, handle_metrics

LOGGER = logging.getLogger('iris.serving.logger')


class Settings(BaseSettings):
    app_name: str
    model_uri: str
    feature_rule: int
    mlflow_enable: bool
    mlflow_server: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.get("/prediction")
async def prediction(petal_length: float, petal_width: float, sepal_length: float, sepal_width: float,
                     settings: Settings = Depends(get_settings)):
    one_iris = np.array([[petal_length, petal_width, sepal_length, sepal_width]])
    featured_iris = one_iris[:, settings.feature_rule:]

    model = None

    try:
        model = mlflow.sklearn.load_model(settings.model_uri)
        LOGGER.info("Model Loaded")
    except Exception as ex:
        LOGGER.error("Load Model {ex}")

    try:
        value = model.predict(featured_iris)
        specie_value = int(value[0])
        specie_name = ""
        if specie_value == 0:
            specie_name = 'setosa'
        elif specie_value == 1:
            specie_name = 'versicolor'
        elif specie_value == 2:
            specie_name = 'virginica'
    except Exception as ex:
        LOGGER.error("Predict Model failed", ex)
        return {"status": "failed", "specie": specie_name}
    return {"status": "success", "specie": specie_name}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    MODEL_URI = "random-forest-model"
    parser.add_argument('--model_uri', type=str, default=MODEL_URI)
    parser.add_argument('--feature_rule', type=int, default=2)

    args = parser.parse_args()
    # app = create_app(args.model_uri, args.feature_rule)
    uvicorn.run(app, host="0.0.0.0", port=5000)
