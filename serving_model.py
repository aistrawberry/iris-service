from flask import Flask
import logging
from logging.config import fileConfig

app = Flask(__name__)

fileConfig('log.ini')
LOGGER = logging.getLogger('iris.serving.logger')


@app.route("/")
def hello():
    LOGGER.info("Hello from Architect's Bot!")
    return "Hello from Architect's Bot!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
