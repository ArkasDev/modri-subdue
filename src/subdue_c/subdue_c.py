"""
This is a wrapper script for the Subdue C implementation
https://github.com/gromgull/subdue
"""

import subprocess
import os

subdue_location = "../../lib/subdue_c/bin/subdue.exe"


def run(output_file_path, input_graph_path):
    subprocess.run([subdue_location])


if __name__ == "__main__":
    run("", "")
