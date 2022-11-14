import requests
from dotenv import load_dotenv

from snap import config

load_dotenv()
requests.packages.urllib3.disable_warnings()


class Fetchdata:
    def __init__(self):
        """Getfacts Blueprint, methods get_all_int will get all interfaces
        configured on the device, get_all_errors will generate all errors
        on the interface"""
        self.host = "wifi.hm.com"
        self.uri = "webacs/api/v4"
        self.json_config = ""

    def get_host_url(self, url: str):
        """Get host from URL"""
        self.url = "https://{prime_host}/{prime_uri}/{prime_url}".format(
            prime_host=self.host, prime_uri=self.uri, prime_url=url
        )
        self.HTTPMethod = "GET"
        self.httpresponse = Rest_connection.HTTPRequest(self)


class restConError(Exception):
    """
    Generic error raised by the restCon module.
    """


class restConRequestError(restConError):
    """
    Error raised by the restCon module when HTTP error code occurred.
    """


class Rest_connection:
    """HTTP REQUESTS"""

    def __init__(self):
        self.headers = ""

    def HTTPRequest(self):
        """Configure via REST"""
        self.headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        authentication = RestAuthentication(self.host)
        try:
            response = requests.request(
                self.HTTPMethod,
                self.url,
                auth=(authentication.user, authentication.password),
                headers=self.headers,
                data=self.json_config,
                verify=False,
            )
            if response.status_code == 200:
                response_json = response.json()
                self.response = response

            elif response.status_code == 302:
                raise restConRequestError("Incorrect credentials provided")
            elif response.status_code == 400:
                response_json = response.json()
                raise restConRequestError(
                    "Invalid request: %s" % response_json["errorDocument"]["message"]
                )
            elif response.status_code == 401:
                raise restConRequestError("Unauthorized access")
            else:
                raise restConRequestError(
                    "Unknown Request Error, return code is %s" % response.status_code
                )
        except requests.exceptions.RequestException:
            raise restConRequestError("Server is down")
        return self.response


class RestAuthentication:
    """GET ERRORS from network interfaces"""

    def __init__(self, host: str):
        """Blue print"""
        suser = config.TACACS_USERNAME
        spassword = config.TACACS_PASSWORD
        sysUser = config.TACACS_USERNAME
        sysPwd = config.TACACS_PASSWORD

        if host == "wifi.hm.com":
            self.host = host
            self.user = suser
            self.password = spassword
        else:
            self.debug = "second method"
            self.host = host
            self.user = sysUser
            self.password = sysPwd
