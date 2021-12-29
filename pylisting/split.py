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

import re


def split_by_cell(program, cell_regex=r'^# In\[[0-9]+\]:$'):
    """Split a given program (such as exported from a Jupyter notebook) into
    separate cells.

    Parameters
    ----------
    program : str
        The program to split.
    cell_regex : str, optional
        The regex to match cell boundaries. Default is consistent with the
        cell markers used in files which are exported from Jupyter notebooks.

    Returns
    -------
    program_split : list of str
        The text from each cell of the program.
    """
    cell_regex = re.compile(cell_regex)

    program_split = ['']
    for line in program.splitlines():
        match = cell_regex.search(line)
        if match:
            program_split.append('')

        program_split[-1] += line + '\n'

    return program_split
