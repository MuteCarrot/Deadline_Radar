import os
import sys

# Ensure parent directory, current directory, and CWD are all on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
cwd = os.getcwd()

for p in (parent_dir, current_dir, cwd):
    if p and p not in sys.path:
        sys.path.insert(0, p)

from server import app
