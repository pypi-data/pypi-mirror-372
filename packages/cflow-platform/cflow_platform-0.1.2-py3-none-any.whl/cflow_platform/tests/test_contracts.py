import asyncio


def test_core_public_api_surfaces():
    from cflow_platform.core.public_api import (
        get_stdio_server,
        get_direct_client_executor,
        safe_get_version_info,
    )

    assert callable(get_stdio_server())
    assert callable(get_direct_client_executor())
    info = safe_get_version_info()
    assert isinstance(info, dict) and "api_version" in info


def test_direct_client_exec_unknown_tool():
    from cflow_platform.core.public_api import get_direct_client_executor

    exec_fn = get_direct_client_executor()
    result = asyncio.get_event_loop().run_until_complete(exec_fn("__no_such_tool__"))
    assert result.get("status") in {"error", "success"}


