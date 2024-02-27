"""
API to send requests to be batched for S3/other storage.
    Configuration: 
        PREFIX: Where to store, default is /tmp/
                                s3://bucket/prefix is recommended
        FLUSH_INTERVAL: How often to flush, maximum is 900 seconds, default is 120 seconds
        BUFFER_LIMIT: How many lines to buffer, default is 100 lines
"""

import os
import logging
import signal
from flask import Flask, jsonify, request
from batch_json_lines import BatchJSONLines

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
logger = logging.getLogger()

# We need to gracefully shutdown if control-c is pressed:
def signal_handler(sig, frame):
    """
    Gracefully shutdown
    """
    logging.info("Shutting down")
    buffer.shutdown()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if "PREFIX" in os.environ:
    prefix = os.environ["PREFIX"]
else:
    prefix = "/tmp/"        # pylint: disable=C0103 # This is our default value
    logging.warning("PREFIX env variable is not set, using local filesystem (/tmp)")

flush_interval = 120       # pylint: disable=C0103 # This is our default value
if "FLUSH_INTERVAL" in os.environ:
    # check if numeric and if it's under 900 seconds we will use it.
    # If > 900 seconds we will use 900 seconds and log a warning of config out of range
    if os.environ["FLUSH_INTERVAL"].isdigit():
        if int(os.environ["FLUSH_INTERVAL"]) < 900:
            flush_interval = int(os.environ["FLUSH_INTERVAL"])
        else:
            flush_interval = 900
            logging.warning("FLUSH_INTERVAL env variable is set to %s, which is out of range, using 900 seconds instead",
                             os.environ["FLUSH_INTERVAL"])

buffer_limit = 100         # pylint: disable=C0103 # This is our default value
if "BUFFER_LIMIT" in os.environ:
    # Check for number of lines to buffer, if not numeric we will use 100 lines and log a warning
    if os.environ["BUFFER_LIMIT"].isdigit():
        buffer_limit = int(os.environ["BUFFER_LIMIT"])

app = Flask(__name__)
buffer = BatchJSONLines(prefix=prefix, buffer_limit=buffer_limit, flush_interval=flush_interval)

@app.route("/send", methods=["POST"])
def send():
    """
    Send a request to be batched for S3, object must be JSON
    """
    logging.debug("INPUT get_json(): %s", request.get_json())
    buffer.add_request(request.get_json())
    return jsonify(request.get_json())

@app.route("/healthy", methods=["GET"])
def healthy():
    """
    Health check
    """
    return "OK"

if __name__ == "__main__":
    app.run(debug=False, port=8000)
