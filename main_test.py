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

# Source code from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main_test.py

# NOTE:
# These tests are unit tests that mock Pub/Sub.

import base64
from uuid import uuid4

import pytest
import requests

import main
import philips_hue
import philips_hue_mock


@pytest.fixture
def config():
    main.app.config.from_object('config.DevConfig')
    return main.app.config


@pytest.fixture
def flask_client():
    main.app.testing = True
    return main.app.test_client()


@pytest.fixture
def philips_hue_client(config):
    philips_hue_client = philips_hue.PhilipsHueClient(
        config['BRIDGE_IP_ADDRESS'], config['USERNAME'])
    return philips_hue_client


def test_empty_payload(flask_client, capsys):
    r = flask_client.post('/', json='')
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid Pub/Sub message format' in out


def test_invalid_payload(flask_client, capsys):
    r = flask_client.post('/', json={'nomessage': 'invalid'})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid Pub/Sub message format' in out


def test_invalid_mimetype(flask_client, capsys):
    r = flask_client.post('/', json="{ message: true }")
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid Pub/Sub message format' in out


def test_nonstring_pubsub_message(flask_client, capsys):
    r = flask_client.post('/', json={'message': True})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid Pub/Sub message format' in out


def test_nonstring_notification_message(flask_client, capsys):
    r = flask_client.post('/', json={'message': {'data': True}})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'data should be in a string format' in out


def test_unicode_notification_message(flask_client, capsys):
    data = '{"incident": {"condition": {"state": "open"}}}'

    r = flask_client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'data should be base64-encoded' in out


def test_invalid_notification_message(flask_client, capsys):
    response = 'invalid message'
    data = base64.b64encode(response.encode()).decode()

    r = flask_client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'notification could not be decoded to a JSON' in out


def test_invalid_incident_message(flask_client, capsys):
    response = '{"invalid": "error"}'
    data = base64.b64encode(response.encode()).decode()

    r = flask_client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid incident format' in out


def test_open_alert_message(flask_client, philips_hue_client, capsys, requests_mock):
    response = '{"incident": {"condition": {"state": "open"}}}'
    data = base64.b64encode(response.encode()).decode()

    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    requests_mock.put(f'http://{bridge_ip_address}/api/{username}/lights/1/state',
                      text=philips_hue_mock.mock_hue_put_response)

    response = flask_client.post('/', json={'message': {'data': data}})
    assert response.status_code == 200  
    assert b"{'success': {'/lights/1/state/on': 'True'}}" in response.data
    assert b"{'success': {'/lights/1/state/hue': '0'}}" in response.data

    
def test_closed_alert_message(flask_client, philips_hue_client, capsys, requests_mock):
    response = '{"incident": {"condition": {"state": "closed"}}}'
    data = base64.b64encode(response.encode()).decode()
    
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    requests_mock.put(f'http://{bridge_ip_address}/api/{username}/lights/1/state', text=philips_hue_mock.mock_hue_put_response)

    response = flask_client.post('/', json={'message': {'data': data}})
    assert response.status_code == 200  
    assert b"{'success': {'/lights/1/state/on': 'True'}}" in response.data
    assert b"{'success': {'/lights/1/state/hue': '25500'}}" in response.data
