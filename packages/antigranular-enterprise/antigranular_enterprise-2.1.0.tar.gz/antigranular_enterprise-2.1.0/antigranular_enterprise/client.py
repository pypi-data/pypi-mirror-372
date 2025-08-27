"""
Module for AGClient class.

AGClient class contians all the methods to interact with the AG server like creating a session, uploading results, etc.
It also contains methods to get the budget, privacy odometer, etc.

"""
import pickle
import requests
import json
from typing import Any, Dict, Union
import base64
import platform
from antigranular_enterprise.utils.error_print import eprint

try:
    import onnx
    onnx_installed = True
except ImportError:
    onnx_installed = False
from IPython import get_ipython
if get_ipython():
    from .magics.magics import AGMagic
from .agent_client.agent_client import get_ag_client, AGClient
from .config.config import config
from .models.models import AGServerInfo
import pandas as pd
from io import BytesIO
from .utils.print_request_id import print_request_id
import time
from collections import OrderedDict
import jwt
import time
from uuid import uuid4
import psutil
def login(
        api_key: str = None,
        token: str = None,
        profile: str = "default"
):
    """
    Login to the AG server and get the client objects.
    Returns:
        AGClient: The AGClient object.

    Raises:
        ConnectionError: If there is an error while creating the client.
    """
    try:
        return AGClient(
            api_key,
            profile,
            token
        )
    except Exception as err:
        raise ConnectionError(f"Error while creating client: {str(err)}")

def read_config(profile="default") -> None:
    """
    Reads the configuration from a given profile.

    Args:
        profile (str): The profile to read the configuration from.
    """
    config.read_config(profile=profile)

def write_config(yaml_config, profile) -> None:
    """
    Writes the configuration to a given profile.

    Args:
        yaml_config (dict): The configuration to write.
        profile (str): The profile to write the configuration to.
    """
    config.write_config(yaml_config, profile)

def load_config(config_url=None, profile="default") -> None:
    """
    Load the configuration from the given URL.

    Args:
        config_url (str): The URL to load the configuration from.
        profile (str): The profile to load the configuration to.
    """
    config.load_config(config_url, profile)
    
def get_nic_id():
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family.name in ["AF_PACKET", "AF_LINK"]:
                mac_address = snic.address
                # Skip empty or placeholder MAC addresses
                if mac_address and mac_address != "00:00:00:00:00:00":
                    return mac_address.upper()
    return None

