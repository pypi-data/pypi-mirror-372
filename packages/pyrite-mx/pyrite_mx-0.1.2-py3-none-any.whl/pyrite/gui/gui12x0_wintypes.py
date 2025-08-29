from ctypes.wintypes import *
import ctypes
from sortedcontainers import SortedDict
from . import gui11x0_wintraits as wintraits
#from . import gui13x0_winapi as winapi

class STARTUPINFOEX(ctypes.Structure):
    _fields_ = [  ('cb', DWORD) ,
                    ('lpReserved', LPSTR),  
                    ('lpDesktop', LPSTR),
                    ('lpTitle', LPSTR),
                    ('dwX', DWORD),
                    ('dwy', DWORD),
                    ('dwXSize', DWORD),
                    ('dwYSize', DWORD),
                    ('dwXCountChars', DWORD),
                    ('dwYCountChars', DWORD),
                    ('dwFillAttribute', DWORD),
                    ('dwFlags', DWORD),
                    ('wShowWindow', WORD),
                    ('cbReserved2', WORD),
                    ('lpReserved2', LPBYTE),
                    ('hStdInput', HANDLE),
                    ('hStdOutput', HANDLE),
                    ('hStdError', HANDLE),
                    ('lpAttributeList', ctypes.POINTER(ctypes.c_void_p)) ]

class PROCESS_INFORMATION (ctypes.Structure):
    _fields_ = [('hProcess', HANDLE),
                    ('hThread', HANDLE),
                    ('dwProcessId',DWORD),
                    ('dwThreadId',DWORD)]

GUID = ctypes.c_ubyte * 16

class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID),
                ("pid", DWORD)]

VARIANT_BOOL = USHORT
class VARIANT_VALUE(ctypes.Union):
    _fields_ = [("boolVal", VARIANT_BOOL), 
                ("pwszVal", LPWSTR)]

class PROPVARIANT(ctypes.Structure):
    VT_EMPTY	        = 0
    VT_NULL     	    = 1
    VT_I2	            = 2
    VT_I4	            = 3
    VT_R4	            = 4
    VT_R8	            = 5
    VT_CY	            = 6
    VT_DATE	            = 7
    VT_BSTR	            = 8
    VT_DISPATCH	        = 9
    VT_ERROR	        = 10
    VT_BOOL	            = 11
    VT_VARIANT	        = 12
    VT_UNKNOWN	        = 13
    VT_DECIMAL	        = 14
    VT_I1	            = 16
    VT_UI1	            = 17
    VT_UI2	            = 18
    VT_UI4	            = 19
    VT_I8	            = 20
    VT_UI8	            = 21
    VT_INT	            = 22
    VT_UINT	            = 23
    VT_VOID	            = 24
    VT_HRESULT	        = 25
    VT_PTR	            = 26
    VT_SAFEARRAY	    = 27
    VT_CARRAY	        = 28
    VT_USERDEFINED	    = 29
    VT_LPSTR	        = 30
    VT_LPWSTR	        = 31
    VT_RECORD	        = 36
    VT_INT_PTR	        = 37
    VT_UINT_PTR	        = 38
    VT_FILETIME	        = 64
    VT_BLOB	            = 65
    VT_STREAM	        = 66
    VT_STORAGE	        = 67
    VT_STREAMED_OBJECT	= 68
    VT_STORED_OBJECT	= 69
    VT_BLOB_OBJECT	    = 70
    VT_CF	            = 71
    VT_CLSID	        = 72
    VT_VERSIONED_STREAM	= 73
    VT_BSTR_BLOB	    = 0xfff
    VT_VECTOR	        = 0x1000
    VT_ARRAY	        = 0x2000
    VT_BYREF	        = 0x4000
    VT_RESERVED	        = 0x8000
    VT_ILLEGAL	        = 0xffff
    VT_ILLEGALMASKED	= 0xfff
    VT_TYPEMASK	        = 0xfff

    _fields_ = [("vt", USHORT),
                ("wReserved1", USHORT),
                ("wReserved2", USHORT),
                ("wReserved3", USHORT),
                ("vVal", VARIANT_VALUE)]

class IPropertyStoreVtbl(ctypes.Structure):
    _fields_ = [
        ('QueryInterface', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))),
        ('AddRef', ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)),
        ('Release', ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)),
        ('GetCount', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))),
        ('GetAt', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(PROPERTYKEY))),
        ('GetValue', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(PROPERTYKEY), ctypes.POINTER(PROPVARIANT))),
        ('SetValue', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(PROPERTYKEY), ctypes.POINTER(PROPVARIANT))),
        ('Commit', ctypes.CFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p))
    ]

class IPropertyStore(ctypes.Structure):
    # {886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}
    IID_IPropertyStore = (GUID)(*bytearray.fromhex("eb8e6d88f28c46448d02cdba1dbdcf99"))
    _fields_ = [('lpVtbl', ctypes.POINTER(IPropertyStoreVtbl))]

class PropertyStock:
    # {9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}
    PKEY_AppUserModel = (GUID)(*bytearray.fromhex("55284c9f799f394ba8d0e1d42de1d5f3"))
    catalog = SortedDict(
        {
            wintraits.System.AppUserModel.ID: (PKEY_AppUserModel, 5, str, PROPVARIANT.VT_LPWSTR),
            wintraits.System.AppUserModel.RelaunchCommand: (PKEY_AppUserModel, 2, str, PROPVARIANT.VT_LPWSTR),
            wintraits.System.AppUserModel.RelaunchDisplayNameResource: (PKEY_AppUserModel, 4, str, PROPVARIANT.VT_LPWSTR),
            wintraits.System.AppUserModel.RelaunchIconResource: (PKEY_AppUserModel, 3, str, PROPVARIANT.VT_LPWSTR),
            wintraits.System.AppUserModel.PreventPinning: (PKEY_AppUserModel, 9, bool, PROPVARIANT.VT_BOOL)
        }
    )

LRESULT = ctypes.c_long
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, HWND, UINT, WPARAM, LPARAM)