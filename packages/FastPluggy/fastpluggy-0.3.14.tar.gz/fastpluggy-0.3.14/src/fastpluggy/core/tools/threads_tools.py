import threading

from loguru import logger


def get_tid():
    """Get the current thread's OS-level thread ID (TID)."""

    thread_info = threading.current_thread()
    logger.info(f"thread_info: {thread_info} ")

    if hasattr(threading, "get_native_id"):
        return threading.get_native_id()


def get_py_ident():
    """Get the current python ident of thread."""

    if hasattr(threading, "get_ident"):
        return threading.get_ident()


def is_thread_alive(native_id):
    for thread in threading.enumerate():
        if thread.native_id == native_id:
            return thread.is_alive()
    return False


def is_thread_alive_by_ident(ident):
    for thread in threading.enumerate():
        if thread.ident == ident:
            return thread.is_alive()
    return False
