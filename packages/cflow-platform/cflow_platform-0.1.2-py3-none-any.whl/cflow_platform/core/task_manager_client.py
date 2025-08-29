from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx


class TaskManagerClient:
    """Package-native HTTP client for ChromaDB-backed tasks.

    Decouples the package from the monorepo TaskManager.
    """

    def __init__(self, base_urls: Optional[List[str]] = None, collection: str = "cerebral_tasks"):
        self.base_urls = base_urls or [
            "http://localhost:8000",
            "http://host.docker.internal:8000",
        ]
        self.collection = collection
        self._active: Optional[str] = None

    async def _endpoint(self) -> Optional[str]:
        if self._active:
            return self._active
        for url in self.base_urls:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(f"{url}/health")
                    if r.status_code == 200:
                        self._active = url
                        return url
            except Exception:
                continue
        return None

    async def list_by_status(self, status: str) -> List[Dict[str, Any]]:
        ep = await self._endpoint()
        if not ep:
            return []
        payload = {"where": {"status": status}, "include": ["documents", "metadatas"]}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{ep}/get/{self.collection}", json=payload)
        if r.status_code != 200:
            return []
        data = r.json()
        items: List[Dict[str, Any]] = []
        metas = data.get("metadatas") or []
        for m in metas:
            if m:
                items.append(m)
        return items

    async def add(self, title: str, description: str, priority: str = "medium") -> Optional[str]:
        ep = await self._endpoint()
        if not ep:
            return None
        task_id = f"T{int(datetime.now().timestamp())}"
        meta = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "status": "pending",
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        payload = {"documents": [f"{title} {description}"], "metadatas": [meta], "ids": [task_id]}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{ep}/add/{self.collection}", json=payload)
        return task_id if r.status_code == 200 else None


