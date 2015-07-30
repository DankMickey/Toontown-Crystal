#!/usr/bin/env python2
import json
import os
import requests
from pandac.PandaModules import *


username = os.environ['ttsUsername']
password = os.environ['ttsPassword']

accountServerEndpoint = ConfigVariableString(
    'account-server-endpoint',
    'https://toontowninfinite.com/api').getValue()
request = requests.post(
    accountServerEndpoint + 'login/',
    data={'n': username, 'p': password})

try:
    response = json.loads(request.text)
except ValueError:
    print "Couldn't verify account credentials."
else:
    if not response['success']:
        print response['reason']
    else:
        os.environ['TTS_PLAYCOOKIE'] = response['token']

        # Start the game:
        import toontown.toonbase.ClientStart
