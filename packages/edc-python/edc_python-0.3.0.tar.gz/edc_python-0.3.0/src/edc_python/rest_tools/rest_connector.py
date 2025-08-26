from io import BytesIO
from json import JSONDecodeError
from requests import RequestException, Response
from requests.structures import CaseInsensitiveDict
# import urllib3
# from requests.auth import HTTPBasicAuth
from requests.sessions import Session
from edc_python.config import ConnectorConfig

class RestConnector(object):

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__()

        self._config = config

        self._session = Session() # config.rest_url)

        if config.header_api_key:
            self._session.headers.update({
            "x-api-key": config.header_api_key
        })

        # if config.rest_client_cert:
        #     if config.rest_client_key:  # when a key is present...
        #         self._session.cert = (config.rest_client_cert, config.rest_client_key)
        #     else:  # else use a single cert file (cert + key is expected to be in that file)
        #         self._session.cert = config.rest_client_cert

        # if config.rest_https_proxy:
        #     self._session.proxies.update({"https": config.rest_https_proxy})
        # if config.rest_http_proxy:
        #     self._session.proxies.update({"http": config.rest_http_proxy})

        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        # # if additional_headers:
        # #     self._session.headers.update(additional_headers)
        # if config.rest_bearer_token:
        #     self._session.headers.update({"Authorization": f"Bearer {config.rest_bearer_token}"})

        # self._session.verify = config.rest_ssl_verify

        # if config.rest_user and config.rest_password:
        #     self._session.auth = HTTPBasicAuth(config.rest_user, config.rest_password)

        # if not self._session.verify:
        #     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_downloadable_file_type(self, url: str) -> str:

        # Streaming, so we can iterate over the response.
        with self._session.get(url, stream=True, allow_redirects=True, headers={"accept": 'application/octet-stream', "content-type": 'application/octet-stream'}) as r:
            return r.headers.get('content-type')

    def download_file(self, url: str, target_file_path: str) -> CaseInsensitiveDict: #, mime_type: str='application/octet-stream'):

        # Streaming, so we can iterate over the response.
        with self._session.get(url, stream=True, allow_redirects=True, headers={'Accept': '*/*', "content-type": 'application/octet-stream'}) as r:
            with open(target_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return r.headers

    def download_file_without_saving(self, url: str, bio: BytesIO) -> CaseInsensitiveDict: #, mime_type: str='application/octet-stream'):

        # Streaming, so we can iterate over the response.
        with self._session.get(url, stream=True, allow_redirects=True, headers={"accept": 'application/octet-stream', "content-type": 'application/octet-stream'}) as r:
            bio.write(r.raw.read())
            return r.headers

    def get_raw(self, url, **kwargs):
        return self._session.get(url, **kwargs)

    def get(self, url, **kwargs):
        return self.safe_json_response_data(self._session.get(url, **kwargs), url, **kwargs)

    def head(self, url, **kwargs):
        return self.safe_json_response_data(self._session.head(url, **kwargs), url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.safe_json_response_data(self._session.post(url, data=data, json=json, **kwargs), url, data, json)
    
    def put_raw(self, url, data=None, **kwargs):
        return self._session.put(url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.safe_json_response_data(self._session.put(url, data=data, **kwargs), url, **kwargs)

    def delete(self, url, **kwargs):
        return self._session.delete(url, **kwargs)
    
    def safe_delete(self, url, **kwargs):
        return self.safe_json_response_data(self._session.delete(url, **kwargs), url, **kwargs)

    def safe_json_response_data(self, r: Response, url, data=None, json=None, **kwargs):
        """
        Returns the json representation of the response.

        Safe in this matter means that this function will raise on invalid status, however it also does its best to get
        a better error message from the response if there is any (compared to a plain Response.raise_for_status() call.

        :param r: The requests response
        :return: Json data
        """
        rdata = None
        try:
            rdata = r.json() if r.content else {}
            r.raise_for_status()
            return rdata
        except RequestException as e:
            if rdata:
                message = f"Api result error: {rdata}\nurl: {url}\ndata: {data}\njson: {json}"
            else:
                message = f"Api error, http code: {r.status_code}\nurl: {url}\ndata: {data}\njson: {json}"
            raise Exception(message, rdata) from e
        except JSONDecodeError as e:
            message = f"Api error. Response is no json: {r.content}"
            raise Exception(message, rdata) from e
