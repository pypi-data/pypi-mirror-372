import sys
import os
from importlib.resources import files

# Ensure project root is in sys.path for development
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def get_ui_path(filename):
    """Return the absolute path to a .ui file in the ui package."""
    ui_dir = files('ui')
    ui_file = ui_dir.joinpath(filename)
    return str(ui_file)
