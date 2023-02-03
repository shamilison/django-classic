import base64
import json
from time import sleep

import requests


class CaptchaSolver(object):

    @classmethod
    def solve_captcha(cls, captcha_url, session, captcha_host, captcha_secret):
        _solved_code = None
        _form_data = {
            "method": "base64",
            "key": captcha_secret,
            "body": base64.b64encode(session.get(captcha_url).content).decode('utf-8'),
            "json": "1",
        }
        # print(_form_data["body"])
        response = requests.post(f'{captcha_host}/in.php', data=_form_data)
        _json_response = json.loads(response.text)
        while _json_response['status'] == 1:
            sleep(2.5)
            _request_id = _json_response['request']
            _solved_res = requests.get(f'{captcha_host}/res.php?key={captcha_secret}&id={_request_id}&action=get&json=1')
            _solved_res = json.loads(_solved_res.text)
            if _solved_res['status'] == 1 and 'request' in _solved_res:
                _solved_code = _solved_res['request']
                break
            else:
                pass
        return _solved_code
