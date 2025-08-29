#import win32api, win32con, win32gui, win32process, win32ui
from . import gui11x0_wintraits as wintraits
from . import gui12x0_wintypes as wintypes

from win32api import GetMonitorInfo, MonitorFromWindow, MonitorFromRect, \
                        EnumDisplayMonitors, GetAsyncKeyState, \
                        WinExec, CloseHandle, OpenProcess, RGB, \
                        GetCurrentThreadId
from win32gui import GetWindowLong, SetWindowLong, GetForegroundWindow, \
                        GetWindowText, GetClassName, GetClassLong, IsIconic, IsWindowVisible, IsWindow, \
                        EnumWindows, EnumChildWindows, GetWindowRect, GetParent, ShowWindow, MoveWindow, \
                        GetWindow, SetFocus, GetFocus, \
                        PostMessage, PostQuitMessage, SendMessage, GetIconInfo, GetObject, SetWindowPos, \
                        RegisterHotKey, SetWindowLong, GetWindowLong, GetActiveWindow,\
                        SetParent, SetLayeredWindowAttributes, \
                        GetForegroundWindow, SetForegroundWindow,\
                        GetActiveWindow, SetActiveWindow, \
                        SetCapture, GetCapture
from win32ui import CreateBitmapFromHandle
from win32process import GetWindowThreadProcessId, GetCurrentProcessId, AttachThreadInput

import ctypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
dwmapi = ctypes.windll.dwmapi
shell32 = ctypes.windll.shell32
ole32 = ctypes.windll.ole32

__CoInitialize = ole32.CoInitialize
__CoInitialize.restype = ctypes.HRESULT
__CoInitialize.argtypes = [ctypes.c_void_p]
def CoInitialize(arg=None):
    __CoInitialize(wintraits.NULL)
CoUninitialize = ole32.CoUninitialize
CoUninitialize.restype = None
CoUninitialize.argtypes = None

SHGetPropertyStoreForWindow = shell32.SHGetPropertyStoreForWindow
SHGetPropertyStoreForWindow.restype = ctypes.HRESULT
SHGetPropertyStoreForWindow.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.GUID), ctypes.POINTER(ctypes.POINTER(wintypes.IPropertyStore))]

__GetDpiForWindow = user32.GetDpiForWindow
__GetClassLongPtr = user32.GetClassLongPtrA
__SetProcessDpiAwarenessContext = user32.SetProcessDpiAwarenessContext


def GetDpiForWindow(hwnd):
    return __GetDpiForWindow(hwnd)

def GetClassLongPtr(hwnd, index):
    return __GetClassLongPtr(hwnd, ctypes.c_int(index))

def SetProcessDpiAwarenessContext(index):
    return __SetProcessDpiAwarenessContext(wintypes.HANDLE(index))


# Define constants
__DWM_EC_DISABLECOMPOSITION = 0
__DWM_EC_ENABLECOMPOSITION = 1
# Define the attribute you want to get
__DWMWA_EXTENDED_FRAME_BOUNDS = 9

