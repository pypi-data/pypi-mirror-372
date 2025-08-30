import json
from lisdk.rsak import RSAK
from lisdk.utils import ApiUtils
from lisdk.httpc import HttpClient
from typing_extensions import Self # type: ignore


class KaClient(HttpClient):

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, *, domain, appid, priKeyPath, pubKeyPath):
        if not self._initialized:
            self.appid = appid
            self.priKey = RSAK.readRSAKey(priKeyPath)
            self.pubKey = RSAK.readRSAKey(pubKeyPath)
            super().__init__(domain)
            self._initialized = True

    def __str__(self) -> str:
        return f"{self.appid}, {self.priKey}, {self.pubKey}"

    def _call(self, *, endpoint, method, headers, biz_body, **kwargs):
        """ 调用KA接口, 并进行签名与验证 """
        payload = self._ka_body()
        payload['request']['body'].update(biz_body)
        payload['signature'] = RSAK.getSignature(rsaKey=self.priKey, data=payload.get('request')) # type: ignore
        allinfo = super()._call(endpoint=endpoint, method=method, headers=headers, payload=payload, **kwargs)
        ResponseBody = allinfo.get('ResponseBody')
        response = ResponseBody['response'] # type: ignore
        response_signature = ResponseBody['signature'] # type: ignore
        varify_result = RSAK.verifySignature(rsaKey=self.pubKey, data=response, signature=response_signature) # type: ignore
        if not varify_result:
            raise Exception('签名验证失败')
        return allinfo
    
    def _ka_body(self):
        """ 生成KA接口报文标准格式 """
        payload = {
            "request": {
                "head": {
                    "version": "1.0.0",
                    "appid": self.appid,
                    "sign_type": "SHA256",
                    "request_time": ApiUtils.now(),
                },
                "body": dict(),
            },
            "signature": ""
        }
        return payload