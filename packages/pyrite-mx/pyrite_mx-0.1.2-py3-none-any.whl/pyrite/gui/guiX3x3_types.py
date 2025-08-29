from . import winapi
from . import wintraits
from . import wintools
from ..smarts import smartmatch
#from ..pyrite02_tools import smartclass
#from . import tools
import sys
import types
from bitarray import bitarray
import time
import re
import math
import psutil
import win32process
import os
from sortedcontainers import SortedSet, SortedDict
from datetime import datetime

def xprint(*args, **kwargs):
    #print(*args,**kwargs,file=sys.stderr)
    pass

class P:
    def __init__(self,x=None,y=None):
        self.x = x
        self.y = y
    @staticmethod
    def from_tuple(xy):
        x, y = xy
        return P(x,y)
    def as_dict(self):
        return {k:v for k,v in self.__dict__.items() if k in ['x','y']}
    def as_tuple(self):
        return self.x, self.y    
    def moved_by(self,dx,dy):
        return P(self.x+dx,self.y+dy)

    
class R:
    def __init__(self, x=None, y=None, w=None, h=None):
        self.x, self.y, self.w, self.h = x, y, w, h        
    @staticmethod
    def from_tuple_ltrb(ltrb):
        l, t, r, b = ltrb
        return R(l,t,r-l,b-t)
    @staticmethod
    def from_tuple_xywh(xywh):
        return R(*xywh)
    def as_dict(self):
        return {k:v for k,v in self.__dict__.items() if k in ['x','y','w','h']}
    def as_tuple_pp(self):
        return (self.x,self.y),(self.x+self.w, self.y+self.h)
    def as_tuple_ltrb(self):
        return self.x,self.y, self.x+self.w, self.y+self.h
    def as_tuple_p(self, index=0):
        return self.as_tuples(index)
    def as_tuple_xywh(self):
        return self.x, self.y, self.w, self.h
    def as_tuple_wh(self):
        return self.w, self.h

    def as_tk_geometry(self):
        return f"{self.w()}x{self.h()}{self.x():+d}{self.y():+d}"
    
    def intersects_r(self, other):
        l1, t1, r1, b1 = self.as_tuple_ltrb()
        l2, t2, r2, b2 = other.as_tuple_ltrb()
        return True if l1<=r2 and r1>=l2 and t1<=b2 and b1>=t2 else False

    def contains_r(self, other):
        l1, t1, r1, b1 = self.as_tuple_ltrb()
        l2, t2, r2, b2 = other.as_tuple_ltrb()
        return True if l1<=l2 and r1>=r2 and t1<=t2 and b1>=b2 else False

    def contains_p(self, p:P):
        l1, t1, r1, b1 = self.as_tuple_ltrb()
        x, y = p.as_tuple()
        return True if l1<=x and r1>=x and t1<=y and b1>=y else False

    def stretched_by(self, from_left, from_top, from_right, from_bottom):
        l, t, r, b = self.as_tuple_ltrb()
        return R.from_tuple_ltrb(l+from_left,t+from_top,r-from_right,b-from_bottom)

    def moved_by(self, dx, dy):
        return R(self.x+dx, self.y+dy, self.w, self.h)

    def moved_to(self, x, y):
        return R(x, y, self.w, self.h)


class Mh:
    def __init__(self, hmon=None):
        self.hmon = hmon

class Wh:
    def __init__(self, hwnd=None, hosted_hwnd=None):
        self.hwnd = hwnd
        self.hosted_hwnd = hosted_hwnd
    def window_text(self):
        return winapi.GetWindowText(self.hwnd)
    def is_minimized(self):
        return True if winapi.IsIconic(self.hwnd) else False
    def is_maximized(self):
        return True if (winapi.GetWindowLong(self.hwnd,wintraits.GWL_STYLE) & wintraits.WS_MAXIMIZE) != 0 else False
    def is_normal(self):
        return True if (winapi.GetWindowLong(self.hwnd,wintraits.GWL_STYLE) & (wintraits.WS_MAXIMIZE|wintraits.WS_MINIMIZE)) == 0 else False
    def is_visible(self):
        return winapi.IsWindowVisible(self.hwnd)
    def rectangle(self):
        return winapi.GetWindowRect(self.hwnd)

class M(Mh,R):
    def __init__(self, hmon=None, x=None, y=None, w=None, h=None, name=None, number=None):
        Mh.__init__(self,hmon)
        R.__init__(self,x,y,w,h)
        self.name = name
        self.number = number
    def as_tuple(self):
        return (v for k,v in self.__dict__.items() if not k.startswith('_'))
    def as_dict(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}
    
    @staticmethod
    def from_hmon(hmon=None, number=FileNotFoundError):
        imon = winapi.GetMonitorInfo(hmon)
        l,t,r,b = imon['Work']
        return M(hmon, l, t, r-l, b-t, name=imon['Device'], number=number)
    
    @staticmethod
    def list_monitors(options=None):
        return [M.from_hmon(hmon) for hmon in wintools.hmon_list_monitors()]
    
    def fetch(options=None):
        '''
        ricarica i campi della struttura sulla base del monitor reale ammesso che esista
        ancora un monitor identificato con hmon
        '''
        pass

    def rake(options=None):
        '''
        cerca di ritrovare i monitor compatibili con gli attributi e ritorna una lista
        '''
        pass

        
