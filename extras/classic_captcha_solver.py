import base64
import json
from time import sleep

import requests

CAPTCHA_COOKIE_HOST = 'https://wafid.com/book-appointment/'
CAPTCHA_SOLVER_HOST = 'https://2captcha.com'
CAPTCHA_SOLVER_API_SECRET = 'd217dfd21af07dda329436e8de9a5953'


class CaptchaSolver(object):

    @classmethod
    def solve_captcha(cls, captcha_url, session):
        _solved_code = None
        _form_data = {
            "method": "base64",
            "key": CAPTCHA_SOLVER_API_SECRET,
            "body": base64.b64encode(session.get(captcha_url).content).decode('utf-8'),
            "json": "1",
        }
        # print(_form_data["body"])
        response = requests.post(f'{CAPTCHA_SOLVER_HOST}/in.php', data=_form_data)
        _json_response = json.loads(response.text)
        while _json_response['status'] == 1:
            sleep(2.5)
            _request_id = _json_response['request']
            _solved_res = requests.get(f'{CAPTCHA_SOLVER_HOST}/res.php?key={CAPTCHA_SOLVER_API_SECRET}&id={_request_id}&action=get&json=1')
            _solved_res = json.loads(_solved_res.text)
            if _solved_res['status'] == 1 and 'request' in _solved_res:
                _solved_code = _solved_res['request']
                break
            else:
                pass
        return _solved_code
