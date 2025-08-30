"""
This module provides functionality to create Abaqus sensitivity files by replacing parameter fields
in an Abaqus template file and generating Python code blocks for parameterized studies.

Features
--------
 - The `AbaqusPy` class automates the process of reading a template, replacing parameter fields,
   generating Python function files for embedded code blocks, and producing final sensitivity files.
 - Designed for use in finite element sensitivity studies and parameter sweeps with Abaqus .inp
   files.
 - All file operations are performed with robust encoding and modular methods for each step.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

"""

import re
from importlib import import_module

class AbaqusPy:
    """
    Class to create sensitivity files by replacing parameter fields in a template file.

    Parameters
    ----------
    template_filename : str
        The base name of the Abaqus template file (without .inp extension).
    sensitivity_filename : str
        The base name for the output sensitivity files.
    param_dict : dict
        Dictionary mapping parameter names to lists of values.
    isens : int
        Index of the sensitivity case to use from param_dict values.
    """

    def __init__(self, *, template_filename, sensitivity_filename, param_dict, isens):
        """
        Initialize the AbaqusPy object.
        """
        self.template_filename = template_filename
        self.sensitivity_filename = sensitivity_filename
        self.param_dict = param_dict
        self.isens = isens
        self.lines = []
        self.replaced_lines = None

    def _read_template(self):
        """
        Read the template .inp file and store its lines in self.lines.

        Returns
        -------
        None
        """
        with open(f'{self.template_filename}.inp', 'r', encoding='utf-8') as file_old:
            self.lines = file_old.readlines()

    def _replace_parameters(self):
        """
        Replace parameter fields in the template lines using param_dict and isens.

        Returns
        -------
        None

        Notes
        -----
        The replaced lines are stored in self.replaced_lines.
        """
        def replacer(match):
            return str(self.param_dict[match.group(0)][self.isens])
        pattern = re.compile('|'.join(re.escape(k) for k in self.param_dict.keys()))
        self.replaced_lines = [pattern.sub(replacer, line) for line in self.lines]

    def _create_function_file(self):
        """
        Create a Python file with functions extracted from the replaced template lines.

        Each function corresponds to a Python code block in the template.

        Returns
        -------
        None
        """
        counter = 0
        py_bool = False
        with open(f'{self.sensitivity_filename}_functions.py', 'w', encoding='utf-8') as func_file:
            for line in self.replaced_lines:
                if r"**\start_python_global" in line:
                    py_bool = True
                    continue
                if r"**\end_python_global" in line:
                    py_bool = False
                    continue
                if r"**\start_python" in line:
                    func_file.write(f'def function_{counter}():\n')
                    py_bool = True
                    counter += 1
                    continue
                if r"**\end_python" in line:
                    py_bool = False
                    continue
                if py_bool:
                    line = re.sub(r'^(\s*)writeLine\s*\+=\s*', r'\1yield ', line)
                    func_file.write(line)

    def _create_sensitivity_file(self):
        """
        Create the final sensitivity .inp file by combining replaced template lines and
        executing generated Python functions for code blocks.

        Returns
        -------
        None
        """
        counter = 0
        py_bool = True
        func_module = import_module(f'{self.sensitivity_filename}_functions')
        with open(f'{self.sensitivity_filename}.inp', 'w', encoding='utf-8') as sens_file:
            for line in self.replaced_lines:
                if r"**\start_python_global" in line:
                    py_bool = False
                    continue
                if r"**\end_python_global" in line:
                    py_bool = True
                    continue
                if r"**\start_python" in line:
                    py_bool = False
                    func = getattr(func_module, f'function_{counter}')
                    for line_part in func():
                        sens_file.write(line_part)
                    counter += 1
                    continue
                if r"**\end_python" in line:
                    py_bool = True
                    continue
                if py_bool:
                    sens_file.write(line)

    def run(self):
        """
        Run the full process: read template, replace parameters, create function file,
        and create the final sensitivity file.

        Returns
        -------
        None
        """
        self._read_template()
        self._replace_parameters()
        self._create_function_file()
        self._create_sensitivity_file()