class W(Wh,R):
    def __init__(self, hwnd=None, x=None, y=None, w=None, h=None, title=None
                 , pid=None, tid=None, palias=None, pname=None, pexe=None
                 , dpi=None, icon=None, wndclassname=None, hosted_hwnd=None):
        Wh.__init__(self,hwnd,hosted_hwnd)
        R.__init__(self,x,y,w,h)
        self.title = title
        self.wndclassname = wndclassname
        self.dpi = dpi
        self.pid = pid
        self.tid = tid
        self.pname = pname
        self.pexe = pexe
        self.palias = palias
        self.icon = icon
    def as_tuple(self):
        return (v for k,v in self.__dict__.items() if not k.startswith('_'))
    def as_dict(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}
    @staticmethod
    def from_w(__w__, **kwargs):
        ww = W(**__w__.as_dict())
        ww.__dict__.update(kwargs)
        return ww
    @staticmethod
    def from_tk_window(__w__, **kwargs):
        ww = W(wintools.hwnd_from_tk_window(__w__))
        ww.__dict__.update(kwargs)
        return ww

    
    @staticmethod
    def list_windows(options=None):
        exclude_handles=None, 
        exclude_states=['minimized','maximized','hidden']
        exclude_titles=['']
        limit_monitors=None        
        if options is not None:
            exclude_handles = options.get('exclude_handles',exclude_handles)   
            exclude_states = options.get('exclude_states',exclude_states)   
            exclude_titles = options.get('exclude_titles',exclude_titles)   
            limit_monitors = options.get('limit_monitors',limit_monitors)   
        def get_windows_2():
            all_windows_handle_list = []

            # The callback function that will be called for each HWND
            # all we do is append the wrapped handle
            def enum_window_proc(hwnd, lparam):
                all_windows_handle_list.append(hwnd)
                return True
            
            # loop over all the children (callback called for each)
            winapi.EnumWindows(enum_window_proc, 0)
            all_windows_list = []
            host_windows_set = SortedDict()
            hosted_windows_set = SortedSet()
            orphan_host_windows_set = SortedDict()
            for hwnd in all_windows_handle_list:
                tid, pid = winapi.GetWindowThreadProcessId(hwnd)
                try:
                    p = psutil.Process(pid)
                    if p.name()=='ApplicationFrameHost.exe':
                        try:
                            cwl = wintools.hwnd_list_child_windows(hwnd)             
                            for cw in cwl:
                                ctid, cpid = winapi.GetWindowThreadProcessId(cw)
                                if cpid != pid:
                                    hosted_windows_set.add(cw)
                                    host_windows_set[hwnd] = cw
                                    break
                            else:
                                orphan_host_windows_set[winapi.GetWindowText(hwnd)]=hwnd
                                continue
                        except Exception as e:
                            xprint('Exception in get_windows_2', e)
                    all_windows_list.append((hwnd,tid,pid,p.name())) 
                except Exception as e:
                    xprint("!!! EXCEPTION psutil.Process: ", e)

            monitors_list = M.list_monitors()
            windows_list = []
            for hwnd, tid, pid, pname in all_windows_list:
                #t_text = win32gui.GetWindowText(hwnd)
                #if t_text.find('Hyper')>=0:
                #    pass
                if hwnd in hosted_windows_set:
                    continue
                w_style = winapi.GetWindowLong(hwnd, wintraits.GWL_STYLE)
                if w_style & wintraits.WS_VISIBLE == 0:
                    continue
                w_ex_style = winapi.GetWindowLong(hwnd, wintraits.GWL_EXSTYLE)
                if w_ex_style & wintraits.WS_EX_NOACTIVATE != 0:
                    continue
                class_name = winapi.GetClassName(hwnd)
                if class_name in ['Shell_TrayWnd', 'Progman', 'WorkerW']:
                    continue
                text = winapi.GetWindowText(hwnd)
                if len(text.strip())==0:
                    continue
                if text in ['Windows Shell Experience Host', 'Windows Input Experience']:
                    continue
                if (w_style & wintraits.WS_ICONIC) == 0:
                    rect = R.from_tuple_ltrb(winapi.GetWindowRect(hwnd))
                    for monitor in monitors_list:
                        if rect.intersects_r(monitor):
                            break
                    else:
                        continue
                host_hwnd = None
                hosted_hwnd = host_windows_set.get(hwnd,None)
                if hosted_hwnd is None:
                    host_hwnd = orphan_host_windows_set.get(text,None)
                    if host_hwnd is not None:
                        hosted_hwnd = hwnd
                if host_hwnd is None:
                    host_hwnd = hwnd
                windows_list.append(W(hwnd=host_hwnd,tid=tid,pid=pid,pname=pname,hosted_hwnd=hosted_hwnd))
            return windows_list



        xprint(f'list_windows start')
        t0 = time.monotonic()
        w_all = get_windows_2() #get_windows()
        t1 = time.monotonic()
        xprint(f'get_windows end t0={t0} t1={t1} T={t1-t0}')
        w_sel = []
        exclude_visible = False
        exclude_hidden = False
        exclude_minimized = False
        exclude_maximized = False
        exclude_restored = False
        if exclude_states is not None:
            if type(exclude_states) is str:
                exclude_states = [exclude_states]    
            if type(exclude_states) is dict:
                exclude_visible = exclude_states.get('visible', False)    
                exclude_hidden = exclude_states.get('hidden', False)    
                exclude_minimized = exclude_states.get('minimized', False) or exclude_states.get('iconized', False)
                exclude_maximized = exclude_states.get('maximized', False) or exclude_states.get('zoomed', False)
                exclude_restored = exclude_states.get('restored', False) or exclude_states.get('normal', False)
            elif type(exclude_states) is list or type(exclude_states) is tuple:
                exclude_visible = 'visible' in exclude_states
                exclude_hidden = 'hidden' in exclude_states
                exclude_minimized = 'minimized' in exclude_states or 'iconized' in exclude_states
                exclude_maximized = 'maximized' in exclude_states or 'zoomed' in exclude_states
                exclude_restored = 'restored' in exclude_states or 'normal' in exclude_states

        w : W
        for z, w in enumerate(w_all):
            try:
                wt = w.window_text()
                if exclude_handles is not None:
                    if int(w.hwnd) in exclude_handles:
                        xprint(f'{w.hwnd} EXCLUDED BY HANDLE [{wt}]')
                        continue
                if limit_monitors is not None:
                    hmon = winapi.MonitorFromWindow(w.hwnd, wintraits.MONITOR_DEFAULTTONEAREST)
                    if not hmon in limit_monitors:
                        xprint(f'{w.hwnd} EXCLUDED BY MONITOR [{wt}]')
                        continue
                if exclude_titles is not None:
                    xprint(f"*** {[wt.lower()]} --- {exclude_titles}")
                    if wt.lower() in exclude_titles:
                        xprint(f'{w.hwnd} EXCLUDED BY TITLE [{wt}]')
                        continue
                if exclude_minimized and w.is_minimized():
                    xprint(f'{w.hwnd} EXCLUDED BY MINIMIZED [{wt}]')
                    continue
                if exclude_maximized and w.is_maximized():
                    xprint(f'{w.hwnd} EXCLUDED BY MAXIMIZED [{wt}]')
                    continue
                if exclude_restored and w.is_normal():
                    xprint(f'{w.hwnd} EXCLUDED BY RESTORED [{wt}]')
                    continue
                if exclude_visible and w.is_visible():
                    xprint(f'{w.hwnd} EXCLUDED BY VISIBLE [{wt}]')
                    continue
                if exclude_hidden and (not w.is_minimized()) and (not w.is_visible()):
                    xprint(f'{w.hwnd} EXCLUDED BY HIDDEN [{wt}]')
                    continue
                _x,_y,_w,_h = R.from_tuple_ltrb(w.rectangle()).as_tuple_xywh()
                w_sel.append(W.from_w(w,title=wt,x=_x,y=_y,w=_w,h=_h,ztag=f'z{z}'))
            except Exception as e:
                xprint(f'EXCEPTION in list_windows: {e}')

        t2 = time.monotonic()
        xprint(f'update list t1={t1} t2={t2} T={t2-t1}')
        xprint(f'list_windows end')
        return w_sel

    def fetch(self,options=None):
        '''
        ricarica i campi della struttura sulla base della finestra reale ammesso che esista
        ancora una finestra identificata con hwnd
        '''
        if not hasattr(self,'pcmdline'):
            p = psutil.Process(self.pid)
            self.pcmdline=p.cmdline()
            self.pexe = p.exe()
            self.pcwd = p.cwd()
        self.classname = winapi.GetClassName(self.hwnd)   
        self.model = wintools.hwnd_system_app_user_model_id_get(self.hwnd)     
        pass

    @staticmethod
    def rake_windows(options=None, **kwargs):      
        _options = dict(exclude_states=[],exclude_titles=[])
        if options is not None:
            _options = _options.update([v for v in options.get(k,None) 
                                    for k in ('exclude_handles','exclude_states','exclude_titles','limit_monitors') 
                                        if v is not None]) 
        wl = W.list_windows(_options)
        rl = []
        for z, w in enumerate(wl):
            try:
                w.fetch()
                for k,v in [(k,v) for k,v in kwargs.items() if v is not None]:
                    try:
                        vv = getattr(w,k)
                        if type(vv) is list:
                            vv = ' '.join(vv)
                        if not re.match(v,vv):
                            break
                    except Exception as e:
                        xprint(e)
                        break    
                else:
                    #w.ztag = f'z{z}'
                    rl.append(w)    
            except Exception as e:
                pass
            pass
        return rl

        '''
        cerca di ritrovare le finestre compatibili con gli attributi e ritorna una lista
        '''
        pass

    def _ensure_pname(self) -> str: 
        if self.pname is None:
            tid, pid = winapi.GetWindowThreadProcessId(self.hwnd)
            try:
                p = psutil.Process(pid)
                self.pname = p.name()                
            except:
                return '<<UNKNOWN>>'
        return self.pname

    def correct_rect(self, r:R):
        l, t, r, b = r.as_tuple_ltrb()
        if self._ensure_pname().lower() == 'code.exe':
            if winapi.GetDpiForWindow(self.hwnd)==96:
                l-=3
                r+=3
                b+=3            
        else:
            l-=7
            r+=7
            b+=7
        return R.from_tuple_ltrb((l,t,r,b))
    
    def decorrect_rect(self, r:R):
        l, t, r, b = r.as_tuple_ltrb()
        if self._ensure_pname().lower() == 'code.exe':
            if winapi.GetDpiForWindow(self.hwnd)==96:
                l+=3
                r-=3
                b-=3            
        else:
            l+=7
            r-=7
            b-=7
        return R.from_tuple_ltrb((l,t,r,b))
    
    def spread_code_guess(self, pad=None, ratio=None, options=None):
        w = self
        if winapi.IsIconic(w.hwnd) or not winapi.IsWindowVisible(w.hwnd):
            return ''
        if pad is None:
            _pad = 10
        elif type(pad) is str:
            _pad = int(pad)
        m0 = M.from_hmon(winapi.MonitorFromWindow(w.hwnd))            
        wr = w.decorrect_rect(R.from_tuple_ltrb(winapi.GetWindowRect(w.hwnd)))
        result = SpreadCode.guess(m0,_pad,wr,ratio=ratio,options=options)
        return result
    
    def spread(self, scode:str, pad=None):
        if pad is None:
            _pad = 10
        elif type(pad) is str:
            _pad = int(pad)
        w = self
        ratio = None
        if scode is not None:
            m = smartmatch()
            if m(r'^[0-9]{1,2}/[0-9]{1,2}$', scode):
                ratio = scode
                scode = None
        if scode is None:
            scode = self.spread_code_guess(ratio=ratio)
        xprint(f'W.spread spread-code={scode}')
        sc = SpreadCode(scode)
        m0 = None
        if sc.monitor is not None:
            imon = sc.monitor-1
            ml =  wintools.hmon_list_monitors()
            if imon<len(ml):
                m0 = M.from_hmon(ml[imon])
        m1 = M.from_hmon(winapi.MonitorFromWindow(w.hwnd))
        if m0 is None:
            m0 = m1
        wr = sc.spread(m0,_pad)
        _wrs = w.correct_rect(wr)
        winapi.MoveWindow(w.hwnd,*_wrs.as_tuple_xywh(),wintraits.TRUE)        
        if m0.hmon != m1.hmon:
            time.sleep(0.2)
            winapi.MoveWindow(w.hwnd,*_wrs.as_tuple_xywh(),wintraits.TRUE)
        _wrg = winapi.GetWindowRect(w.hwnd)
        _wefb = winapi.DwmGetWindowExtendedFrameBounds(w.hwnd)
        _wdpi = winapi.GetDpiForWindow(w.hwnd)
        return self.hwnd, _wrs, _wrg, _wefb, _wdpi
    
    @staticmethod
    def start(cmdline, spread=None, rake=None, options=None):
        if rake is not None:
            wl = W.rake_windows(**rake)
            if wl:
                for w in wl:
                    wintools.hwnd_restore(w.hwnd)
                    if spread is not None and options is not None and 'spread-alwais' in options:
                        w.spread(spread)
                return
        wlb:list[W] = W.list_windows(options=dict(exclude_states=[]))
        wsb = SortedSet({w.hwnd for w in wlb})
        rematch = smartmatch()
        if os.path.exists(cmdline) or rematch(r' *"? *[a-zA-Z][a-zA-Z_-]+:.*',cmdline):
            os.startfile(cmdline)
        else:
            StartupInfo = win32process.STARTUPINFO()
            StartupInfo.dwFlags = 0 #win32process.STARTF_USESHOWWINDOW
            #StartupInfo.wShowWindow = wintraits.SW_NORMAL
            flags = wintraits.NORMAL_PRIORITY_CLASS | wintraits.DETACHED_PROCESS | wintraits.CREATE_NEW_PROCESS_GROUP
            if options is not None:
                if 'new-console-window' in options:
                    flags = wintraits.NORMAL_PRIORITY_CLASS | wintraits.CREATE_NEW_CONSOLE | wintraits.CREATE_NEW_PROCESS_GROUP
                if 'no-console-window' in options:
                    flags = wintraits.NORMAL_PRIORITY_CLASS | wintraits.CREATE_NO_WINDOW | wintraits.CREATE_NEW_PROCESS_GROUP        
            hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(None, cmdline, None, None, wintraits.FALSE,
                            flags, 
                            None, None, StartupInfo)
            winapi.CloseHandle(hThread)
            winapi.CloseHandle(hProcess)

        '''
        winapi.WinExec(cmdline,wintraits.SW_SHOW)
        '''
        xprint(f'{datetime.now()}w-rake-start')
        wdx = SortedDict()
        for i in range(0,10):
            time.sleep(0.2)
            wla:list[W] = W.list_windows(options=dict(exclude_states=[]))
            for w in wla:
                if w.hwnd not in wsb:
                    if w.hwnd not in wdx:
                        wdx[w.hwnd] = w                        
                        xprint(f'FOUND {w.hwnd} {w.title.encode()} {w.pname.encode()}')
                        wintools.hwnd_restore(w.hwnd)
                        if spread is not None:
                            w.spread(spread)
                            xprint(f'{datetime.now()} w-rake-spreaded to {spread}')                        
                        else:
                            xprint(f'{datetime.now()}w-rake-found')
                        return w
        xprint(f'{datetime.now()}w-rake-end')

    
