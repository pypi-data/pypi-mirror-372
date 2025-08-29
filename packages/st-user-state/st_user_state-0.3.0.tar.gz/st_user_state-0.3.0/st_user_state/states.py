import threading
from typing import Protocol, cast

from .session_state import SessionState


class _StatesHolder(Protocol):
    _states: dict[str, SessionState]
    _state_lock: threading.Lock


class _MainThread(_StatesHolder, threading.Thread):
    pass


def _init_main_thread() -> None:
    thread = _main_thread()
    if not hasattr(thread, "_states"):
        thread._states = {}
        thread._state_lock = threading.Lock()


def _get_state(ident: str) -> SessionState:
    if state := get_states().get(ident):
        return state

    state = SessionState(ident)
    get_states().update({ident: state})

    return state


def _main_thread() -> _MainThread:
    return cast(_MainThread, threading.main_thread())


def _state_lock() -> threading.Lock:
    return _main_thread()._state_lock


def fresh_state(ident: str) -> SessionState:
    """
    Creates a fresh state for the given identifier, deleting any old.

    Args:
        ident (str): The identifier for the state.

    Returns:
        SessionState: The newly created state.
    """
    if ident in get_states():
        old = get_states()[ident]
        old.__del__()

    return _get_state(ident)


def get_states() -> dict[str, SessionState]:
    """
    Returns the dictionary of session states.

    Returns:
        dict[str, SessionState]: A dictionary containing the session states.
    """
    return _main_thread()._states


def set_states(states: dict[str, SessionState]):
    """
    Sets the state to the given dictionary of SessionState objects.

    Args:
        states (dict[str, SessionState]):
            A dictionary mapping state names to SessionState objects.

    Returns:
        None
    """
    with _state_lock():
        _main_thread()._states = states


def set_state(ident: str, state: SessionState) -> None:
    """
    Safely set or overwrite a state.

    Args:
        ident (str): The identifier for the state.
        state (SessionState): The state to be set.

    Returns:
        None
    """
    get_states().update({ident: state})


def drop_state(ident: str) -> None:
    """
    Safely drop an active state.

    Args:
        ident (str): The identifier of the state to be dropped.

    Raises:
        ValueError: If the given identifier is not found in the active states.

    """
    if ident in get_states():
        with _state_lock():
            get_states().pop(ident)
    else:
        raise ValueError("Unknown ident")
