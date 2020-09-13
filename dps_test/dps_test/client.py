import requests

class APIClient:
    def __init__(self, url):
        if url[-1] is not '/':
            url += '/'
        self.url = url
        self.server_info = self.info().json()
        self.server_type = self.server_info['type']
        self.debug = self.server_info['debug']

    def info(self):
        return self._GET('info')

    def _make_url(self, endpoint):
        return self.url + 'api/v1/' + endpoint

    def _POST(self, endpoint, jo={}):
        return requests.post(self._make_url(endpoint), json=jo)

    def _GET(self, endpoint, jo={}):
        return requests.get(self._make_url(endpoint))

    def _validate_response(response):
        status_code = response.status_code
        if status_code is not 200:
            return False
        return True

    def _print_error(response):
        jo = response.json()
        for error in jo['error']:
            print(error)
