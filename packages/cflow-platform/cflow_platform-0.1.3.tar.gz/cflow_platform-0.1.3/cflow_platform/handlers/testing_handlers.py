from __future__ import annotations

from typing import Any, Dict


class TestingHandlers:
    async def handle_test_analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "analysis": {"tests": 0, "confidence": 1.0}}

    async def handle_test_delete_flaky(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "deleted": 0}

    async def handle_test_confidence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "confidence": {"score": 1.0}}


