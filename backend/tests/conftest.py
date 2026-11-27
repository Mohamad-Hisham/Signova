"""Match the event loop selected by Uvicorn on the current platform."""

from asyncio import new_event_loop


def pytest_asyncio_loop_factories():
    try:
        from uvloop import new_event_loop as uvloop_factory
    except ImportError:
        return {"asyncio": new_event_loop}
    return {"uvloop": uvloop_factory}
