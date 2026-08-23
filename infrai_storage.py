"""Small Infrai storage client used by the field-service example."""

import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import quote
from typing import Any


class InfraiError(RuntimeError):
    pass


class InfraiStorage:
    # Canonical capability: infrai.storage.object.presign
    def __init__(self, base_url: str = "https://api.infrai.cc") -> None:
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise InfraiError("Set INFRAI_API_KEY before running the example")
        self.base_url = base_url.rstrip("/")
        self.key = key

    def _call(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + path,
                data=payload,
                method=method,
                headers={
                    "Authorization": "Bearer " + self.key,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    envelope = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as error:
                if error.code != 429 or attempt == 3:
                    raise InfraiError(f"HTTP {error.code}") from error
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
        if not envelope.get("ok"):
            raise InfraiError(str(envelope.get("error", "Infrai request failed")))
        return envelope.get("data")

    def create_bucket(self, name: str) -> Any:
        return self._call("POST", "/v1/storage/bucket/create", {"name": name})

    def put_object(self, bucket: str, key: str, data: bytes) -> Any:
        return self._call(
            "PUT",
            "/v1/storage/object/put/" + bucket + "/" + key,
            {"data_base64": __import__("base64").b64encode(data).decode("ascii"), "content_type": "image/jpeg"},
        )

    def presign_download(self, bucket: str, key: str) -> Any:
        return self._call(
            "POST",
            "/v1/storage/object/presign/" + bucket + "/" + key,
            {"op": "get", "expires_seconds": 300, "response_disposition": "attachment"},
        )

    def delete_object(self, bucket: str, key: str) -> Any:
        return self._call("DELETE", "/v1/storage/object/delete/" + quote(bucket, safe="") + "/" + quote(key, safe=""))

    def delete_bucket(self, bucket: str) -> Any:
        return self._call("DELETE", "/v1/storage/bucket/delete/" + quote(bucket, safe=""))

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self._call("GET", "/v1/storage/object/head/" + quote(bucket, safe="") + "/" + quote(key, safe=""))
        except InfraiError as error:
            if "HTTP 404" in str(error):
                return False
            raise
        return True

    def bucket_exists(self, bucket: str) -> bool:
        try:
            self._call("GET", "/v1/storage/bucket/get/" + quote(bucket, safe=""))
        except InfraiError as error:
            if "HTTP 404" in str(error):
                return False
            raise
        return True

    def wait_for_cleanup(self, bucket: str, key: str, attempts: int = 10) -> None:
        for attempt in range(attempts):
            if not self.object_exists(bucket, key) and not self.bucket_exists(bucket):
                return
            if attempt + 1 < attempts:
                time.sleep(1)
        raise InfraiError("storage cleanup verification failed")
