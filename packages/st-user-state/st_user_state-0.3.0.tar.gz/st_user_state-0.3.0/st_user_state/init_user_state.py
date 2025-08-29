import atexit
import logging
import threading
from typing import Callable

from .manager import default_clean_up, default_shut_down
from .state_proxy import StateProxyType, get_proxy
from .states import _init_main_thread

STATE_MGR_NAME = "_state_clean_up_daemon"


def init_user_state(
    get_ident: Callable[[], str],
    clean_up: Callable[[], None] | None = None,
    shut_down: Callable[[], None] | None = None,
) -> StateProxyType:
    """
    Initialises the user state.

    The function initialises the storage of session, registers a shutdown
    function to be called at exit (if provided), and starts a new daemon thread
    to clean stale sessions. Finally, it returns a proxy for the user state.

    Args:
        get_ident (Callable[[], str]): A function that returns a unique
            identifier for the user.
        clean_up (Callable[[], None], optional): A function to clean up stale
            sessions. Can be used to save stale sessions to disk.
        shut_down (Callable[[], None], optional): A function to be called at
            program exit for graceful killing of sessions. Can be used to save
            sessions to disk.

    Returns:
        None
    """
    _init_main_thread()

    if clean_up is None:
        clean_up = default_clean_up

    if shut_down is None:
        shut_down = default_shut_down

    atexit.register(shut_down)

    if STATE_MGR_NAME not in [t.name for t in threading.enumerate()]:
        logging.debug("Starting state manager.")
        daemon = threading.Thread(
            target=clean_up, daemon=True, name=STATE_MGR_NAME
        )
        daemon.start()

    return get_proxy(get_ident)
