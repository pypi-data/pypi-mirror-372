import os
import sys

# add the current file directory so that python finds tentris_sys.*.so
cur_file_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(cur_file_dir)

from .http_store import *

from .native_bindings import *
from .version import __version__
