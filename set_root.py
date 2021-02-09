import sys
import os


def set_root():
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    os.chdir(project_root)
