'''
Module containing code meant to deal with logging of
third party tools
'''
import os
import sys
import time
import threading
from io                    import StringIO
from contextlib            import contextmanager
from dmu.logging.log_store import LogStore

log = LogStore.add_logger('dmu:logging:messages')
# --------------------------------
class FilteredStderr:
    '''
    This class is meant to be used to filter the messages
    in the error stream by substrings
    '''
    # --------------------------------
    def __init__(
            self,
            banned_substrings : list[str],
            capture_stream    : StringIO):
        '''
        Parameters
        -------------
        banned_substrings : List of substrings that, if found in error message, will drop error
        capture_stream    : Used to store error stream filtered messages, expected to be sys.__stderr__
        '''
        self._banned         = banned_substrings
        self._capture_stream = capture_stream
    # --------------------------------
    def write(self, message : str):
        '''
        Should allow filtering error messages
        '''
        if not any(bad in message for bad in self._banned):
            # This will make it to the error messages
            self._capture_stream.write(message)
    # --------------------------------
    def flush(self):
        '''
        Should override the error stream's flush method
        '''
        self._capture_stream.flush()
# --------------------------------
@contextmanager
def filter_stderr(
        banned_substrings : list[str],
        capture_stream    : StringIO|None=None):
    '''
    This contextmanager will suppress error messages

    Parameters
    -----------------
    banned_substrings : List of substrings that need to be found in error messages
                        in order for them to be suppressed
    capture_stream    : Buffer needed to run tests, not needed for normal use
    '''
    if capture_stream is None:
        capture_stream = sys.__stderr__

    read_fd, write_fd = os.pipe()
    saved_fd          = os.dup(2)

    os.dup2(write_fd, 2)
    os.close(write_fd)

    filtered        = FilteredStderr(banned_substrings, capture_stream)
    reader_finished = threading.Event()

    def reader():
        try:
            with os.fdopen(read_fd, 'r', buffering=1) as pipe:
                while True:
                    line = pipe.readline()
                    if not line:
                        break
                    filtered.write(line)
                filtered.flush()
        finally:
            reader_finished.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    try:
        yield
    finally:
        os.dup2(saved_fd, 2)
        os.close(saved_fd)

        time.sleep(0.1)
        reader_finished.wait(timeout=1.0)
# --------------------------------
