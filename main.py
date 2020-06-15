# Copyright 2019 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The code in this module is based on https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main.py. See https://cloud.google.com/run/docs/tutorials/pubsub for the accompanying Cloud Run/PubSub solutions guide.

# [START run_pubsub_server_setup]
import base64
import os
import json
import philips_hue

from flask import Flask, request


app = Flask(__name__)
app.config.from_object('config.DevConfig')
philips_hue_client = philips_hue.PhilipsHueClient(app.config['PHILIPS_HUE_URL'])
# [END run_pubsub_server_setup]


def trigger_hue_from_incident(incident, light_id):
    """Changes the color of a Philips Hue light based on an incident message from pub/sub.
    
    Sets the color of the light to red if the incident is open and green if the incident is closed.

    Args:
        incident: A JSON message about an incident from pub/sub.
        light_id: The id of the light to set the color for.
    """
    if incident["incident"]["condition"]["state"] == "open":
        philips_hue_client.set_color(light_id, 0)
    elif incident["incident"]["condition"]["state"] == "closed":
        philips_hue_client.set_color(light_id, 25500)

        
# [START run_pubsub_handler]
@app.route('/', methods=['POST'])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = 'no Pub/Sub message received'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        msg = 'invalid Pub/Sub message format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    pubsub_message = envelope['message']

    response = 'empty response'
    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
        response = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()
        
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        msg = 'invalid incident format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    trigger_hue_from_incident(response, 1)  


    return ('', 204)
# [END run_pubsub_handler]


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)