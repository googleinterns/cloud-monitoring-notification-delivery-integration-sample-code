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

"""Module to handle input from Google Monitoring.

This module defines functions and errors to handle input from Google Monitoring,
such as Pub/Sub notifications.
"""

import json
import base64
import binascii


class NotificationParseError(Exception):
    """Exception raised for errors in a Pub/Sub notification format.

    Attributes:
        message: explanation of the error
    """

    def __init__(self, message):
        self.message = message
        
        
class IncidentParseError(NotificationParseError):
    """Exception raised for errors in an incident notification format.

    Attributes:
        message: explanation of the error
    """
    pass
        

def parse_notification_from_pubsub_envelope(pubsub_envelope):
    """Parses notification messages from Pub/Sub.

    Args:
        pubsub_envelope: The JSON message to parse from Pub/Sub.
        
    Returns:
        The resulting parsed notification as a JSON.
        
    Raises:
        NotificationParseError: If notification cannot be parsed.
    """
    try:
        notification_base64_string = pubsub_envelope['message']['data']
    except KeyError as e:
        raise NotificationParseError('invalid Pub/Sub message format') from e
    except TypeError as e:
        raise NotificationParseError('invalid Pub/Sub message format') from e

    try:
        notification_bytes = base64.b64decode(notification_base64_string)
    except binascii.Error as e:
        raise NotificationParseError('notification should be base64-encoded') from e
    except TypeError as e:
        raise NotificationParseError('notification should be in a string format') from e

    notification_string = notification_bytes.decode('utf-8')
    notification_string = notification_string.strip()
    try:
        notification_dict = json.loads(notification_string)
    except json.JSONDecodeError as e:
        raise NotificationParseError('notification could not be decoded to a JSON') from e
    
    return notification_dict


def parse_incident_from_notification(notification):
    """Parses incident message from a notification JSON.

    Args:
        notification: The incident notification.
        
    Returns:
        The resulting parsed incident dictionary.
        
    Raises:
        IncidentParseError: If notification cannot be parsed.
    """
    try:
        incident = notification['incident']
    except KeyError as e:
        raise IncidentParseError('invalid incident format') from e
        
    return incident