import numpy as np
from numpy.ctypeslib import ndpointer
import ctypes as ct
import _ctypes
import platform
import os
import ctypes
from _ctypes import POINTER
from ctypes import c_int, c_double, c_char, c_char_p, c_long, c_longlong, c_bool, Structure
from contextlib import contextmanager
import tempfile
try:
    from ctypes import windll
except ImportError:
    pass
import sys
from pathlib import Path
import atexit

c_int_p = POINTER(ctypes.c_long)
c_long_p = POINTER(ctypes.c_longlong)
c_double_p = POINTER(ctypes.c_double)
c_float_p = POINTER(ctypes.c_float)
c_bool_p = POINTER(ctypes.c_bool)


# Add support for complex numbers to ctypes.
# This solution is copied from: https://stackoverflow.com/a/65743183/3676517
class c_double_complex(Structure):
    """complex is a c structure
    https://docs.python.org/3/library/ctypes.html#module-ctypes suggests
    to use ctypes.Structure to pass structures (and, therefore, complex)
    """

    _fields_ = [("real", c_double), ("imag", c_double)]

    @property
    def value(self):
        return self.real + 1j * self.imag  # fields declared above


c_double_complex_p = POINTER(c_double_complex)

in_use = []


class SuppressStream(object):

    def __init__(self, suppressed_output_file, stream=sys.stderr):
        self.orig_stream_fileno = stream.fileno()
        self.stream = stream
        self.suppressed_output_file = suppressed_output_file

    def __enter__(self):
        # save stream file descriptor
        self.orig_stream_dup = os.dup(self.orig_stream_fileno)
        self.stream.flush()
        os.dup2(self.suppressed_output_file.fileno(), self.orig_stream_fileno)

    def __exit__(self, type, value, traceback):
        os.dup2(self.orig_stream_dup, self.orig_stream_fileno)
        os.close(self.orig_stream_dup)


def suppress_output(f):
    def wrap(*args, **kwargs):
        if 'verbose' not in kwargs or not kwargs.pop('verbose'):
            with SuppressStream(sys.stdout), SuppressStream(sys.stderr):
                f(*args, **kwargs)
        else:
            f(*args, **kwargs)
    return wrap


