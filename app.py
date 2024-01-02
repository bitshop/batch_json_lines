"""
API to send requests to be batched for S3/other storage.
"""
import os
import logging
from flask import Flask, jsonify, request
from batch_json_lines import BatchJSONLines

if "PREFIX" in os.environ:
    prefix = os.environ["PREFIX"]
else:
    prefix = "/tmp/"        # pylint: disable=C0103 # This is our default value
    logging.warning("PREFIX env variable is not set, using local filesystem (/tmp)")
    prefix = "s3://streamlit-sr-test"

buffer = BatchJSONLines(prefix=prefix)

app = Flask(__name__)


@app.route("/send", methods=["POST"])
def send():
    """
    Send a request to be batched for S3, object must be JSON
    """
    buffer.add_request(request.get_json())
    return jsonify(request.get_json())


if __name__ == "__main__":
    app.run(debug=False, port=8000)
