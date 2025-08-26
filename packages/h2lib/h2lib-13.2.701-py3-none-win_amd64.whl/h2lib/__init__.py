import sys
import os
from ._h2lib import H2Lib, MultiH2Lib
from ._version import __version__, h2lib_version, hawc2_version
# try:
# from ._version import __version__
# if __version__ == 'unknown':
#     f = os.path.abspath(os.path.dirname(__file__) + '/../../update_version.py')
#     if os.path.isfile(f):
#         os.system(f'{sys.executable} {f}')
#     import importlib
#     importlib.reload(_version)
#     from ._version import __version__, h2lib_version, hawc2_version
# except BaseException:
#     pass
