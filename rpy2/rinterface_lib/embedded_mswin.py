import sys
import typing
from rpy2.rinterface_lib import embedded
from rpy2.rinterface_lib import callbacks
from rpy2.rinterface_lib import openrlib

ffi = openrlib.ffi

# These constants are default values from R sources
_DEFAULT_VSIZE = 67108864  # vector heap size
_DEFAULT_NSIZE = 350000  # language heap size
_DEFAULT_MAX_VSIZE = sys.maxsize  # max vector heap size
_DEFAULT_MAX_NSIZE = 50000000  # max language heap size
_DEFAULT_PPSIZE = 50000  # stack size
_DEFAULT_C_STACK_LIMIT = -1


def _initr_win32(
        interactive: bool = True,
        _want_setcallbacks: bool = True,
        _c_stack_limit: int = _DEFAULT_C_STACK_LIMIT

) -> typing.Optional[int]:
    with openrlib.rlock:
        if embedded.isinitialized():
            return None

        options_c = [ffi.new('char[]', o.encode('ASCII'))
                     for o in embedded._options]
        n_options = len(options_c)
        n_options_c = ffi.cast('int', n_options)
        status = openrlib.rlib.Rf_initEmbeddedR(n_options_c, options_c)
        embedded.setinitialized()

        embedded.rstart = ffi.new('Rstart')
        rstart = embedded.rstart
        rstart.rhome = openrlib.rlib.get_R_HOME()
        rstart.home = openrlib.rlib.getRUser()
        rstart.CharacterMode = openrlib.rlib.LinkDLL
        if _want_setcallbacks:
            rstart.ReadConsole = callbacks._consoleread
            rstart.WriteConsoleEx = callbacks._consolewrite_ex
            rstart.CallBack = callbacks._callback
            rstart.ShowMessage = callbacks._showmessage
            rstart.YesNoCancel = callbacks._yesnocancel
            rstart.Busy = callbacks._busy

        rstart.R_Quiet = True
        rstart.R_Interactive = interactive
        rstart.RestoreAction = openrlib.rlib.SA_RESTORE
        rstart.SaveAction = openrlib.rlib.SA_NOSAVE

        rstart.vsize = ffi.cast('size_t', _DEFAULT_VSIZE)
        rstart.nsize = ffi.cast('size_t', _DEFAULT_NSIZE)
        rstart.max_vsize = ffi.cast('size_t', _DEFAULT_MAX_VSIZE)
        rstart.max_nsize = ffi.cast('size_t', _DEFAULT_MAX_NSIZE)
        rstart.ppsize = ffi.cast('size_t', _DEFAULT_PPSIZE)

        openrlib.rlib.R_SetParams(rstart)

        # TODO: still needed ?
        openrlib.rlib.R_CStackLimit = ffi.cast('uintptr_t', _c_stack_limit)

        return status
