import sys

from .about import __version__  # noqa

if sys.platform == "win32":
    from .windows import *  # noqa
    from .win_trayicon import *  # noqa
elif sys.platform == "linux":
    from .linux import *  # noqa
elif sys.platform == "darwin":
    from .linux import *  # noqa
from .base import *  # noqa
from .time_utils import *  # noqa