@contextmanager
def chdir(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def cwd(f):
    def wrap(self, *args, **kwargs):
        with chdir(self.model_path):
            f(self, *args, **kwargs)
    return wrap


def wrap(self, f, *args, check_stop=True, **kwargs):
    c_args = []
    args = list(args)
    for i, arg in enumerate(args):
        if isinstance(arg, (list, tuple)):
            if all([isinstance(e, int) for e in arg]):
                # default to int64 which is default on linux but not windows
                args[i] = np.array(arg, dtype=np.int64)
            else:
                args[i] = np.array(arg)
        if isinstance(args[i], np.ndarray):

            if self.fortran:
                if not args[i].flags.f_contiguous:
                    sys.stderr.write(f'argument {i} for {f.__name__} not f_contiguous\n')
            else:
                if not args[i].flags.c_contiguous:
                    sys.stderr.write(f'argument {i} for {f.__name__} not c_contiguous\n')

            args[i] = np.require(args[i], requirements=['C', 'F'][self.fortran])

    for arg in args:
        if isinstance(arg, bool):
            c_args.append(c_bool_p(c_bool(arg)))
        elif isinstance(arg, int):
            c_args.append(c_long_p(c_longlong(arg)))
        elif isinstance(arg, float):
            c_args.append(c_double_p(c_double(arg)))
        elif isinstance(arg, str):
            c_args.append(c_char_p(arg.encode('cp1252')))
            # c_args.append(c_int_p(c_int(len(arg))))

        elif isinstance(arg, np.ndarray):
            if arg.dtype in [np.int32]:
                c_args.append(arg.ctypes.data_as(c_int_p))
            elif arg.dtype in [np.int64]:
                c_args.append(arg.ctypes.data_as(c_long_p))
            elif arg.dtype == np.float64:
                c_args.append(arg.ctypes.data_as(c_double_p))
            elif arg.dtype == np.float32:
                c_args.append(arg.ctypes.data_as(c_float_p))
            elif arg.dtype == np.complex128:
                c_args.append(arg.ctypes.data_as(c_double_complex_p))
            else:
                raise NotImplementedError(arg.dtype)

        else:
            # raise NotImplementedError(arg.__class__.__name__)
            c_args.append(arg)
    if 'restype' in kwargs:
        restype = kwargs['restype']
        if hasattr(restype, 'dtype'):
            restype = np.ctypeslib.as_ctypes_type(restype)
        f.restype = restype
    with chdir(self.cwd):
        if self.suppress_output:
            with SuppressStream(self.suppressed_output_file, sys.stdout), SuppressStream(self.suppressed_output_file, sys.stderr):
                res = f(*c_args)
        else:
            res = f(*c_args)
    try:
        self.check_stop()
    except BaseException:
        if check_stop:
            raise

    ret_args = []
    for arg in args:
        c_arg = c_args.pop(0)
        if isinstance(arg, (int, float, bool)):
            ret_args.append(c_arg.contents.value)
        elif isinstance(arg, (str)):
            ret_args.append(c_arg.value.decode('cp1252'))
            # c_args.pop(0)
        else:
            ret_args.append(arg)
    return ret_args, res


class DLLWrapper(object):
    def __init__(self, filename, cwd='.', cdecl=True, fortran=True):
        self.filename = str(filename)
        if os.path.abspath(self.filename) in in_use:
            raise Exception(f'{os.path.abspath(self.filename)} already in use in current process.')
        self.cwd = cwd
        self.cdecl = cdecl
        self.fortran = fortran
        self.suppress_output = False
        self.suppressed_output_file = tempfile.TemporaryFile('w')
        self.open()
        in_use.append(os.path.abspath(self.filename))
        atexit.register(self.close)

    def check_stop(self):
        stop_code = 0
        cstop_code = c_long_p(c_longlong(stop_code))
        getattr(self.lib, 'get_stop_code')(cstop_code)
        if cstop_code.contents.value:
            stop_msg = (" " * 1024).encode('cp1252')
            cstop_msg = c_char_p(stop_msg)
            getattr(self.lib, 'get_stop_message')(cstop_msg)
            stop_msg = cstop_msg.value.decode('cp1252').strip()
            getattr(self.lib, 'reset_stop_code_and_message')()
            raise Exception(stop_msg)

    @staticmethod
    def find_dll(path, name):
        p = Path(path)

#         if sys.platform == "win32":
#             prefixes = ['']
#             if sys.maxsize > 2**32:
#                 suffixes = ['.dll', '_64.dll']
#             else:
#                 suffixes = ['.dll']
#         elif sys.platform == 'linux':
#             prefixes = ['lib','']
#             suffixes = ['.so']
#         else:
#             raise NotImplementedError()

        dll_lst = []
        file_patterns = ['*%s*.dll' % name, '*%s*.so' % name]
        for fp in file_patterns:
            dll_lst.extend(list(p.glob("**/" + fp)))

        def use_first(dll_lst):
            f = str(dll_lst[0])
            print("Using ", os.path.abspath(f))
            return DLLWrapper(f)

        if len(dll_lst) == 1:
            return use_first(dll_lst)
        elif len(dll_lst) > 1:
            # check if excluding dlls in hawc2-binary, i.e. "hawc2-<platform>" results in one dll
            dll_lst2 = [d for d in dll_lst if not str(d).startswith('hawc2-')]
            if len(dll_lst2) == 1:
                return use_first(dll_lst2)
            raise FileExistsError("Multiple dlls found:\n" + "\n".join([str(p) for p in dll_lst]))
        else:
            raise FileNotFoundError("No " + " or ".join(file_patterns) +
                                    " files found in " + os.path.abspath(p.absolute()))

    def open(self):
        assert os.path.isfile(self.filename), os.path.abspath(self.filename)
        if self.cdecl:
            try:
                # python < (3, 8) and > 3.10?:
                self.lib = ct.CDLL(self.filename)
            except BaseException:
                self.lib = ct.CDLL(self.filename, winmode=ctypes.DEFAULT_MODE)
        else:
            self.lib = windll.LoadLibrary(self.filename)

    def close(self):
        if "FreeLibrary" in dir(_ctypes):
            _ctypes.FreeLibrary(self.lib._handle)
        else:
            _ctypes.dlclose(self.lib._handle)
        del self.lib
        self.suppressed_output_file.close()
        atexit.unregister(self.close)
        in_use.remove(os.path.abspath(self.filename))

#     def __enter__(self):
#         self.open()
#         return self
#
#     def __exit__(self, type, value, traceback):
#         self.close()
#         return False

    def __getattr__(self, name):
        if name == 'lib':
            raise Exception("DLL not loaded. Run using: 'with dll: ...'")
        return self.get_lib_function(name)

    def get_lib_function(self, name):
        try:
            f = getattr(self.lib, name)
        except AttributeError as e:
            raise AttributeError("Attribute '%s' not found in dll ('%s')" % (name, self.filename))
        return lambda *args, **kwargs: wrap(self, f, *args, **kwargs)

    def version(self, function_name='get_version'):
        try:
            f = getattr(self.lib, function_name)
            f.argtypes = [c_char_p, c_long]
            s = "".ljust(255)
            arg = c_char_p(s.encode('utf-8'))
            f(arg, len(s))
            return arg.value.decode().strip()
        except AttributeError:
            if function_name == 'get_version':
                return self.version('version')

    def getFileProperties(self):
        if sys.platform != "win32":
            raise OSError("Only supported for Windows")
        import win32api
        fname = self.filename

        # ==============================================================================
        """
        Read all properties of the given file return them as a dictionary.
        """
        propNames = ('Comments', 'InternalName', 'ProductName',
                     'CompanyName', 'LegalCopyright', 'ProductVersion',
                     'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                     'FileVersion', 'OriginalFilename', 'SpecialBuild')

        props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

        try:
            # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
            fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
            props['FixedFileInfo'] = fixedInfo
            props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                                                    fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                                                    fixedInfo['FileVersionLS'] % 65536)

            # \VarFileInfo\Translation returns list of available (language, codepage)
            # pairs that can be used to retreive string info. We are using only the first pair.
            lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

            # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
            # two are language/codepage pair returned from above

            strInfo = {}
            for propName in propNames:
                strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
                # print str_info
                strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

            props['StringFileInfo'] = strInfo
        except BaseException:
            pass

        return props


class Type2DllWrapper(DLLWrapper):
    def __init__(self, filename, dll_subroutine_init, dll_subroutine_update,
                 arraysizes_init, arraysizes_update,
                 init_array):
        super().__init__(filename)
        self.dll_subroutine_init = dll_subroutine_init
        self.dll_subroutine_update = dll_subroutine_update
        self.arraysizes_init = arraysizes_init
        self.arraysizes_update = arraysizes_update
        self.init_array = init_array

    def open(self):
        DLLWrapper.open(self)
        self.init()

    def call(self, name, array, n1, n2):
        f = getattr(self.lib, name)
        f.argtypes = [ndpointer(shape=n1, dtype=ct.c_double, flags='FORTRAN'),
                      ndpointer(shape=n2, dtype=ct.c_double, flags='FORTRAN')]
        f.restype = None

        pad_array = np.zeros(n1)
        pad_array[:len(array)] = array
        arg1 = np.array(pad_array, dtype=ct.c_double, order='F')
        arg2 = np.zeros(n2, dtype=ct.c_double, order='F')

        f(arg1, arg2)
        return arg2

    def init(self):
        n1, n2 = self.arraysizes_init
        return self.call(self.dll_subroutine_init, self.init_array, n1, n2)

    def update(self, array):
        n1, n2 = self.arraysizes_update
        return self.call(self.dll_subroutine_update, array, n1, n2)
