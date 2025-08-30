import jwt
import requests
from ..base import schemas


class ApiClient:

    def __init__(self, base_url: str):
        self.base_url: str = base_url
        self.token: schemas.LoginOut | None = None
        self.user: schemas.UserLoginOut | None = None
        self.ins = requests

    def make_headers(self, url: str, custom_headers: dict | None = None):
        headers = {}
        if self.token and not url.startswith("/open"):
            headers["Authorization"] = f"Bearer {self.token.access_token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers
    def raise_for_resp(self, resp):
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") != 200:
            raise Exception(result.get("message"))
        return result.get("data")

    def login(self, username: str, password: str, client_id: str, grant_type: str):
        data = {"username": username, "password": password, "client_id": client_id, "grant_type": grant_type}
        resp = self.post(f"{self.base_url}/open/login", data=data)
        self.token = schemas.LoginOut.model_validate(resp)
        payload = jwt.decode(self.token.access_token, options={"verify_signature": False})
        self.user = schemas.UserLoginOut.model_validate_json(payload.get("signature_data"))
        return payload
    
    def register(self, username: str, password: str, password_two: str):
        return self.post(f"{self.base_url}/open/register", json={"username": username, "password": password, "password_two": password_two})
    

    def recharge(self, username: str, password: str,card_number: str):
        return self.post(f"{self.base_url}/biz/recharge/cards/recharge", json={"username": username, "password": password, "card_number": card_number})
    
    def softwares_verify(self, software_name: str, password: str):
        return self.post(f"{self.base_url}/biz/softwares/verify", json={"name": software_name, "password": password})
       
    def softwares_upgrade(self, software_name: str):
        return self.get(f"{self.base_url}/biz/softwares/upgrade", params={"name": software_name})

    def change_password(self, password_old: str, password: str, password_two: str):
        return self.post(f"{self.base_url}/auth/user/change/password", json={"password_old": password_old, "password": password, "password_two": password_two})

    def request(self, method: str, url: str, **kwargs):
        """
        统一请求方法，自动带上headers，Content-Type自适应，处理响应。
        """
        full_url = url if url.startswith("http") else f"{self.base_url}{url}"
        headers = kwargs.pop("headers", {}) or {}
        # Content-Type自适应
        if "Content-Type" not in {k.title(): v for k, v in headers.items()}:
            if "json" in kwargs:
                headers["Content-Type"] = "application/json"
            elif "data" in kwargs and isinstance(kwargs["data"], dict):
                headers["Content-Type"] = "application/x-www-form-urlencoded"
        all_headers = self.make_headers(url,headers)
        resp = self.ins.request(method, full_url, headers=all_headers, **kwargs)
        return self.raise_for_resp(resp)

    def get(self, url: str, **kwargs):
        """GET 请求封装"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        """POST 请求封装"""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        """PUT 请求封装"""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        """DELETE 请求封装"""
        return self.request("DELETE", url, **kwargs)
