# Copyright 2021 Mark Chilenski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from contextlib import AbstractContextManager
from dataclasses import dataclass
import inspect
import sys


@dataclass
class Output(object):
    """Object to store traceback information when something is written to,
    e.g., stdout.
    """
    value: str
    caller_filename: str
    caller_line: int


class CallerTargetNotFoundError(Exception):
    """Exception raised when the caller target cannot be found.
    """
    pass


class OutputTracker(object):
    def __init__(self, passthrough=None, caller_target=0):
        """(Read-only) file-like object to keep track of everything written to,
        e.g., stdout. This can optionally be passed through to another object.

        Access the output history in self.history.

        Parameters
        ----------
        passthrough : file-like, optional
            Another file-like object to pass values to. Default is to not pass
            through to anything.
        caller_target : int or str, optional
            The target caller to log. This can be either:
            * An int, in which case this element in the call stack (excepting
                the methods of OutputTracker) is used.
            * A str, in which case inspect.stack() is traversed until a
                filename matching the str is found.
            Default is 0 (use the immediate caller of the write function). If
            the caller target cannot be found, the value will be silently
            dropped.
        """
        self.history = []
        self.passthrough = passthrough
        self.caller_target = caller_target

    def get_caller(self):
        """Get the calling frame's info. If the requested caller target can't
        be matched, a CallerTargetNotFoundError is raised.

        Returns
        -------
        caller : namedtuple
            The info on the calling frame.
        """
        if isinstance(self.caller_target, int):
            try:
                frame = inspect.stack()[self.caller_target + 2].frame
            except IndexError:
                frame = None
        else:
            frame = None
            for entry in inspect.stack():
                if entry.filename == self.caller_target:
                    frame = entry.frame
                    break
        if frame:
            return inspect.getframeinfo(frame)
        else:
            raise CallerTargetNotFoundError('Caller target not found!')

    def write(self, value):
        """Write a string.

        Parameters
        ----------
        value : str
            The value to write.
        """
        try:
            caller = self.get_caller()
            self.history.append(
                Output(
                    value=value,
                    caller_filename=caller.filename,
                    caller_line=caller.lineno
                )
            )
        except CallerTargetNotFoundError:
            pass

        if self.passthrough:
            self.passthrough.write(value)


class CaptureContext(AbstractContextManager):
    def __init__(self, stdout_tracker, stderr_tracker):
        """Context manager to capture history of everything written to stdout
        and stderr. Note that stderr is captured, but exceptions are not
        caught, so this is primarily useful for capturing warning text.

        Parameters
        ----------
        stdout_tracker : OutputTracker
            The OutputTracker to use to capture things written to stdout.
        stderr_tracker : OutputTracker
            The OutputTracker to use to capture things written to stderr.
        """
        self.stdout_tracker = stdout_tracker
        self.stderr_tracker = stderr_tracker

    def __enter__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.stdout_tracker
        sys.stderr = self.stderr_tracker

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


def run_and_capture_output(program):
    """Run the given Python code and capture everything it writes to stdout and
    stderr. Note that stderr is captured, but exceptions are not caught. The
    Python code is run with __name__ = '__main__', so code in a main guard will
    be executed.

    Parameters
    ----------
    program : str
        The program to run.

    Returns
    -------
    stdout_history : list of Output
        Each call to stdout.write, in the order it occurred.
    stderr_history : list of Output
        Each call to stderr.write, in the order it occurred.
    """
    stdout_tracker = OutputTracker(
        passthrough=sys.stdout, caller_target='<string>'
    )
    stderr_tracker = OutputTracker(
        passthrough=sys.stderr, caller_target='<string>'
    )
    with CaptureContext(stdout_tracker, stderr_tracker):
        exec(program, {'__name__': '__main__'})

    return stdout_tracker.history, stderr_tracker.history