# Define the DwmGetWindowAttribute function
__DwmGetWindowAttribute = dwmapi.DwmGetWindowAttribute
__DwmGetWindowAttribute.argtypes = [wintypes.HWND, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
__DwmGetWindowAttribute.restype = ctypes.HRESULT

def DwmGetWindowExtendedFrameBounds(hwnd):
    rect = wintypes.RECT()
    rect_ptr = ctypes.pointer(rect)
    void_ptr = ctypes.cast( rect_ptr, ctypes.POINTER(ctypes.c_void_p) )
    result = __DwmGetWindowAttribute(hwnd, __DWMWA_EXTENDED_FRAME_BOUNDS, void_ptr, ctypes.sizeof(rect))
    if result != 0:
        raise ctypes.WinError(result)
    return rect.left, rect.top, rect.right, rect.bottom

CreateProcess = kernel32.CreateProcessW
CreateProcess.argtypes = [
    wintypes.LPCWSTR,                               # lpApplicationName,
    wintypes.LPWSTR,                                # lpCommandLine,
    ctypes.POINTER(ctypes.c_void_p),                # lpProcessAttributes
    ctypes.POINTER(ctypes.c_void_p),                # lpThreadAttributes
    wintypes.BOOL,                                  # bInheritHandles
    wintypes.DWORD,                                 # dwCreationFlags
    ctypes.POINTER(ctypes.c_void_p),                # lpEnvironment
    wintypes.LPCWSTR,                               # lpCurrentDirectory
    ctypes.POINTER(wintypes.STARTUPINFOEX),         # lpStartupInfo
    ctypes.POINTER(wintypes.PROCESS_INFORMATION)    # lpProcessInformation
]
CreateProcess.restype = wintypes.BOOL

GetShellWindow = user32.GetShellWindow
GetShellWindow.argtypes = []
GetShellWindow.restype = wintypes.HWND

# Define the function prototype
InitializeProcThreadAttributeList = kernel32.InitializeProcThreadAttributeList
InitializeProcThreadAttributeList.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # lpAttributeList
    wintypes.DWORD,                   # dwAttributeCount
    wintypes.DWORD,                   # dwFlags
    ctypes.POINTER(ctypes.c_size_t)   # lpSize
]
InitializeProcThreadAttributeList.restype = wintypes.BOOL

UpdateProcThreadAttribute = kernel32.UpdateProcThreadAttribute
UpdateProcThreadAttribute.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),    # lpAttributeList
    wintypes.DWORD,                     # dwFlags
    ctypes.POINTER(wintypes.DWORD),     # Attribute
    ctypes.POINTER(ctypes.c_void_p),    # lpValue
    ctypes.c_size_t,                    # cbSize
    ctypes.POINTER(ctypes.c_void_p),    # lpPreviousValue
    ctypes.POINTER(ctypes.c_size_t)     # lpReturnSize
]
UpdateProcThreadAttribute.restype = wintypes.BOOL

GetLastError = kernel32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = wintypes.DWORD


SetCurrentProcessExplicitAppUserModelID = shell32.SetCurrentProcessExplicitAppUserModelID
SetCurrentProcessExplicitAppUserModelID.argtypes = [wintypes.LPCWSTR]
SetCurrentProcessExplicitAppUserModelID.restype = wintypes.HANDLE


GetConsoleWindow = kernel32.GetConsoleWindow
GetConsoleWindow.argtypes = []
GetConsoleWindow.restype = wintypes.HWND


# Define SetWindowLongPtrW
# example usage of GWL_WNDPROC: SetWindowLongPtr(hwnd, GWL_WNDPROC, ctypes.cast(wnd_proc_callback, ctypes.c_void_p))
SetWindowLongPtr = user32.SetWindowLongPtrW
SetWindowLongPtr.argtypes = [wintypes.HWND, wintypes.INT, ctypes.c_void_p]
SetWindowLongPtr.restype = ctypes.c_void_p

# Define GetWindowLongPtrW
GetWindowLongPtr = user32.GetWindowLongPtrW
GetWindowLongPtr.argtypes = [wintypes.HWND, wintypes.INT]
GetWindowLongPtr.restype = ctypes.c_void_p

# Define CallWindowProcW
CallWindowProc = user32.CallWindowProcW
CallWindowProc.argtypes = [
    ctypes.c_void_p,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
CallWindowProc.restype = ctypes.c_long


SetConsoleMode = kernel32.SetConsoleMode
SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
SetConsoleMode.restype = wintypes.BOOL
GetConsoleMode = kernel32.GetConsoleMode
GetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
GetConsoleMode.restype = wintypes.BOOL

GetStdHandle = kernel32.GetStdHandle
GetStdHandle.argtypes = [wintypes.DWORD]
GetStdHandle.restype = wintypes.HANDLE
SetStdHandle = kernel32.SetStdHandle
SetStdHandle.argtypes = [wintypes.DWORD, wintypes.HANDLE]
SetStdHandle.restype = wintypes.BOOL
