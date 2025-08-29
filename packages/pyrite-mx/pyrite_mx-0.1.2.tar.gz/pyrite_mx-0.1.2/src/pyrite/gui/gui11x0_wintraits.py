#from pywinauto.win32defines import *
from win32con import *

import ctypes

#define DPI_AWARENESS_CONTEXT_UNAWARE              ((DPI_AWARENESS_CONTEXT)-1)
#define DPI_AWARENESS_CONTEXT_SYSTEM_AWARE         ((DPI_AWARENESS_CONTEXT)-2)
#define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE    ((DPI_AWARENESS_CONTEXT)-3)
#define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 ((DPI_AWARENESS_CONTEXT)-4)
#define DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED    ((DPI_AWARENESS_CONTEXT)-5)

DPI_AWARENESS_CONTEXT_UNAWARE = -1
DPI_AWARENESS_CONTEXT_SYSTEM_AWARE = -2
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = -3
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED = -5

EXTENDED_STARTUPINFO_PRESENT = 0x00080000

class System:
    class AppUserModel:
        ID = 'System.AppUserModel.ID'
        RelaunchCommand = 'System.AppUserModel.RelaunchCommand'
        RelaunchIconResource = 'System.AppUserModel.RelaunchIconResource'
        RelaunchDisplayNameResource = 'System.AppUserModel.RelaunchDisplayNameResource'
        PreventPinning = 'System.AppUserModel.PreventPinning'