class AGClient:
    """
    AGClient class to interact with the AG server for competitions as well as accessing datasets for functionalities like creating a session, uploading competition submissions, downloading metadata, etc.
    """

    __UUID = str(uuid4())
    
    __os = platform.platform()
    __nic_id = get_nic_id()
    __oblv_ag: AGClient
    session_id: str

    def __init__(
        self,
        api_key: str = None,
        profile: str = "default",
        token: str = None
    ):
        """
        Initialize AGClient class and check for headers if Client.

        Raises:
            ConnectionError: If there is an error while connecting to the server.
        """
        config.load_config(profile=profile)
        # Make client if headers are provided
        self.__oblv_ag = get_ag_client()
        self.__headers = {
            "Content-type": "application/json",
            "accept": "application/json",
            "Authorization": "",
            "refresh_token": ""
        }
        
        if token:
            # Exchange external token for internal tokens
            try:
                exchanged_token = self.__exchange_token(token)
                self.__headers['Authorization'] = exchanged_token['access_token']
                self.__headers['refresh_token'] = exchanged_token.get('refresh_token', '')
            except Exception as e:
                raise ConnectionError(f"Token exchange failed: {str(e)}")
        elif not isinstance(api_key, str) or api_key.strip() == "":
                raise ValueError("Either api_key or token must be provided")
            
        # Create an AG session if we have authorization or api_key
        if self.__headers.get('Authorization') or api_key:
            self.__connect(api_key)

        if hasattr(self, 'session_id'):
            try:
                print(f"Connected to Antigranular server session id: {str(self.session_id)}")
                if get_ipython():
                    res = AGMagic.load_ag_magic()
                    print("Cell magic '%%ag' registered successfully, use `%%ag` in a notebook cell to execute your python code on Antigranular private python server")
                else:
                    self.execute = self.__session_execute
            except Exception as ex:
                print(
                    "Error loading %%ag magic functions, you might not be able to use cell magics as intended: ",
                    str(ex),
                )
            if get_ipython():
                AGMagic.load_oblv_client(ag_server=self.__oblv_ag, session_id=self.session_id)

    @classmethod
    def _from_agent_client(cls, ag_client_secret):
        """
        Initialize AGClient class from Client.
        """
        return cls(ag_client_secret)

    def __exchange_token(self, external_token: str) -> Dict[str, str]:
        """
        Exchange an external token for internal tokens using OAuth 2.0 token exchange flow.
        
        Args:
            external_token (str): The external token to exchange
            
        Returns:
            Dict[str, str]: Dictionary containing access_token and refresh_token
            
        Raises:
            ConnectionError: If there is an error during token exchange
        """
        try:
            
            
            token_exchange_params = {
                "subject_token": external_token
            }
            token_exchange_url = config.AGENT_CONSOLE_URL + '/auth/exchange_token'
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            response = requests.post(
                token_exchange_url,
                data=token_exchange_params,
                headers=headers,
                timeout=10,  # Add timeout for the request
                stream=True
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            # Validate response contains required tokens
            if "access_token" not in token_data:
                raise ValueError("Token exchange response missing access_token")
                
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "token_type": token_data.get("token_type", "Bearer")
            }
            
        except requests.exceptions.HTTPError as e:
            error_details = ""
            try:
                error_response = e.response.json()
                error_details = f" - {error_response.get('error_description', error_response.get('error', ''))}"
            except Exception:
                error_details = f" - {e.response.text}"
            raise ConnectionError(f"Token exchange failed with HTTP {e.response.status_code}{error_details}")
        except requests.exceptions.Timeout:
            raise ConnectionError("Token exchange request timed out")
        except Exception as e:
            raise ConnectionError(f"Error during token exchange.")

    def __is_token_expired(self) -> bool:
        try:
            payload = jwt.decode(self.__headers['Authorization'], options={"verify_signature": False})
            current_time = time.time() + 10 # 10 seconds for network latency
            return payload.get('exp', 0) < current_time
        except Exception as e:
            raise ConnectionError(f"Error while checking token expiry: {str(e)}")

    def __get_refresh_token(self) -> None:
        try:
            if not self.__is_token_expired():
                return
            res = requests.post(
                config.AGENT_CONSOLE_URL + "/jupyter/token/refresh",
                json={"refresh_token": self.__headers.get('refresh_token')},
            )
            res.raise_for_status()
            data = json.loads(res.text)
            self.__headers['Authorization'] = data.get("access_token")
            self.__headers['refresh_token'] = data.get("refresh_token")
        except Exception:
            raise ConnectionError("Error while refreshing token")

    def __connect(self, api_key: str = None) -> None:
        try:
            # If we already have an authorization token (from token exchange), skip the login flow
            if (not self.__headers.get('Authorization')) and api_key:
                # Original login flow for API key authentication
                params = {"apikey": api_key}
                try: 
                    api_path = "/jupyter/login/request"
                    params = {
                        **params,
                        "machine_uuid": self.__UUID,
                        "os": self.__os,
                    }
                    if self.__nic_id:
                        params["nic_id"] = self.__nic_id
                    response = requests.post(config.AGENT_CONSOLE_URL + api_path, json=params, stream=True)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(f"Error while requesting token: {str(err)}")
                
                if get_ipython():
                    for line in response.iter_lines():
                        if line:
                            json_obj = line.decode().strip()
                            if json_obj.startswith('data: '):
                                try:
                                    data = json.loads(json_obj[6:])  # Parse JSON directly from the sliced string
                                    self.__process_message(data)
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing JSON: {e}")
                else:
                    self.__process_message(response)
            
            # Create session if we have authorization token
            if self.__headers.get('Authorization') != "":
                try:
                    res = self.__exec(
                        "POST",
                        "/start-session",
                        headers=self.__headers,
                    )
                    if res.status_code != 200:
                        raise requests.exceptions.HTTPError(
                            f"Error while starting a new session in server status code: {res.status_code} message: {res.text}"
                        )
                    self.session_id = json.loads(res.text)["session_id"]
                except Exception as err:
                    raise ConnectionError(f"Error calling /start-session: {str(err)}")
            else:
                message = "Error during authentication. Please ensure login approval on AGENT Console or provide a valid token."
                if get_ipython():
                    eprint(message)
                else:
                    raise SystemExit(eprint(message))

        except Exception as err:
            raise ConnectionError(f"Error while creating client: {str(err)}")
    
    def __process_message(self, data: Union[Dict[str, Any], requests.Response]) -> None:
        # Handle both dict (from JSON) and Response object
        data_dict = data.json() if isinstance(data, requests.Response) else data
            
        approval_status = data_dict.get('approval_status')
        if approval_status == 'approved':
            token = data_dict.get('access_token')
            if token:
                self.__headers['Authorization'] = data_dict.get('access_token')
                self.__headers['refresh_token'] = data_dict.get('refresh_token', '')
                if get_ipython():
                    print("\033[92m" + "Request approved." + "\033[0m")
            else:
                print("Token not found in the approved message.")
        elif approval_status == 'pending':
            print(f"Your request is pending approval. Please visit the following URL to approve the request: {data_dict.get('approval_url', '')}")
        elif approval_status == 'expired':
            print("\033[91m Request Expired \033[0m")
        elif approval_status == 'failed':
            print(f"\033[91m {json.dumps(data_dict, indent=2)} \033[0m")

    def __get_output(self, message_id, globals_dict) -> None:
        """
        Retrieves the code execution output from the Antigranular server.
        """
        count = 1
        return_value = ""
        if get_ipython():
            return_output = False
        else:
            return_output = True
        while True:
            if count > int(config.AG_EXEC_TIMEOUT):
                if return_output:
                    return_value += "Error : AG execution timeout."
                else:
                    print("Error : AG execution timeout.")
                break
            try:
                res = self.__exec(
                    "GET",
                    "/sessions/output",
                    params={"session_id": self.session_id}
                )
            except Exception as err:
                raise ConnectionError(
                    f"Error during code execution on AG Server: {str(err)}"
                )
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while requesting AG server for output, HTTP status code: {res.status_code}, message: {res.text}"
                )
            kernel_messages = json.loads(res.text)["output_list"]
            for message in kernel_messages:
                if message.get("parent_header", {}).get("msg_id") == message_id:
                    if message["msg_type"] == "status":
                        if message["content"]["execution_state"] == "idle":
                            return None if return_value == '' else return_value
                    elif message["msg_type"] == "stream":
                        if (message["content"]["name"] == "stdout") or (message["content"]["name"] == "stderr"):
                            if return_output:
                                return_value += message["content"]["text"]
                            else:
                                print(message["content"]["text"])
                    elif message["msg_type"] == "error":
                        tb_str = ""
                        for tb in message["content"]["traceback"]:
                            tb_str += tb

                        if return_output:
                            raise SystemExit(tb_str)
                        else:
                            print(tb_str)
                            return None
                    elif message["msg_type"] == "ag_export_value":
                        try:
                            data = message["content"]
                            for name, value in data.items():
                                globals_dict[name] = pickle.loads(base64.b64decode(value))
                                print(
                                    "Setting up exported variable in local environment:",
                                    name,
                                )
                        except Exception as err:
                            raise ValueError(
                                f"Error while parsing export values message: {str(err)}"
                            )
            time.sleep(1)
            count += 1
        return None if return_value == '' else return_value
    
    def __session_execute(self, code, globals_dict={}) -> None:
        if not code:
            raise ValueError("Code must be provided.")
        try:
            res = self.__exec(
                "POST",
                "/sessions/execute",
                headers=self.__headers,
                json={"session_id": self.session_id, "code": code},
            )
        except Exception as err:
            raise ConnectionError(f"Error calling /sessions/execute: {str(err)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while executing the provided compute operation in the server status code: {res.status_code} message: {res.text}"
                )
            res_body_dict = json.loads(res.text)
            return self.__get_output(res_body_dict.get('message_id'), globals_dict)

    def interrupt_kernel(self) -> dict:
        try:
            res = self.__exec(
                "POST",
                "/sessions/interrupt-kernel",
                headers=self.__headers,
                json={"session_id": self.session_id},
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /sessions/interrupt-kernel: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while fetching the interrupt-kernel, HTTP status code: {res.status_code}, message: {res.text}"
                )
            return json.loads(res.text)

    def terminate_session(self) -> dict:
        try:
            res = self.__exec(
                "POST",
                "/sessions/terminate-session",
                headers=self.__headers,
                json={"session_id": self.session_id},
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /terminate-session: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while fetching the terminate-session, HTTP status code: {res.status_code}, message: {res.text}"
                )
            requests.delete(
                config.AGENT_CONSOLE_URL + "/jupyter/logout",
                json={"refresh_token": self.__headers.get('refresh_token')},
            )
            return json.loads(res.text)
                
    def __active_count(self) -> dict:
        """
        Get the active count.
        """
        try:
            res = self.__exec("GET", "/sessions/active-count", headers=self.__headers)
        except Exception as e:
            raise ConnectionError(f"Error calling /sessions/active-count: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while fetching the __active_count, HTTP status code: {res.status_code}, message: {res.text}"
                )
            return json.loads(res.text)
    
    def __print_json_table(self, data):

        longest_key = max(len(key) for key in data)

        print("Metric", "Value".rjust(longest_key + 5), sep='  ')

        print("-" * (longest_key + 2), "-" * 10, sep='-+-')

        # Print each key-value pair in the dictionary
        for key, value in data.items():
            print(f"{key.ljust(longest_key)} | {str(value).rjust(10)}")

    def privacy_odometer(self, lifetime=False) -> None:
        """
        Get the privacy odometer.

        Raises:
            ConnectionError: If there is an error while calling /privacy_odometer.
            requests.exceptions.HTTPError: If there is an error while fetching the privacy odometer.
        """
        try:
            res = self.__exec(
                "GET",
                "/sessions/privacy_odometer",
                params={"session_id": self.session_id, "show_only_session_budgets": not lifetime},
                headers=self.__headers,
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /privacy_odometer: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while fetching the privacy odometer, HTTP status code: {res.status_code}, message: {res.text}"
                )
            return self.__print_json_table(json.loads(res.text))

    def __load(self, name, data_type: str, metadata: dict, categorical_metadata: dict, is_private: bool) -> None:
        if data_type == "model":
            code = f"{name} = load_model('{name}')"
        if data_type == "dataframe" or data_type == "series":
            code = f"{name} = load_dataframe('{name}', metadata={metadata}, categorical_metadata={categorical_metadata}, is_private={is_private}, data_type='{data_type}')"
        if data_type == "dict" or data_type == "OrderedDict":
            code = f"{name} = load_dict('{name}', data_type='{data_type}')"
        try:
            self.__session_execute(code)
        except Exception as e:
            raise ConnectionError(f"Error calling /sessions/execute: {str(e)}")
    
    def private_import(self, data=None, name: str = None, path=None, is_private=False, metadata={}, categorical_metadata={}) -> None:
        """
        Load a user provided model or dataset into the AG server.

        Parameters:
            name (str): The name to use for the model or dataset.
            data (onnx.ModelProto, pd.DataFrame, dict, OrderedDict, pd.Series): The data to load. Defaults to None.
            path (str, optional): The path to the model, the external data should be under the same directory of the model. Defaults to None.
            is_private (bool, optional): Whether the data is private. Defaults to False.
            metadata (dict, optional): The metadata for the dataset. Defaults to {}.
            categorical_metadata (dict, optional): The categorical metadata for the dataset. Defaults to {}.
        Returns:
            None
        """
        if (name is None) or (not isinstance(name, str) and not name.isidentifier()):
            raise ValueError("name must be a valid identifier")
        if not (data is None or path is None):
            raise ValueError("Both data and path cannot be provided, please provide only one of them")
        if isinstance(data, pd.DataFrame):
            res = self.__exec(
                "POST",
                "/sessions/cache_data",
                headers=self.__headers,
                json={"session_id": self.session_id, "data": base64.b64encode(data.to_csv(index=True).encode()).decode(), "name": name},
            )
            data_type = "dataframe"
        elif isinstance(data, pd.Series):
            res = self.__exec(
                "POST",
                "/sessions/cache_data",
                headers=self.__headers,
                json={"session_id": self.session_id, "data": base64.b64encode(data.to_csv(header=False).encode()).decode(), "name": name},
            )
            data_type = "series"
        elif onnx_installed and isinstance(data, onnx.ModelProto):
            try:
                onnx.checker.check_model(data)
                onnx_bytes_io = BytesIO()
                onnx_bytes_io.seek(0)
                onnx.save_model(data, onnx_bytes_io)
            except Exception as e:
                raise ValueError(f"Invalid ONNX model: {str(e)}")
            res = self.__exec(
                "POST",
                "/sessions/cache_model",
                headers=self.__headers,
                json={"session_id": self.session_id, "name": name, "model": base64.b64encode(onnx_bytes_io.getvalue()).decode()},
            )
            data_type = "model"
        elif isinstance(data, (dict, OrderedDict)):
            res = self.__exec(
                "POST",
                "/sessions/cache_data",
                headers=self.__headers,
                json={"session_id": self.session_id, "data": base64.b64encode(json.dumps(data).encode()).decode(), "name": name},
            )
            data_type = "dict" if isinstance(data, dict) else "OrderedDict"
        elif path:
            if not onnx_installed:
                raise ValueError("ONNX is not installed, please install ONNX to use this feature")
            if not path.endswith(".onnx"):
                raise ValueError("Invalid model file format, only .onnx files are supported")
            try:
                onnx_model = onnx.load(path)
                onnx.checker.check_model(onnx_model)
            except Exception as e:
                raise ValueError(f"Invalid ONNX model: {str(e)}")
            res = self.__exec(
                "POST",
                "/sessions/cache_model",
                headers=self.__headers,
                json={"session_id": self.session_id, "name": name, "model": base64.b64encode(open(path, "rb").read()).decode()},
            )
            data_type = "model"
        else:
            raise ValueError("Either a DataFrame, ONNX model, or path must be provided")
        

        if res.status_code != 200:
            raise requests.exceptions.HTTPError(
                print_request_id(f"Error: {res.text}", res)
            )
        else:
            print(f"{data_type} cached to server, loading to kernel...")
            self.__load(name, data_type, metadata, categorical_metadata, is_private)

    # Use Oblv Client server to make HTTP requests
    def __exec(self, method, endpoint, data="", json={}, params={}, headers={}, files=None):
        """
        Execute an HTTP request using the Oblv Client server.

        Parameters:
            method (str): The HTTP method.
            endpoint (str): The endpoint URL.
            data (Any, optional): The request data. Defaults to None.
            json (Any, optional): The request JSON. Defaults to None.
            params (dict, optional): The request parameters. Defaults to None.
            headers (dict, optional): The request headers. Defaults to None.

        Returns:
            Response: The HTTP response.

        Raises:
            ValueError: If the method is not supported by the client.
        """
        if hasattr(self, 'session_id'):
            self.__get_refresh_token()
        url_endpoint = f"{self.__oblv_ag.url}:{self.__oblv_ag.port}{endpoint}"
        if method == "GET":
            r = self.__oblv_ag.get(
                url_endpoint,
                json=json,
                params=params,
                headers=headers,
            )
        elif method == "POST":
            r = self.__oblv_ag.post(
                url_endpoint, json=json, params=params, headers=headers, files=files
            )
        elif method == "PUT":
            r = self.__oblv_ag.put(
                url_endpoint, json=json, params=params, headers=headers
            )
        elif method == "DELETE":
            r = self.__oblv_ag.delete(
                url_endpoint, json=json, params=params, headers=headers
            )
        else:
            raise ValueError(f"{method} not supported by client")
        return r