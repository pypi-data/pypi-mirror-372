from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
from IPython.display import display, Markdown
import requests
import polars as pl

JSONType = Union[Dict[str, Any], List[Any]]


# @dataclass
class Request:
    base_url: str = "http://localhost"
    api_version: str = "v1"
    api_port: Optional[int] = 11084
    resource_name: str = "users"
    headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Content-Type": "application/json",
        }
    )
    file_headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    verify: bool = True
    show_curl: bool = True
    verbose: bool = True
    _session: requests.Session = field(init=False, repr=False)

    def __post_init__(self):
        self._session = requests.Session()
        if self.headers:
            self._session.headers.update(self.headers)

    def set_bearer(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    def set_basic(self, username: str, password: str):
        self._session.auth = (username, password)
        return self

    def _join(self, *parts: str) -> str:
        return "/".join(
            str(p).strip("/") for p in parts if p is not None and str(p) != ""
        )

    def _base(self) -> str:
        if self.api_port is not None and ":" not in self.base_url.split("//")[-1]:
            return f"{self.base_url}:{self.api_port}"
        return self.base_url

    def _url(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        path = self._join(
            self.api_version,
            self.resource_name,
            str(id) if id is not None else None,
            endpoint,
        )
        url = f"{self._base()}/{path}"
        if params:
            url += f"?{urlencode(params, doseq=True)}"
        return url

    def _curl(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        payload: Optional[Dict[str, Any]],
        files: Optional[List[Tuple]],
    ):
        if not self.show_curl:
            return
        parts = [f"curl -X {method.upper()} '{url}'"]
        for k, v in headers.items():
            parts.append(f"-H '{k}: {v}'")
        if files:
            for f in files:
                if len(f) == 2:
                    k, fp = f
                    parts.append(f"-F '{k}=@{getattr(fp, 'name', 'file')}'")
                else:
                    k, fp, meta = f
                    parts.append(
                        f"-F '{k}=@{getattr(fp, 'name', 'file')};type={meta.get('Content-Type', 'application/octet-stream')}'"
                    )
        elif payload is not None:
            parts.append(f"-d '{requests.utils.requote_uri(str(payload))}'")
        display(" ".join(parts))

    def _display(
        self,
        response: requests.Response,
        key: Optional[str] = None,
        to_polars: bool = False,
    ):
        status = response.status_code
        try:
            data = response.json()
            bucket = key or ("data" if response.ok else "errors")
            header = f"**[ Response - {status} ]**" + (
                f" - *status*: {data.get('status', '')}"
                if isinstance(data, dict)
                else ""
            )
            header += (
                f" - *message*: {data.get('message', '')}"
                if isinstance(data, dict) and data.get("message")
                else ""
            )
            header += f" - **{bucket}**:"
            if self.verbose:
                display(Markdown(header))
            content = data.get(bucket) if isinstance(data, dict) else data
            if to_polars and isinstance(content, list):
                try:
                    df = pl.DataFrame(content)
                    display(df)
                except Exception:
                    display(content)
            else:
                display(content)
        except ValueError:
            if self.verbose:
                display(Markdown(f"**[ Response - {status} ]** - *non-JSON body*:"))
            display(response.text)

    def request(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._url(id=id, endpoint=endpoint, params=params)
        if self.verbose:
            display(f"URL: {url}")

        hdrs = dict(self._session.headers)
        if headers:
            hdrs.update(headers)

        self._curl(method, url, hdrs, payload if files is None else None, files)

        if files is not None:
            effective_headers = {
                k: v for k, v in hdrs.items() if k.lower() != "content-type"
            }
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=effective_headers,
                data=payload,
                files=files,
                timeout=timeout or self.timeout,
                verify=self.verify,
            )
        else:
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=hdrs,
                json=payload,
                timeout=timeout or self.timeout,
                verify=self.verify,
            )

        self._display(resp, key=key, to_polars=to_polars)
        return resp

    def get(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "GET",
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            key=key,
            to_polars=to_polars,
            timeout=timeout,
        )

    def post(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ):
        local_headers = self.file_headers if files else None
        if headers and local_headers:
            local_headers = {**local_headers, **headers}
        elif headers:
            local_headers = headers
        return self.request(
            "POST",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            files=files,
            headers=local_headers,
            key=key,
            to_polars=to_polars,
            timeout=timeout,
        )

    def put(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "PUT",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            key=key,
            to_polars=to_polars,
            timeout=timeout,
        )

    def patch(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "PATCH",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            key=key,
            to_polars=to_polars,
            timeout=timeout,
        )

    def delete(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "DELETE",
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            key=key,
            to_polars=to_polars,
            timeout=timeout,
        )

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)
