import re

import requests
try:
    import aiohttp
except ImportError:
    aiohttp = None

from .exceptions import QujingInvokeError


class QujingByHttp:
    def __init__(self, host, port_config=61000, protocol="http"):
        self.host = host
        self.port_config = port_config
        self.protocol = protocol
        self.base_config_url = f"{self.protocol}://{self.host}:{self.port_config}"
        self.base_invoke_url = f"{self.protocol}://{self.host}:$port/invoke"

    def get_pid(self, packages: list, **kwargs):
        # 获取包名对应的进程号，即端口号
        url = f"{self.base_config_url}/manualguid"
        kwargs.setdefault("timeout", 5)
        resp = requests.get(url, **kwargs)
        ports = {package: re.findall(f"<td>{package}</td>.*?<td>(.*?)</td>", resp.text, re.S) for package in packages}
        ports = {package: int(port[0]) for package, port in ports.items() if len(port)}
        return ports

    def set_app(self, packages: list, **kwargs):
        # 设置目标app，设置后才能通过invoke接口调用
        url = f"{self.base_config_url}/settargetapp"
        params = {i: i for i in packages}
        kwargs.setdefault("timeout", 5)
        resp = requests.get(url, params=params, **kwargs)
        return resp.status_code == 200

    def invoke(self, port_invoke: int, data: dict, **kwargs):
        # 调用目标app内部函数的接口
        url = self.base_invoke_url.replace("$port", str(port_invoke))
        kwargs.setdefault("timeout", 5)
        try:
            resp = requests.post(url, data=data, **kwargs)
        except Exception as e:
            raise QujingInvokeError({"code": 500, "data": data, "error": str(e), "type": "error"})
        # 处理返回的数据
        _text = resp.text.strip()
        if _text.startswith("Base64#"):
            datatype = "base64"
            resp_data = _text[7:]
        elif _text.startswith("raw#"):
            datatype = "raw"
            resp_data = _text[4:]
        else:
            datatype = "raw"
            resp_data = _text
        return {"data": resp_data, "dtype": datatype}


class AsyncQujingByHttp:
    """异步版本的QujingByHttp类，用于协程环境"""
    
    def __init__(self, host, port_config=61000, protocol="http"):
        if aiohttp is None:
            raise ImportError("aiohttp is required for async functionality. Install it with: pip install aiohttp")
        self.host = host
        self.port_config = port_config
        self.protocol = protocol
        self.base_config_url = f"{self.protocol}://{self.host}:{self.port_config}"
        self.base_invoke_url = f"{self.protocol}://{self.host}:$port/invoke"

    async def get_pid(self, packages: list, **kwargs):
        """异步获取包名对应的进程号，即端口号"""
        url = f"{self.base_config_url}/manualguid"
        timeout = aiohttp.ClientTimeout(total=kwargs.pop("timeout", 5))
        
        async with aiohttp.ClientSession(timeout=timeout, **kwargs) as session:
            async with session.get(url) as resp:
                text = await resp.text()
                ports = {package: re.findall(f"<td>{package}</td>.*?<td>(.*?)</td>", text, re.S) for package in packages}
                ports = {package: int(port[0]) for package, port in ports.items() if len(port)}
                return ports

    async def set_app(self, packages: list, **kwargs):
        """异步设置目标app，设置后才能通过invoke接口调用"""
        url = f"{self.base_config_url}/settargetapp"
        params = {i: i for i in packages}
        timeout = aiohttp.ClientTimeout(total=kwargs.pop("timeout", 5))
        
        async with aiohttp.ClientSession(timeout=timeout, **kwargs) as session:
            async with session.get(url, params=params) as resp:
                return resp.status == 200

    async def invoke(self, port_invoke: int, data: dict, **kwargs):
        """异步调用目标app内部函数的接口"""
        url = self.base_invoke_url.replace("$port", str(port_invoke))
        timeout = aiohttp.ClientTimeout(total=kwargs.pop("timeout", 5))
        
        try:
            async with aiohttp.ClientSession(timeout=timeout, **kwargs) as session:
                async with session.post(url, data=data) as resp:
                    text = await resp.text()
        except Exception as e:
            raise QujingInvokeError({"code": 500, "data": data, "error": str(e), "type": "error"})
        
        # 处理返回的数据
        _text = text.strip()
        if _text.startswith("Base64#"):
            datatype = "base64"
            resp_data = _text[7:]
        elif _text.startswith("raw#"):
            datatype = "raw"
            resp_data = _text[4:]
        else:
            datatype = "raw"
            resp_data = _text
        return {"data": resp_data, "dtype": datatype}
