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

from collections import defaultdict


def group_by_line(history):
    """Group a history list by line.

    Parameters
    ----------
    history : list of Output
        Each call to write, in the order it occurred.

    Returns
    -------
    history_by_line : defaultdict mapping int to list of str
        Dict which contains all of the outputs from a given line.
    """
    history_by_line = defaultdict(list)
    for output in history:
        history_by_line[output.caller_line].append(output.value)
    return history_by_line


def format_output(lines):
    """Format 0 or more lines of text.

    Parameters
    ----------
    lines : list of str
        The line(s) to format. The output depends on the length of this list:
        * 0: empty string.
        * 1: '# ' is prepended to the one line.
        * >=2: the text is captured in a triple-quoted string.

    Returns
    -------
    text : str
        The formatted text.
    """
    full_text = ''.join(lines)
    full_text_lines = full_text.splitlines()
    if len(full_text_lines) == 0:
        return ''
    elif len(full_text_lines) == 1:
        return '# ' + full_text
    else:
        return '"""\n' + full_text + '"""\n'


def annotate_program(program, stdout_history, stderr_history):
    """Create a new version of a program with stdout and stderr notated after
    each line.

    Parameters
    ----------
    program : str
        The program, as it was executed.
    stdout_history : list of Output
        Each call to stdout.write, in the order it occurred.
    stderr_history : list of Output
        Each call to stderr.write, in the order it occurred.

    Returns
    -------
    annotated_program : str
        The program with output annotations added.
    """
    stdout_history_by_line = group_by_line(stdout_history)
    stderr_history_by_line = group_by_line(stderr_history)

    annotated_program = ''
    for i_line, line in enumerate(program.splitlines()):
        annotated_program += line
        annotated_program += '\n'
        annotated_program += format_output(stderr_history_by_line[i_line + 1])
        annotated_program += format_output(stdout_history_by_line[i_line + 1])

    return annotated_program
