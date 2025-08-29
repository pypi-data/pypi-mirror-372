from . import gui16x1_winapi as winapi
from . import gui15x1_wintypes as wintypes
from . import gui14x1_wintraits as wintraits
from typing import Tuple
from sortedcontainers import SortedSet
import re
import os
import psutil
from PIL import Image, ImageTk, ImageGrab, ImageChops
import PIL.ImageDraw
import PIL
import xml.etree.ElementTree as ET
import ctypes
import time

def hmon_list_monitors(options=None):
    monitor_list = []
    for index, (hmon, hdc, (l, t, r, b)) in enumerate(winapi.EnumDisplayMonitors(),1):
        if options is not None:
            monitor_list.append((hmon, hdc, (l, t, r, b)))
        else:
            monitor_list.append(hmon)
    return monitor_list

def hmon_from_monitor_number(monitor_number):
    mon_list = hmon_list_monitors()
    if monitor_number<1 or monitor_number>len(mon_list):
        return None
    return mon_list[monitor_number-1]

def hmon_from_hwnd(hwnd):
    return winapi.MonitorFromWindow(hwnd, wintraits.MONITOR_DEFAULTTONEAREST)

# ltrb stands for left-top-right-bottom
def hmon_from_rect_ltbr(ltrb_tuple):
    return winapi.MonitorFromRect(ltrb_tuple, wintraits.MONITOR_DEFAULTTONEAREST)

def hwnd_restore(hwnd):
    try:
        cpid = winapi.GetCurrentProcessId()
        fghwnd = winapi.GetForegroundWindow()
        fgtid, fgpid = winapi.GetWindowThreadProcessId(fghwnd)
        tid, pid = winapi.GetWindowThreadProcessId(hwnd)
        if pid==cpid and fgpid==cpid:
            #print('hwnd_window_show: trying internally...')
            if winapi.IsIconic(hwnd):
                winapi.ShowWindow(hwnd, wintraits.SW_RESTORE)
            winapi.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            if winapi.SetForegroundWindow(hwnd) == hwnd:
                return
    except Exception as e:
        print('exception in hwnd_window_show:', e)
    
    try:
        #print('hwnd_window_show: trying with external process...')
        winapi.WinExec(fr'C:\1\X\tools\windows-spread-switcher\build\windows-spread-switcher.exe {hwnd} show')
        return
    except Exception as e:
        print('exception in hwnd_window_show:', e)


def hwnd_minimize(hwnd):
    #print(f'hwnd_minimize {hwnd}')
    try:
        cpid = winapi.GetCurrentProcessId()
        tid, pid = winapi.GetWindowThreadProcessId(hwnd)
        if pid==cpid:
            #print('hwnd_minimize: trying internally...')
            if winapi.IsIconic(hwnd):
                winapi.ShowWindow(hwnd,wintraits.SW_RESTORE)
            else:
                winapi.ShowWindow(hwnd,wintraits.SW_SHOWMINIMIZED)
            return
    except Exception as e:
        print('exception in hwnd_window_show:', e)

    try:
        #print('hwnd_minimize: trying with external process...')
        winapi.WinExec(fr'C:\1\X\tools\windows-spread-switcher\build\windows-spread-switcher.exe {hwnd} minimize')
        return
    except Exception as e:
        print('exception in hwnd_minimize:', e)

def hwnd_close(hwnd):
    #print(f'hwnd_close {hwnd}')
    try:
        winapi.PostMessage(hwnd,wintraits.WM_CLOSE,0,0);
    except Exception as e:
        print('exception in hwnd_window_show:', e)

def hwnd_move(hwnd, x, y, w, h, repaint):
    #print('hwnd_move_window')
    #return win32gui.SetWindowPos(hwnd,win32con.NULL,x,y,w,h,win32con.SWP_ASYNCWINDOWPOS) #win32con.SWP_NOACTIVATE|win32con.SWP_NOZORDER|(win32con.SWP_NOREDRAW if not repaint else 0))
    winapi.MoveWindow(hwnd,x,y,w,h,repaint)

def hwnd_zorder(hwnd):
    z_order = -1
    hwnd2 = hwnd
    while hwnd2 != wintraits.NULL:        
        hwnd2 = winapi.GetWindow(hwnd2, wintraits.GW_HWNDPREV)
        z_order += 1
    return z_order

#@warnings.deprecated('deprecata perchè fuorviante. usare hwnd_toplevel_from_tk_window o hwnd_toplevel_from_tk_widget')
def hwnd_from_tk_window(tk_wwindow):
    hwnd = tk_wwindow.winfo_id()
    hwnd_parent = hwnd
    while hwnd_parent != wintraits.NULL:
        hwnd = hwnd_parent
        hwnd_parent = winapi.GetParent(hwnd)
    return hwnd

def hwnd_toplevel_from_tk_window(tk_window):
    hwnd = tk_window.winfo_id()
    hwnd_parent = hwnd
    while hwnd_parent != wintraits.NULL:
        hwnd = hwnd_parent
        hwnd_parent = winapi.GetParent(hwnd)
    return hwnd

