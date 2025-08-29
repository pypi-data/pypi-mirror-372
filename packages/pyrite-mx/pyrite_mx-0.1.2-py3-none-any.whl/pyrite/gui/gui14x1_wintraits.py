from .gui11x0_wintraits import *
from . import gui12x0_wintypes as wintypes
import ctypes
__PROC_THREAD_ATTRIBUTE_PARENT_PROCESS = 0x00020000
PROC_THREAD_ATTRIBUTE_PARENT_PROCESS = ctypes.cast(__PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,ctypes.POINTER(wintypes.DWORD))