'''
        _dpi = winapi.GetDpiForWindow(self.hwnd)
        if _dpi == 96:
            l-=7
            r+=7
            b+=7
        return R.from_tuple_ltrb((l,t,r,b))
'''

'''
        if self.pname.lower() == 'code.exe':
            l+=0
            r-=0
            b-=0
        else:
            l-=0
            r+=0
            b+=0
        return R.from_tuple_ltrb((l,t,r,b))
'''        
        


class SpreadCode:
    class __fields__:
        X_DIVS = 'x_divs'
        X_SPAN = 'x_span'
        X_FROM = 'x_from'
        X_AXIS = 'x_axis'
        SEPAR  = 'separ'
        Y_DIVS = 'y_divs'
        Y_SPAN = 'y_span'
        Y_FROM = 'y_from'
        Y_AXIS = 'y_axis'
        MONITOR = 'monitor'
        STRETCHES = 'stretches'

        X_FIELDS = [X_DIVS,X_SPAN,X_FROM,X_AXIS]
        Y_FIELDS = [Y_DIVS,Y_SPAN,Y_FROM,Y_AXIS] 
        FIELDS = [*X_FIELDS,
                  SEPAR,
                    *Y_FIELDS,
                    MONITOR,STRETCHES]
    
    class Stretch:
        def __init__(self, delta:int, sides:str):
            self.delta = delta
            self.sides = sides

    def __init__(self, text:str):
        self.mask : bitarray = None
        self.monitor : int = None
        self.separ : str = None
        self.x_divs : int = None
        self.x_span : int = None
        self.x_from : int = None
        self.x_axis : str = None
        self.y_divs : int = None
        self.y_span : int = None
        self.y_from : int = None
        self.y_axis : str = None
        self.stretches = []
        ms, m3 = self._parse(text)
        if ms is not None:
            self.mask = ms
            self.__dict__.update({k:v for k,v in m3.items() if k!='stretches'})
            for x in m3['stretches']:
                self.stretches.append(SpreadCode.Stretch(**x))

    @staticmethod
    def parse(text):
        return SpreadCode(text)
        
    def _parse(self, text):
        divs_s = lambda scope: fr'(?P<{scope}_divs__s>[0-9])'
        span_s = lambda scope: fr'(?P<{scope}_span__s>[0-9])'
        from_s = lambda scope: fr'(?P<{scope}_from__s>[0-9])'

        divs_l = lambda scope: fr'(?P<{scope}_divs__l>[0-9]+)'    
        span_l = lambda scope: fr'(?P<{scope}_span__l>[0-9]+)'    
        from_l = lambda scope: fr'(?P<{scope}_from__l>[0-9]+)'    
                

        stretch_d = lambda scope: fr'(?P<{scope}_stretch_delta__k>[+-][0-9]+)'
        stretch_s = lambda scope: fr'(?P<{scope}_stretch_sides__s>(?:px)?([xywhltrbXYWH]+)?)'
        stretch = lambda scope: fr'(?:{stretch_d(scope)}{stretch_s(scope)})'

        axis = lambda scope: fr'(?P<{scope}_axis__k>[xy])' 
        separ = lambda scope: fr'(?P<{scope}_separ__k>(?<![xy])[/\\]|[/\\]?)' 
        monitor = lambda scope: fr'(?:\:(?P<{scope}_monitor__k>[0-9]+))'
        part = lambda scope: \
            fr'(?:' \
                fr'{divs_s(scope)}{span_s(scope)}{from_s(scope)}' \
                fr'|' \
                fr'{divs_l(scope)}\.{span_l(scope)}\.{from_l(scope)})' \
            fr'{axis(scope)}?'   
        pattern = lambda scope: fr'^{part(f"{scope}_x")}(?:{separ(scope)}{part(f"{scope}_y")})?' \
            fr'{stretch(f"{scope}_s1")}?{stretch(f"{scope}_s2")}?' \
            fr'{stretch(f"{scope}_s3")}?{stretch(f"{scope}_s4")}?' \
            fr'{stretch(f"{scope}_s5")}?{stretch(f"{scope}_s6")}?' \
            fr'{stretch(f"{scope}_s7")}?{stretch(f"{scope}_s8")}?' \
            fr'{monitor(scope)}?$'  
        parser = re.compile(pattern('p'))
        mx = parser.match(text)
        if not mx:
            return None, None
        m1 = {k:mx.group(i) for k,i in mx.re.groupindex.items()}
        m2 = {k[2:-3]:None for k in m1} | {k[2:-3]:v for k,v in m1.items() if v is not None}
        #x = {'_'.join(reversed(k.split('_'))):v for k,v in m2.items()}
        if  (m2['x_axis'] is None and m2['y_axis'] is None and m2['separ']=='\\') or \
            (m2['x_axis'] == 'y' or m2['y_axis'] == 'x') :
            for k in [kk[2:] for kk in m2 if kk.startswith('x_')]:
                m2[f'x_{k}'], m2[f'y_{k}'] = (m2[f'y_{k}'], m2[f'x_{k}'])        
        m2.update({k:int(v) for k,v in m2.items() if v is not None and k.endswith('_offset_delta')})
        m3 = {k:v for k,v in m2.items() if k[2:11]!='_stretch_' and k[2:10]!='_spread_'} | \
                {'stretches':[{'delta':int(v), 'sides':m2[f'{k[:-6]}_sides']} for k,v in m2.items() if v is not None and k.endswith('_stretch_delta')]}
        m3.update({k:int(v) for k,v in m3.items() if v is not None and k[2:6] in('divs','from','span')})
        if m3['monitor'] is not None:
            m3['monitor'] = int(m3['monitor'])
        #m3 = m2 | {'x_axis':'x', 'y_axis':'y'}
        #mr = {k:m3[k] for k in sorted(m3)} 
        ms = bitarray([1 if v is not None else 0 for v in m3.values()])
        return ms, m3
    def bitmask(self,*keys):
        return bitarray([1 if k in keys else 0 for k in SpreadCode.__fields__.FIELDS]) if keys else self.mask
    
    @staticmethod 
    def spread_path(__lwr,__upr,__divs,__pad):
        _pad = __pad // 2
        _lwr = __lwr+_pad
        _upr = __upr-_pad
        _len = _upr - _lwr
        _slice = _len // __divs
        _extra = _len - (_slice * __divs)
        _cols = [None]*__divs
        i=1
        l = __lwr+_pad
        u = __upr-_pad
        r = u - l
        w = _slice
        e = _extra
        while r > _slice :
            if e > 0:
                c = 1
                e -=2
            else:
                c = 0
            ll = (l+_pad, l+w-_pad)
            uu = (u-w+_pad, u-_pad)
            _cols[i-1] = (*ll, ll[1]-ll[0])
            _cols[-i] = (*uu, uu[1]-uu[0])
            d = w+c
            l += d
            u -= d
            r = u - l 
            i += 1
        if _cols[i-1] is None:
            cc = (l+_pad, u-_pad)
            _cols[i-1] = (*cc, cc[1]-cc[0])
        return _cols

    
    @staticmethod
    def spread_space(__lwr,__upr,__pad,__divs,__span,__from, mode='normal'):
        _divs = __divs if __divs > 0 else 1
        _span = __span if __span > 0 and __span<=_divs else _divs            
        if __from == 0:
            if _divs % 2 == 0:
                if _span % 2 == 0:
                    _from = _divs // 2 - _span // 2
                else:       
                    _divs *= 2
                    _span *= 2
                    _from = _divs // 2 - (_span+1) // 2
            else:
                if _span % 2 == 0:
                    _divs *= 2
                    _span *= 2
                    _from = _divs // 2 - _span // 2 
                else:
                    _divs *= 2
                    _span *= 2
                    _from = _divs // 2 - (_span+1) // 2 
        else:
            _from = __from - 1

        dd = _divs - (_from+_span)
        if dd < 0:
            dd = -dd
            _from -= dd
            if _from < 0:
                dd = -_from
                _from = 0
                _span -= (dd)
        if _divs <= 0:
            _divs = 1 
        if _from < 0 or _from >= _divs:
            _from = 0
        if _span < 1 or _span > _divs:
            _span = _divs
        '''
        _pad = __pad // 2
        _lwr = __lwr+_pad
        _upr = __upr-_pad
        _len = _upr - _lwr
        _slice = _len // _divs
        _extra = _len - (_slice * _divs)
        _cols = [None]*_divs
        i=1
        l = __lwr+_pad
        u = __upr-_pad
        r = u - l
        w = _slice
        e = _extra
        while r > _slice :
            if e > 0:
                c = 1
                e -=2
            else:
                c = 0
            ll = (l+_pad, l+w-_pad)
            uu = (u-w+_pad, u-_pad)
            _cols[i-1] = (*ll, ll[1]-ll[0])
            _cols[-i] = (*uu, uu[1]-uu[0])
            d = w+c
            l += d
            u -= d
            r = u - l 
            i += 1
        if _cols[i-1] is None:
            cc = (l+_pad, u-_pad)
            _cols[i-1] = (*cc, cc[1]-cc[0])
        '''
        _cols = SpreadCode.spread_path(__lwr,__upr,_divs,__pad)
        lll = []
        cc = __lwr
        for ll, uu, xx in _cols:
            lll.append(ll-cc)
            cc = uu
        lll.append(__upr-cc)
        _cols.append(('*', *lll))
        if mode=='mirror':
            _from = _divs - _from - _span
        _res = (_cols[_from][0], _cols[_from+_span-1][1]) 
        xprint(f'spread_space({__lwr},{__upr},{__pad},{__divs},{__span},{__from}): [{_cols}] -> {_res}')
        return _res

    def spread(self, ws_rect:R, pad: int=10) -> R:
        wsl,wst,wsr,wsb = ws_rect.as_tuple_ltrb()
        rsl, rst, rsr, rsb = (wsl,wst,wsr,wsb)        
        rsm : bitarray = self.bitmask() 
        xm : bitarray = self.bitmask(*SpreadCode.__fields__.X_FIELDS) 
        ym : bitarray = self.bitmask(*SpreadCode.__fields__.Y_FIELDS) 

        x_from, x_span, x_divs = self.x_from, self.x_span, self.x_divs
        y_from, y_span, y_divs = self.y_from, self.y_span, self.y_divs
        for s in self.stretches:
            ss = s.sides
            dd = s.delta
            if ss.startswith('px'):
                ss = ss[2:]
            if ss!='':
                for c in ss:
                    if c=='X':
                        x_from += dd
                    elif c=='Y':
                        y_from += dd
                    elif c=='W':
                        x_span += dd
                    elif c=='H':
                        y_span += dd

        if (rsm & xm).count(1):         
            rsl, rsr = SpreadCode.spread_space(rsl, rsr, pad, x_divs, x_span, x_from)   
        else:
            rsl, rsr = (rsl+pad, rsr-pad)
        if (rsm & ym).count(1):            
            rst, rsb = SpreadCode.spread_space(rst, rsb, pad, y_divs, y_span, y_from, mode='mirror')
        else:
            rst, rsb = (rst+pad, rsb-pad)
        for s in self.stretches:
            ss = s.sides
            dd = s.delta
            if ss.startswith('px'):
                ss = ss[2:]
            if ss!='':
                for c in ss:
                    if c=='l':
                        rsl+=dd
                    elif c=='t':
                        rst-=dd
                    elif c=='r':
                        rsr+=dd
                    elif c=='b':
                        rsb-=dd
                    elif c=='x':
                        rsl+=dd
                        rsr+=dd
                    elif c=='y':
                        rst-=dd
                        rsb-=dd
                    elif c=='w':
                        rsl-=dd
                        rsr+=dd
                    elif c=='h':
                        rst-=dd
                        rsb+=dd
            else:
                rsl-=dd
                rst-=dd
                rsr+=dd
                rsb+=dd

        #return rsl-4, rst, rsr+4, rsb+4
        return R.from_tuple_ltrb((rsl, rst, rsr, rsb))
    

    @staticmethod
    def guess1(ws_rect:R, pad, w_rect:R):
        wsl,wst,wsr,wsb = ws_rect.as_tuple_ltrb()
        wl, wt, wr, wb = w_rect.as_tuple_ltrb()

        dd = 1000000
        for cc in range(1,10):
            _cols = SpreadCode.spread_path(wsl,wsr,cc,pad)
            for rc in range(1,10):
                _rows = SpreadCode.spread_path(wst,wsb,rc,pad)
                d0 = 1000000
                d1 = 1000000
                for i in range(0,cc):
                    for j in range(0,rc):
                        d0x = wl-_cols[i][0]
                        d0y = wt-_rows[j][0]
                        d0d = math.sqrt(d0x**2+d0y**2)
                        if d0d < d0:
                            d0 = d0d
                            d0i = i
                            d0j = j
                        d1x = wr-_cols[i][1]
                        d1y = wb-_rows[j][1]
                        d1d = math.sqrt(d1x**2+d1y**2)
                        if d1d < d1:
                            d1 = d1d
                            d1i = i
                            d1j = j
                d3 = d1 + d0
                if d3 < dd:
                    dd = d3
                    d_cols = cc
                    d_rows = rc
                    d0from = d0i+1
                    d0span = d1i-d0i+1
                    d1from = d0j+1
                    d1span = d1j-d1j+1
                    if dd<0.1:
                        break
                if dd<0.1:
                    break
            if dd<0.1:
                break
        
        if [x for x in (d_cols,d0span,d0from,d_rows,d1span,d1from) if x >=10]:
            scode = f'{d_cols}.{d0span}.{d0from}/{d_rows}.{d1span}.{d1from}'
        else:
            scode = f'{d_cols}{d0span}{d0from}/{d_rows}{d1span}{d1from}'
        return scode

    @staticmethod
    def area_of_quadrilateral(vertices):
        """
        Calculate the area of a quadrilateral given its vertices.
        
        Parameters:
        vertices (list of tuples): A list of four tuples, each containing the (x, y) coordinates of a vertex.
        
        Returns:
        float: The area of the quadrilateral.
        """
        #if len(vertices) != 4:
        #    raise ValueError("There must be exactly four vertices.")
        #v = [(x,-y) for x,y in vertices]
        v = vertices
        x1, y1 = v[0]
        x2, y2 = v[1]
        x3, y3 = v[2]
        x4, y4 = v[3]
        
        # Using the Shoelace formula
        #area = 0.5 * abs(x1*y2 + x2*y3 + x3*y4 + x4*y1 - y1*x2 - y2*x3 - y3*x4 - y4*x1)
        area = 0.5 * abs(x1*y2 + x2*y3 + x3*y4 + x4*y1 - y1*x2 - y2*x3 - y3*x4 - y4*x1)
        
        return area



    @staticmethod
    def guess(ws_rect:R, pad, w_rect:R, ratio=None, options=None):
        wsl,wst,wsr,wsb = ws_rect.as_tuple_ltrb()
        wl, wt, wr, wb = w_rect.as_tuple_ltrb()
        t0 = ((wb-wt)/(wr-wl))
        dd = 1000000000

        if ratio is not None:
            scols, srows = ratio.split('/')
            lcols, lrows = (int(scols), int(srows))
            ucols, urows = (lcols+1, lrows+1)
        else:
            lcols, lrows = (1,1)
            ucols, urows = (10,10)
        for cc in range(lcols,ucols):
            _cols = SpreadCode.spread_path(wsl,wsr,cc,pad)
            for rc in range(lrows,urows):
                _rows = SpreadCode.spread_path(wst,wsb,rc,pad)
                for x1 in range(0,cc):
                    for y1 in range(0,rc):
                        for x2 in range(x1,cc):
                            for y2 in range(y1,rc):
                                l = _cols[x1][0]
                                t = _rows[y1][0]
                                r = _cols[x2][1]
                                b = _rows[y2][1]
                                t1 = math.sqrt( (t-wt)**2 + (l-wl)**2 )
                                t2 = math.sqrt( (b-wb)**2 + (r-wr)**2 )
                                ax = (t1+t2)/2
                                if ax < dd:
                                    dd = ax
                                    rows = _rows
                                    cols = _cols
                                    dc = cc
                                    dr = rc
                                    dx1 = x1
                                    dy1 = y1
                                    dx2 = x2
                                    dy2 = y2
                                    ddt = t
                                    ddl = l
                                    ddr = r
                                    ddb = b
                    
        # dr-oj perchè la y la volgio dare come le ordinate, che crescono salendo == mirrored di sopra
        for x in (dc,dx2-dx1+1,dx1+1,dr,dy2-dy1+1,dr-dy2):
            if x>=10:
                scode = f'{dc}.{dx2-dx1+1}.{dx1+1}/{dr}.{dy2-dy1+1}.{dr-dy2}'
                break
        else:        
            scode = f'{dc}{dx2-dx1+1}{dx1+1}/{dr}{dy2-dy1+1}{dr-dy2}'
        if options is not None:
            if 'complete' in options:
                deltas = [(wl-ddl,'l'), (wt-ddt,'t'), (wr-ddr,'r'), (wb-ddb,'b')]
                d1=[]
                for _a, _b in deltas:
                    if _a != 0:
                        for _i, (_c, _d), in enumerate(d1):
                            if _c==_a:
                                d1[_i]=(_c, _d+_b)
                                break
                            elif _b=='r' and 'l' in _d and _a==-_c:
                                d1[_i]=(_a if _a<0 else _c, _d.replace('l','w'))
                                break
                            elif _b=='b' and 't' in _d and _a==-_c:
                                d1[_i]=(_a if _a<0 else _c, _d.replace('t','h'))
                                break
                        else:
                            d1.append((_a,_b))
                for _a, _b in d1:
                    scode += f'{_a:+d}{_b}'
        if isinstance(ws_rect,M):
            m0 = ws_rect
            ml = M.list_monitors()
            for i, m1 in enumerate(ml):
                if m1.hmon == m0.hmon:
                    scode += f':{i+1}'
                    break
        if options is not None:
            if 'debug' in options:
                return scode, (dd,(wl,wt,wr,wb),(ddl,ddt,ddr,ddb))
        return scode

                        





        


    
    




