__author__ = 'shamilsakib'

from collections import OrderedDict

from rest_framework import renderers, status


class ClassicJSONRenderer(renderers.JSONRenderer):
    def flatten_dictionary(self, data):
        if isinstance(data, list):
            return data[0]
        if isinstance(data, (dict, OrderedDict)):
            _k = list(data.keys())[0]
            return _k + ": " + self.flatten_dictionary(data[_k])
        return data

    def render(self, data, accepted_media_type=None, renderer_context=None):
        ignore_keys = ['success', 'message', 'status_code']
        status_code = renderer_context['response'].status_code
        if status_code == 204:
            renderer_context['response'].status_code = 200
        if not data:
            data = {}
        if isinstance(data, list):
            data_list = data
            data = dict()
            data["results"] = data_list

        data['success'] = status.is_success(status_code)
        data['message'] = 'Request processed successfully.'

        if not status.is_success(status_code):
            if status.is_client_error(status_code):
                data['message'] = data.get('detail', '')
            elif status.is_server_error(status_code):
                data['message'] = data.get('detail', "A server error has occurred. "
                                                     "Please contact administrator for assistance.")

            if data['message'] == '':
                for key in data.keys():
                    if key not in ignore_keys:
                        if isinstance(data[key], list):
                            if isinstance(data[key][0], dict):
                                data['message'] = data[key][0][list(data[key][0].keys())[0]]
                                if isinstance(data['message'], list):
                                    data['message'] = key + " : " + data['message'][0]
                            else:
                                data['message'] = key + " : " + data[key][0]
                        else:
                            data['message'] = data[key]
                        break

            result = dict()
            for key in data.keys():
                if key in ignore_keys:
                    result[key] = data[key]

            if isinstance(data['message'], (dict, list)):
                result['message'] = self.flatten_dictionary(result['message'])

            return super().render(
                data=result, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
        return super().render(
            data=data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