def hwnd_toplevel_from_tk_widget(tk_widget):
    hwnd = tk_widget.winfo_id()
    hwnd_parent = hwnd
    while hwnd_parent != wintraits.NULL:
        hwnd = hwnd_parent
        hwnd_parent = winapi.GetParent(hwnd)
    return hwnd

def hwnd_list_child_windows(hwnd):
    @staticmethod
    def win32_window_load_children_cb(hwnd_child, w_set):
        w_set.append(hwnd_child)
    w_set = []
    winapi.EnumChildWindows(hwnd, win32_window_load_children_cb, w_set)
    return w_set

def hwnd_grab_icon(hwnd, tpid:Tuple[int, int]=None):
        try:
            wt = winapi.GetWindowText(hwnd)
            if wt == 'Settings':
                pass
            if tpid is None:
                tid, pid = winapi.GetWindowThreadProcessId(hwnd)
            else:
                tid, pid = tpid
            
            #if wt == 'Settings':
            #    win32_get_gui_thread_info non serve ad un mazza
            #    Window.win32_get_gui_thread_info(tid)
            p = psutil.Process(pid)
            if p.name()=='ApplicationFrameHost.exe':
                try:
                    # questo sotto tenta di recuperare il processo hostato dentro ApplicationFrameHost
                    # però funziona solo se la finestra è visibile
                    cwl = hwnd_list_child_windows(hwnd)             
                    for cw in cwl:
                        ctid, cpid = winapi.GetWindowThreadProcessId(cw)
                        if cpid != pid:
                            p = psutil.Process(cpid)
                            break
                except Exception as e:
                    print('Exception ', e)
            try:
                cp_dir = os.path.split(p.exe())[0]
                appx_manifest_fn = os.path.join(cp_dir, 'AppxManifest.xml')
                for i in range(1,3):
                    if os.path.exists(appx_manifest_fn):
                        break
                    cp_dir = os.path.split(cp_dir)[0]
                    appx_manifest_fn = os.path.join(cp_dir, 'AppxManifest.xml')
                if os.path.exists(appx_manifest_fn):
                    tree = ET.parse(appx_manifest_fn)
                    root = tree.getroot()
                    ns = {"win10":"http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
                    # pathToLogo = manifest.Root.Element(XName.Get("Properties", ns)).Element(XName.Get("Logo", ns)).Value;
                    properties = root.find('win10:Properties', namespaces=ns)
                    logo = properties.find("win10:Logo", namespaces=ns)
                    #print(logo.text)
                    logo_fn = os.path.join(cp_dir,logo.text)
                    #print(logo_fn, os.path.exists(logo_fn))
                    fdn = os.path.split(logo_fn)
                    fne = os.path.splitext(fdn[1])
                    spec = f'{fdn[0]}\\{fne[0]}*{fne[1]}'
                    ls = os.listdir(fdn[0])
                    lx = SortedSet()
                    for ff in ls:
                        if re.match(fr'{fne[0]}.*\{fne[1]}',ff):
                            lx.add(ff)
                    if logo_fn not in lx:
                        index = lx.bisect_right(f'{fdn[1]}.scale-')
                        if index>=len(lx):
                            return None
                        logo_fn = lx[index]

                    #print(f'{p.name()} [{wt}] [{logo_fn}]')
                    logo_final_fn = os.path.join(fdn[0],logo_fn)
                    img = PIL.Image.open(logo_final_fn)
                    width, height = img.size
                    if height>24:
                        img = img.resize((width*24//height, 24))
                    image = ImageTk.PhotoImage(img)
                    return image
            except Exception as e:
                print('Exception ', e)
                pass
                

            # hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
            hicon = winapi.SendMessage(hwnd, wintraits.WM_GETICON, 0, 0)
            if hicon:
                #print('icon grabbed by WM_GETICON 0')
                pass
            if not hicon:
                hicon = winapi.SendMessage(hwnd, wintraits.WM_GETICON, 2, 0)
                if hicon:
                    #print('icon grabbed by WM_GETICON 2')
                    pass
            if not hicon:
                hicon = winapi.SendMessage(hwnd, wintraits.WM_GETICON, 1, 0)
                if hicon:
                    #print('icon grabbed by WM_GETICON 1')
                    pass
            if not hicon:
                hicon = winapi.GetClassLongPtr(hwnd, -14)
                if hicon:
                    #print('icon grabbed by GCLP_HICON')
                    pass
            if not hicon:
                hicon = winapi.GetClassLongPtr(hwnd, -34)
                if hicon:
                    #print('icon grabbed by GCLP_HICONSM')
                    pass
            
            if hicon:
                info = winapi.GetIconInfo(hicon)
                try:
                    if info[4]:  # Icon has color plane.
                        hbmp = info[4]
                        bmp = winapi.GetObject(info[4])
                        mode = "RGBA" # "RGBA"
                        width = bmp.bmWidth
                        height = bmp.bmHeight
                    else:  # Icon has no colour plane, image data stored in mask.
                        hbmp = info[3]
                        bmp = winapi.GetObject(hbmp)
                        mode = "1"
                        width = bmp.width
                        height = bmp.height // 2  # A monochrome icon contains image and XOR mask in the hbmMask.
                    b = winapi.CreateBitmapFromHandle(hbmp)
                    bits_string = b.GetBitmapBits(True)
                    img = PIL.Image.frombytes(mode, (width, height), bits_string, "raw", "BGRA")

                    #crop_box = crop_by_background(img,10)
                    #print(f'CROP-BOX: [{crop_box}] [{width}, {height}]')

                    if height>24:
                        img = img.resize((width*24//height, 24))
                    elif height<24:
                        img = img.resize((width*24//height, 24))
                    image = ImageTk.PhotoImage(img)
                    return image
                finally:
                    info[3].close()
                    info[4].close()
            else:
                print(f"Unable to grab icon for hwnd:{hwnd} [{winapi.GetWindowText(hwnd)}]")                
                img = PIL.Image.new(mode="RGB", size=(24, 24), color = (28, 28, 28))
                draw = PIL.ImageDraw.Draw(img)
                draw.ellipse((4, 4, 20, 20), fill = (128, 28, 28), outline =(78, 28, 28), width=2)
                image = ImageTk.PhotoImage(img)
                return image
        except Exception as err:
            print(err, " grabbing icon for ", hwnd, winapi.GetWindowText(hwnd))

def hwnd_dpi_rect_correct( hwnd, r ):
    dpi = winapi.GetDpiForWindow(hwnd)
    winapi.SetProcessDpiAwarenessContext

def process_create_with_desktop_process_privileges(cmdline):
    hwnd = winapi.GetShellWindow()

    # Initialize variables
    lpAttributeList = ctypes.c_void_p(0)
    dwAttributeCount = 1
    dwFlags = 0
    lpSize = ctypes.c_size_t(0)

    # First call to get the required buffer size
    winapi.InitializeProcThreadAttributeList(lpAttributeList, dwAttributeCount, dwFlags, ctypes.byref(lpSize))

    # Allocate buffer
    lpAttributeList = ctypes.cast(ctypes.create_string_buffer(lpSize.value), ctypes.POINTER(ctypes.c_void_p))

    # Second call to actually initialize the attribute list
    result = winapi.InitializeProcThreadAttributeList(lpAttributeList, dwAttributeCount, dwFlags, ctypes.byref(lpSize))
    if result:
        #if not result:
        #    raise ctypes.WinError(winapi.GetLastError())

        tid, pid = winapi.GetWindowThreadProcessId(hwnd)
        hProcess = winapi.OpenProcess(wintraits.PROCESS_CREATE_PROCESS, wintraits.FALSE, pid);   
        phProcess = ctypes.c_void_p(int(hProcess))
        
        result = winapi.UpdateProcThreadAttribute(lpAttributeList, 0, wintraits.PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, ctypes.byref(phProcess), ctypes.sizeof(phProcess), None, None)
        if result:
            siex = wintypes.STARTUPINFOEX()
            siex.cb = ctypes.sizeof(wintypes.STARTUPINFOEX)
            siex.lpAttributeList = lpAttributeList
            

            pi = wintypes.PROCESS_INFORMATION()

            result = winapi.CreateProcess(None, cmdline,  None, None, wintraits.FALSE,
                                    wintraits.CREATE_NEW_CONSOLE | wintraits.EXTENDED_STARTUPINFO_PRESENT, 
                                    None, None, siex, ctypes.byref(pi))
            
            winapi.CloseHandle(pi.hThread)
            winapi.CloseHandle(pi.hProcess)
        winapi.CloseHandle(hProcess)
    return True if result!=wintraits.FALSE else False


def hwnd_system_app_user_model_id_get(hwnd):
    '''
    WARNING: winapi.CoInitialize() is required to be called once per thread before this
    '''
    ps = wintypes.PropertyStore.from_hwnd(hwnd)
    old_value =  ps[wintraits.System.AppUserModel.ID]
    return old_value 

def hwnd_system_app_user_model_id_set(hwnd, new_value):
    '''
    WARNING: winapi.CoInitialize() is required to be called once per thread before this
    '''
    ps = wintypes.PropertyStore.from_hwnd(hwnd)
    old_value =  ps[wintraits.System.AppUserModel.ID]
    ps[wintraits.System.AppUserModel.ID] = new_value
    ps.commit()
    return old_value 


def hwnd_set_layered(hwnd, color_key_rgb_triplet=None, alpha_percent=None):
    l_ex_style = winapi.GetWindowLong(hwnd, wintraits.GWL_EXSTYLE)
    l_ex_style |= wintraits.WS_EX_LAYERED
    winapi.SetWindowLong(hwnd, wintraits.GWL_EXSTYLE, l_ex_style)
    flags = 0
    color_key = 0
    alpha_byte = 0
    if color_key_rgb_triplet is not None:
        r, g, b = color_key_rgb_triplet
        color_key = winapi.RGB(r//256, g//256, b//256)
        flags |= wintraits.LWA_COLORKEY
    if alpha_percent is not None:
        alpha_byte = int(alpha_percent*255)
        flags |= wintraits.LWA_ALPHA
    if flags != 0:
        winapi.SetLayeredWindowAttributes(hwnd, color_key, alpha_byte, flags)

