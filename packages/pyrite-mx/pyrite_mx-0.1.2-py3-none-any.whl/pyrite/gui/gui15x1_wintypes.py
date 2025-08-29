from .gui12x0_wintypes import *
from . import gui13x0_winapi as winapi

class PropertyStore:
    stock_properties_catalog = PropertyStock.catalog
    def __init__(self, target=None):
        self.target = ctypes.POINTER(IPropertyStore)()
        self.invoke = None
    def __del__(self):
        if self.target and self.invoke:
            self.invoke.Release(self.target)  
    def set_value(self, prop, value, options=None):
        prop_key = PROPERTYKEY()
        prop_variant = PROPVARIANT()
        prop_key.fmtid, prop_key.pid, py_type, prop_variant.vt = self.stock_properties_catalog[prop]
        if value is not None:
            match(prop_variant.vt):
                case PROPVARIANT.VT_LPWSTR:
                    prop_variant.vVal.pwszVal = str(value)
                case PROPVARIANT.VT_BOOL:
                    prop_variant.vVal.boolVal = wintraits.TRUE if bool(value) else wintraits.FALSE 
                case _:
                    raise Exception('ERROR')
        else:
            prop_variant.vt = PROPVARIANT.VT_EMPTY
        result = self.invoke.SetValue(self.target,prop_key, prop_variant)
        if result != 0:
            raise Exception('ERROR')
    def get_value(self,prop, options=None):
        prop_key = PROPERTYKEY()
        prop_variant = PROPVARIANT()
        prop_key.fmtid, prop_key.pid, py_type, var_type = self.stock_properties_catalog[prop]
        result = self.invoke.GetValue(self.target,prop_key, prop_variant)
        if result != 0:
            raise Exception('ERROR')
        match(prop_variant.vt):
            case PROPVARIANT.VT_LPWSTR:
                value = str(prop_variant.vVal.pwszVal)
            case PROPVARIANT.VT_BOOL:
                value = True if prop_variant.vVal.boolVal != 0 else False
            case PROPVARIANT.VT_EMPTY:
                value = None
            case _:
                raise Exception('ERROR')
        return value
    def commit(self):
        result = self.invoke.Commit(self.target)
        return True if result == 0 else False
    def bind(self, target=None):
        if self.target != target:
            if self.target:
                if self.invoke:
                    self.invoke.Release(self.target)
                    self.invoke = None
            self.target = target
        if self.target:
            if not self.invoke:
                self.invoke = target.contents.lpVtbl.contents
        return self
    def __len__(self):
        length = ctypes.c_ulong()
        result = self.invoke.GetCount(self.target,ctypes.byref(length))
        if result != 0:
            raise Exception('ERROR')
        return int(length)
    def __getitem__(self, key):
        return self.get_value(key)
    def __setitem__(self, key, value):
        return self.set_value(key,value)

    def com_iid(self):
        return IPropertyStore.IID_IPropertyStore
    def com_ptr(self):
        return self.target
    
    @staticmethod
    def from_hwnd(hwnd):
        ps = PropertyStore()
        result = winapi.SHGetPropertyStoreForWindow(int(hwnd), ps.com_iid(), ps.com_ptr())
        if result != 0:
            return None
        return ps.bind(ps.com_ptr())

