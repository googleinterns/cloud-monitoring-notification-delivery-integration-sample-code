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
from uuid import uuid4
from dotenv import load_dotenv

import pytest

from philips_hue import set_color, configure_light

load_dotenv()
URL = os.environ.get("philips-url")


def test_set_color():
    set_color(1, 0)
    
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 0
    
def test_configure_light_open():
    response = {"incident": {"condition": {"state": "open"}}}
    configure_light(response, 1)
    
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 0
    
def test_configure_light_closed():
    response = {"incident": {"condition": {"state": "closed"}}}
    configure_light(response, 1)
    
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 25500
    