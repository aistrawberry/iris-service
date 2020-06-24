from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.sklearn
import argparse
import logging.config

LOGGER = logging.getLogger('iris.train.logger')


def load_dataset():
    iris = datasets.load_iris()
    return iris


def build_feature(dataset, rule):
    features = dataset.data[:, rule:]
    return features


def prepare_data(row_data, features, test_size):
    labels = row_data.target
    return train_test_split(features, labels, test_size=test_size, random_state=7)


def train_model(test_size, feature_rule, num_estimators):
    # prepare data
    row_data = load_dataset()
    x_train, x_test, y_train, y_test = prepare_data(row_data, build_feature(row_data, feature_rule), test_size)

    with mlflow.start_run(run_name="Iris RF Experiment") as run:
        # train model
        mlflow.log_param("num_estimators", num_estimators)
        rf = RandomForestRegressor(n_estimators=num_estimators)
        rf.fit(x_train, y_train)
        predictions = rf.predict(x_test)

        # save model artifact
        mlflow.sklearn.log_model(rf, "random-forest-model")
        model_uri = mlflow.get_artifact_uri()

        # log model performance
        mse = mean_squared_error(y_test, predictions)
        mlflow.log_metric("mse", mse)
        # LOGGER.info("score", extra={'mse': mse})

        mlflow.end_run()
        # LOGGER.info(run.info)
        return model_uri


if __name__ == "__main__":
    # get parameters from run shell, expose endpoint
    parser = argparse.ArgumentParser()

    # set parameters
    parser.add_argument('--num_estimators', type=int, default=100)

    # set tags
    parser.add_argument('--test_size', type=float, default=0.2)
    parser.add_argument('--feature_rule', type=int, default=2)
    parser.add_argument('--source_type', type=str, default='CLOUD_IDE')

    parser.add_argument('--mlflow_experiment', type=str, default='iris-model')
    args = parser.parse_args()
    mlflow.set_experiment(args.mlflow_experiment)

    # set mlflow server here
    MLFLOW_SERVER_HOST = "http://mlfow-service-webapp.customer-dev.svc:5000"
    # parser.add_argument('--mlflow_server', type=str, default=MLFLOW_SERVER_HOST)
    # mlflow.set_tracking_uri(args.mlflow_server)

    # call train method
    train_model(args.test_size, args.feature_rule, args.num_estimators)
