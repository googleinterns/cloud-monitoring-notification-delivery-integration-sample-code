# Copyright 2020 Google, LLC.
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

# NOTE:
# These tests are unit tests for functions in philips_hue.py.

import requests
import os
import base64

import pytest

import main
import philips_hue

main.app.config.from_object('config.DevConfig')
url = main.app.config['PHILIPS_HUE_URL']


def test_set_color():
    philips_hue_client = philips_hue.PhilipsHueClient(url)
    philips_hue_client.set_color(1, 0)
    
    r = requests.get(f'{url}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 0
    