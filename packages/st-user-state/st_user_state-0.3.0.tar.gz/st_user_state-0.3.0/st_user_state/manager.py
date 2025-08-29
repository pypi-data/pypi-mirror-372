import copy
import datetime as dt
import logging
import threading
import time
from functools import partial
from typing import Callable, NoReturn

from .session_state import SessionState
from .states import drop_state, get_states

CHECK_EVERY = 60
MAX_AGE = 60 * 30


def filter_old_states(
    states: dict[str, SessionState],
    max_age: int = MAX_AGE,
    persist_fun: Callable[[SessionState], None] = None,
) -> NoReturn:
    """
    Filter out old states and drop them.

    Args:
        states (dict[str, SessionState]): View on states to filter.
        max_age (int): The maximum age of a state in seconds.
        persist_fun (Callable[[SessionState], None], optional): A function to
            handle states to be killed, e.g., by saving to disk. Recieves a
            deep copy of the state before it is killed. Should not be blocking.
    """
    for key in list(states.keys()):
        age = dt.datetime.now() - get_states()[key].last_access

        logging.debug(f"{key} age: {age.seconds}")

        if age.seconds < max_age:
            continue

        if persist_fun is not None:
            thread = threading.Thread(
                target=persist_fun, args=copy.deepcopy(states[key])
            )
            thread.start()

        logging.info(f"Dropping state state {key}")
        drop_state(key)


def default_clean_up(
    check_every: int = CHECK_EVERY,
    max_age: int = MAX_AGE,
    kill_func: Callable[[dict[str, SessionState]], None] | None = None,
) -> NoReturn:
    """
    Checks states regularly and performs some clean up logic.

    Defaults to killing old states.

    Args:
        check_every (int): The interval (in seconds) at which to perform the
            clean-up check.
        max_age (int): The maximum age (in seconds) of a state before it is
            considered old and eligible for clean-up. Not used when custom
            kill_funcs are set.
        kill_func (Callable[[dict[str, SessionState]], None] | None):
            The function to use for cleaning up the states.
            If None, states older than max_age are killed.

    Returns:
        None

    """
    if kill_func is None:
        kill_func = partial(filter_old_states, max_age=max_age)

    while True:
        time.sleep(check_every)
        logging.debug("Clean-up started.")
        kill_func(get_states())


def default_shut_down(
    persist_fun: Callable[[SessionState], None] = None,
) -> None:
    """
    Loops through and explicitly kills sessions.

    Args:
        persist_fun (Callable[[SessionState], None], optional):
            A function that takes a SessionState object as input and performs
            some action, e.g., persist to disk.

    Returns:
        None

    """
    for key in list(get_states().keys()):
        logging.warning(f"Killing state {key}.")

        if persist_fun is not None:
            persist_fun(get_states()[key])

        drop_state(key)
