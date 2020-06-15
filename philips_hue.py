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

import requests
import json


class PhilipsHueClient(object):
    """A client to interact with the Philips Hue API and configure Philips Hue lights."""
    
    
    def __init__(self, api_url):
        self.api_url = api_url
        

    def set_color(self, light_id, hue):
        """Sets the color of a Philips Hue light to a specified hue value.

        Args:
            light_id: The id of the light to set the color for.
            hue: Hue of the light.
        """
        r = requests.put(url = f'{self.api_url}/lights/{light_id}/state', data=json.dumps({"on": True, "hue": hue}))