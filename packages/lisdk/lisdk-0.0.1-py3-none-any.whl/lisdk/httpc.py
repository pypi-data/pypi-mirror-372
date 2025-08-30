import requests
from abc import ABC

class HttpClient(ABC):
    
    def __init__(self, domain: str):
        self.domain = domain
        self.http = requests

    def _call(self,*, endpoint, method, headers, payload, **kwargs):
        url = self.domain + endpoint
        response = self.http.request(method=method, url=url, headers=headers, json=payload, **kwargs)
        allinfo = {
            "URL": url,
            "METHOD": method,
            "HEADERS": headers,
            "RequestBody": payload
        }
        try:
            allinfo['ResponseBody'] = response.json()
        except:
            allinfo['ResponseBody'] = response.text
        finally:
            return allinfo
