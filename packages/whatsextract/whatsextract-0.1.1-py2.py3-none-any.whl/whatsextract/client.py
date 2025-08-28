from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Any
import asyncio
import json
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


@dataclass
class ExtractionResult:
    email: Optional[str]
    phone: Optional[str]
    name: Optional[str]
    company: Optional[str]
    requirement: Optional[str]
    budget: Optional[str]
    confidence: float
    processing_time_ms: int


class WhatsExtract:
    """
    WhatsExtract API Client for Python.

    Example:
        client = WhatsExtract("we_dev_local_1234567890", base_url="http://localhost:8080")
        r = client.extract("Contact john@example.com +1 415 555 0000")
        print(r.email, r.phone)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8080",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        if not isinstance(api_key, str) or len(api_key) < 8:
            raise ValueError("Invalid API key")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "DELETE"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, json_body: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self._session.request(
            method, url, headers=self._headers, json=json_body, timeout=self.timeout
        )
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            raise RuntimeError(f"WhatsExtract error {resp.status_code}: {detail}")
        try:
            return resp.json()
        except Exception:
            return {}

    def extract(self, message: str, mode: str = "lite") -> ExtractionResult:
        t0 = time.perf_counter()
        data = self._request("POST", "/v2/extract", {"message": message, "mode": mode})
        dt = int((time.perf_counter() - t0) * 1000)
        return ExtractionResult(
            email=data.get("email"),
            phone=data.get("phone"),
            name=data.get("name"),
            company=data.get("company"),
            requirement=data.get("requirement"),
            budget=data.get("budget"),
            confidence=float(data.get("confidence", 0.0)),
            processing_time_ms=dt,
        )

    async def extract_async(self, message: str, mode: str = "lite") -> ExtractionResult:
        if aiohttp is None:  # pragma: no cover
            # fallback to sync in thread
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.extract, message, mode)

        t0 = time.perf_counter()
        url = f"{self.base_url}/v2/extract"
        headers = self._headers.copy()
        payload = {"message": message, "mode": mode}
        # simple retry with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as sess:
                    async with sess.post(url, headers=headers, json=payload) as r:
                        if r.status >= 400:
                            txt = await r.text()
                            raise RuntimeError(f"WhatsExtract error {r.status}: {txt}")
                        data = await r.json()
                        dt = int((time.perf_counter() - t0) * 1000)
                        return ExtractionResult(
                            email=data.get("email"),
                            phone=data.get("phone"),
                            name=data.get("name"),
                            company=data.get("company"),
                            requirement=data.get("requirement"),
                            budget=data.get("budget"),
                            confidence=float(data.get("confidence", 0.0)),
                            processing_time_ms=dt,
                        )
            except Exception:
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(min(2 ** attempt, 8))

        raise RuntimeError("unreachable")

    def batch_extract(
        self,
        messages: List[str],
        mode: str = "lite",
        chunk_size: int = 100,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        webhook_url: Optional[str] = None,
    ) -> List[ExtractionResult]:
        if not messages:
            return []
        results: List[ExtractionResult] = []
        total = len(messages)
        for i in range(0, total, chunk_size):
            chunk = messages[i : i + chunk_size]
            resp = self._request(
                "POST",
                "/v2/batch",
                {"messages": chunk, "mode": mode, "skip_errors": True, "webhook_url": webhook_url},
            )
            # Sort and map back to ExtractionResult
            for item in sorted(resp.get("results", []), key=lambda x: x["index"]):
                d = item.get("data") or {}
                results.append(
                    ExtractionResult(
                        email=d.get("email"),
                        phone=d.get("phone"),
                        name=d.get("name"),
                        company=d.get("company"),
                        requirement=d.get("requirement"),
                        budget=d.get("budget"),
                        confidence=float(d.get("confidence", 0.0)) if d else 0.0,
                        processing_time_ms=resp.get("processing_time_ms", 0),
                    )
                )
            if progress_callback:
                progress_callback(min(i + chunk_size, total), total)
        return results

    def extract_from_dataframe(
        self,
        df,  # type: ignore
        column: str,
        add_columns: bool = True,
    ):
        if pd is None:
            raise RuntimeError("pandas not installed. `pip install pandas`")
        if column not in df.columns:
            raise KeyError(f"column '{column}' not in DataFrame")
        emails: List[Optional[str]] = []
        phones: List[Optional[str]] = []
        confs: List[float] = []

        for text in df[column].astype(str).tolist():
            r = self.extract(text)
            emails.append(r.email)
            phones.append(r.phone)
            confs.append(r.confidence)

        if add_columns:
            df = df.copy()
            df["email"] = emails
            df["phone"] = phones
            df["confidence"] = confs
        return df

    def configure_webhook(self, webhook_url: str, events: List[str]) -> Dict[str, Any]:
        return self._request(
            "POST", "/v2/webhooks", {"webhook_url": webhook_url, "events": events, "active": True}
        )

    def get_usage(self) -> Dict[str, Any]:
        return self._request("GET", "/v2/usage")

    @staticmethod
    def validate_message(base_url: str, message: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{base_url}/v2/validate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"message": message}),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
