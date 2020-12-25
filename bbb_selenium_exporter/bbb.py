from collections import OrderedDict
from hashlib import sha1
from urllib.parse import urlencode
from uuid import uuid4
import xml.etree.ElementTree as ET

import requests


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class Meeting():
    def __init__(self, hostname, secret, name=None):
        self._hostname = hostname
        self._secret = secret
        self._meeting_id = name or str(uuid4())
        self._moderator_pw = str(uuid4())

    def __enter__(self):
        self._api_call('create', {'meetingID': self._meeting_id, 'moderatorPW': self._moderator_pw})
        return self

    def __exit__(self, *args):
        self._api_call('end', {'meetingID': self._meeting_id, 'password': self._moderator_pw})

    def _api_call(self, method, params):
        try:
            response = requests.get(self._build_url(method, params), timeout=0.5)
            root = ET.fromstring(response.text)
            if root.findall('returncode')[0].text == 'SUCCESS':
                return
            message_key = root.findall('messageKey')[0].text
            message = root.findall('message')[0].text
            raise Error(f'{message_key}: {message}')
        except requests.exceptions.RequestException as exc:
            raise Error('failed to talk to server') from exc
        except ET.ParseError as exc:
            raise Error('failed to parse server response') from exc
        except IndexError as exc:
            raise Error('received XML response with missing keys') from exc

    def _build_url(self, method, params):
        params = OrderedDict(params)
        params['checksum'] = self._checksum(method, params)
        return f'https://{self._hostname}/bigbluebutton/api/{method}?{urlencode(params)}'

    def _checksum(self, method, params):
        return sha1(f'{method}{urlencode(params)}{self._secret}'.encode()).hexdigest()

    def join_url(self, username):
        return self._build_url('join', {
            'meetingID': self._meeting_id,
            'password': self._moderator_pw,
            'fullName': username,
            'redirect': 'true',
        })
