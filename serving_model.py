from flask import Flask, request
from flask.logging import default_handler
import logging
from logging.config import fileConfig
import mlflow
import mlflow.sklearn
import numpy as np
import argparse

fileConfig('log.ini')
LOGGER = logging.getLogger('iris.serving.logger')


def create_app(model_uri, feature_rule):
    app = Flask('iris-service')
    app.logger.removeHandler(default_handler)

    load_model(app, model_uri, feature_rule)

    @app.route("/")
    def hello():
        LOGGER.info("Hello from Architect's Bot!")
        return "Hello from Architect's Bot!"

    @app.route("/predicate")
    def predicate():
        random_forest_regressor = app.config['model']
        feature_iris, query_params = filter_parameter()

        specie_name = prediction(feature_iris, random_forest_regressor)
        LOGGER.info('Predict Success', extra={'data': dict(query_params),
                                              'feature': app.config['feature_rule'],
                                              'label': specie_name})
        return specie_name

    def filter_parameter():
        query_params = request.values
        one_iris = np.array([[float(query_params.get('petal_length')), float(query_params.get('petal_width')),
                              float(query_params.get('sepal_length')), float(query_params.get('sepal_width'))]])
        feature_iris = one_iris[:, app.config['feature_rule']:]
        return feature_iris, query_params

    def prediction(feature_iris, random_forest_regressor):
        specie_name = 'unknown'
        try:
            value = random_forest_regressor.predict(feature_iris)
            specie_value = int(value[0])
            if specie_value == 0:
                specie_name = 'setosa'
            elif specie_value == 1:
                specie_name = 'versicolor'
            elif specie_value == 2:
                specie_name = 'virginica'
        except Exception as ex:
            LOGGER.error("Predict Model failed", ex)
        return specie_name

    return app


def load_model(app, model_uri, feature_rule):
    app.config['model-uri'] = model_uri
    app.config['feature_rule'] = feature_rule
    try:
        LOGGER.info("loading Model...")
        app.config['model'] = mlflow.sklearn.load_model(model_uri)
        LOGGER.info("Model Loaded")
    except Exception as ex:
        LOGGER.error("Load Model failed", ex)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_uri', type=str, default="random-forest-model")
    parser.add_argument('--feature_rule', type=int, default=2)

    args = parser.parse_args()
    app = create_app(args.model_uri, args.feature_rule)
    app.run(host="0.0.0.0", port=5000, debug=True)
