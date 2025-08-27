import json
import jwt
import time
import requests
from ..config.config import config
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class AGClient:
    """
    Class to test AGClient when the AG Server with Oblv server is not available. 
    Instead using AG private python server directly(passing custom x_oblv_name headers).
    """
    def __init__(
        self,
        URL,
        PORT,
        headers={},
    ):
        self.url = URL
        self.port = PORT
        self.base_url = URL + ":" + PORT
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def get(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "GET", endpoint, data=data, json=json, params=params, headers=headers
        )

    def post(self, endpoint, data=None, json=None, params=None, headers=None, files=None):
        return self._make_request(
            "POST", endpoint, data=data, json=json, params=params, headers=headers, files=files
        )

    def put(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "PUT", endpoint, data=data, json=json, params=params, headers=headers
        )

    def delete(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "DELETE", endpoint, data=data, json=json, params=params, headers=headers
        )
    
    def __is_token_expired(self) -> bool:
        try:
            payload = jwt.decode(self.session.headers['Authorization'], options={"verify_signature": False})
            current_time = time.time() + 10  # 10 seconds for network latency

            return payload.get('exp', 0) < current_time
        except Exception as e:
            raise ConnectionError(f"Error while checking token expiry: {str(e)}")

    def __get_refresh_token(self) -> None:
        try:
            if not self.__is_token_expired():
                return
            res = requests.post(
                config.AGENT_CONSOLE_URL + "/jupyter/token/refresh",
                json={"refresh_token": self.session.headers.get('refresh_token')},
            )
            res.raise_for_status()
            data = json.loads(res.text)
            self.session.headers['refresh_token'] = data.get("refresh_token")
            self.session.headers['Authorization'] = data.get("access_token")
        except Exception as e:
            raise ConnectionError(f"Error while refreshing token")

    def _make_request(
        self, method, endpoint, data=None, json=None, params=None, headers=None, files=None
    ):
        if self.session.headers.get('Authorization'):
            self.__get_refresh_token()
        url = endpoint
        verify = True
        if hasattr(config, 'TLS_ENABLED'):
            verify = config.TLS_ENABLED.lower() == "true"
            if not verify:
                urllib3.disable_warnings(InsecureRequestWarning)
        if headers:
            with self.session as s:
                s.headers.update(headers)
                response = s.request(method, url, data=data, json=json, params=params, files=files, verify=verify)
                s.headers.update(self.session.headers)
        else:
            response = self.session.request(
                method, url, data=data, json=json, params=params, verify=verify
            )
        return response


def get_ag_client():
    """
    Connect to AG server Server and initialize the Oblv client, AG server Server URL and port from config.
    """
    return AGClient(
        config.AGENT_JUPYTER_URL,
        config.AGENT_JUPYTER_PORT,
    )
