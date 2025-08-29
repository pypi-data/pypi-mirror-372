import os
import winshell
import string
from .config import *
from ..smarts import smartmatch, SmartMatch
import re
from typing import List, Type
import sys

PUNTUACTION = string.punctuation.replace('-','')
PUNTUACTION_RE_ESCAPED = re.escape(PUNTUACTION)
TRANSLATION_TABLE = str.maketrans(PUNTUACTION, ":"*len(PUNTUACTION))

class Pattern:
    id = None
    re1 = None
    base_path = None
    zone = None
    subs_sep = ''
    def __init__(self, path=None):
        super().__init__()
        self.path = path
        self.matched = None
    @classmethod
    def includes(cls, path):
        return path.startswith(cls.base_path)   
    def match(self):
        self.matched = smartmatch()
        return self.matched(self.re1,self.path)  
    def test(self, spec):
        return re.match(self.re1,spec)     
    def canonical(self, default=None, compact=False):
        if self.matched:
            code = default
            zone = self.matched[('zone',str,None)]
            if zone is None:
                return code
            code = zone
            root = self.matched[('root',str,None)]
            if root is not None:
                code = f'{code}-{root}'
                subs = self.matched[('subs',str,None)]
                if subs is not None:
                    code = f'{code}{self.subs_sep}{subs.translate(TRANSLATION_TABLE)}'
            if not compact:
                name = self.matched[('name',str,None)]
                if name is not None:
                    code = f'{code}-{name}'
            return code
        else:
            rel_path = self.path[len(self.base_path)+1:]
            parts = rel_path.split(os.path.sep)
            for part in parts[:1]:
                if re.match(self.re1, part):
                    code = self.canonicalize(part,None,True)
                else:
                    code = f'{self.zone}-{part}'
            if len(parts)>1:
                for part in parts[1:-1]:
                    part_code = self.canonicalize(part,part,True)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
                for part in parts[-1:]:
                    part_code = self.canonicalize(part,part,compact)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
            return code
        
    @classmethod
    def canonicalize(cls, spec, default=None, compact=False):
        if os.path.sep in spec:
            real_path = os.path.realpath(spec)            
            if not cls.includes(real_path):
                return default
            return cls(real_path).canonical(default, compact)
        else:
            p = cls(spec)
            if not p.match():
                return default
            return p.canonical(default, compact)

class Pattern11(Pattern):
    id = '11'
    zone = '11'
    subs_sep = ''
    re1 = r'(?P<zone>11)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\1'

class Pattern21(Pattern):
    id = '21'
    zone = '21'
    subs_sep = ''
    re1 = r'(?P<zone>21)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\2'

class Pattern31(Pattern):
    zone = '31'
    subs_sep = ''
    def canonical(self, default=None, compact=False):
        if self.matched:
            code = default
            zone = self.matched[('zone',str,None)]
            if zone is None:
                return code
            code = zone
            root = self.matched[('root',str,None)]
            if root is not None:
                code = f'{code}-{root}'
                subs = self.matched[('subs',str,None)]
                if subs is not None:
                    code = f'{code}{self.subs_sep}{subs.translate(TRANSLATION_TABLE)}'
            if not compact:
                name = self.matched[('name',str,None)]
                if name is not None:
                    code = f'{code}-{name}'
            return code
        else:
            rel_path = self.path[len(self.base_path)+1:]
            parts = rel_path.split(os.path.sep)
            for part in parts[:1]:
                if re.match(self.re1, part):
                    code = self.canonicalize(part,None,True)
                else:
                    code = f'31-{part}'
            if len(parts)>1:
                for part in parts[1:-1]:
                    part_code = self.canonicalize(part,part,True)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
                for part in parts[-1:]:
                    part_code = self.canonicalize(part,part,compact)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
            return code

class Pattern31d(Pattern31):
    id = '31d'
    re1 = r'(?P<zone>31)-(?P<root>D[A-Z0-9]{4})(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\3\\1\\1'

class Pattern31m(Pattern31):
    id = '31m'
    re1 = r'(?P<zone>31)-(?P<root>M[0-9]{2})(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\3\\1\\2'
    subs_sep = ':'

class Pattern31o(Pattern31):
    id = '31o'
    re1 = r'(?P<zone>31)-(?P<root>O[A-Z0-9]{4})(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\3\\1\\3'

class Pattern31c(Pattern31):
    id = '31c'
    re1 = r'(?P<zone>31)-(?P<root>C[0-9]{2})(?:(?P<subs>[^-]+))?(?:-(?P<name>.+))?'
    base_path = 'C:\\1\\W\\3\\1\\4'
    subs_sep = ':'


class Pattern41(Pattern):
    id = '41'
    zone = '41'
    re_name = r'(?P<name>.+)'
    re_subs = r'(?P<subs>[^-]+)'
    re_time = r'(?P<time>[0-9]{4})'
    re_day = r'(?P<day>[0-9]{2})'
    re_month = r'(?P<month>[0-9]{2})'
    re_year = r'(?P<year>[0-9]{2})'
    re_zone = r'(?P<zone>41)'
    re1 = rf'{re_zone}-{re_year}(?:{re_month}(?:{re_day}(?:\.{re_time}(?:{re_subs})?)?)?)?(?:-{re_name})?'
    base_path = 'C:\\1\\W\\4'
    #format_code = lambda self, zone, root, subs: f'{zone}-{root}:{subs}'
    def canonical(self, default=None, compact=False):
        if self.matched:
            code = default
            zone = self.matched[('zone',str,None)]
            if zone is None:
                return code
            code = zone
            year = self.matched[('year',str,None)]
            if year is not None:
                code = f'{code}-{year}'
                month = self.matched[('month',str,None)]
                if month is not None:
                    code = f'{code}:{month}'
                    day = self.matched[('day',str,None)]
                    if day is not None:
                        code = f'{code}:{day}'
                        time = self.matched[('time',str,None)]
                        if time is not None:
                            code = f'{code}:{time}'
                            subs = self.matched[('subs',str,'')]
                            if subs is not None:
                                code = f'{code}:{subs.translate(TRANSLATION_TABLE)}'
            if not compact:
                name = self.matched[('name',str,None)]
                if name is not None:
                    code = f'{code}-{name}'
            return code
        else:
            rel_path = self.path[len(self.base_path)+1:]
            parts = rel_path.split(os.path.sep)
            for part in parts[:1]:
                if re.match(self.re1, part):
                    code = self.canonicalize(part,None,True)
                else:
                    code = f'{self.zone}-{part}'
            if len(parts)>1:
                for part in parts[1:-1]:
                    part_code = self.canonicalize(part,part,True)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
                for part in parts[-1:]:
                    part_code = self.canonicalize(part,part,compact)
                    if part_code.startswith(code):
                        code = part_code
                    else:
                        code += f':{part}'
            return code

class Pattern51(Pattern):
    id = '51'
    zone = '51'
    subs_sep = ''
    re1 = r'(?P<zone>51)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.*))?'
    base_path = 'C:\\1\\W\\5'


class Pattern61(Pattern):
    id = '61'
    zone = '61'
    subs_sep = ''
    re1 = r'(?P<zone>61)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.*))?'
    base_path = 'C:\\1\\W\\6'

class Pattern71(Pattern):
    id = '71'
    zone = '71'
    subs_sep = ''
    re1 = r'(?P<zone>71)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.*))?'
    base_path = 'C:\\1\\W\\7'

class PatternD1(Pattern):
    id = 'D1'
    zone = 'D1'
    subs_sep = ''
    re1 = r'(?P<zone>D1)-(?P<root>[A-Z0-9]+)(?:(?P<subs>[^-]+))?(?:-(?P<name>.*))?'
    base_path = 'C:\\1\\Y\\D1'

patterns : List[Type[Pattern]]= [
    Pattern11,
    Pattern21,
    Pattern31d,
    Pattern31m,
    Pattern31o,
    Pattern31c,
    Pattern41,
    Pattern51,
    Pattern61,
    Pattern71,
    PatternD1
]

'''
def canonical_name(path, default=None, compact=False):
    if os.path.sep in path:
        real_path = os.path.realpath(path)
        for pat in patterns:
            if pat.includes(real_path):
                break
        else:
            return default
        return pat(path).canonical(default, compact)
    else:
        for pat in patterns:
            p = pat(path)
            if p.match():
                break
        else:
            return default
        return p.canonical(default, compact)
'''

def pathname_complete(spec:str, default=None, options=[]):
    for pat in patterns:
        p = pat(spec)
        if p.match():
            break
    else:
        return default    
    spec_c = p.canonical(default)
    if spec_c is default:
        return spec_c
    spec_p = spec_c.split('-')
    if len(spec_p)<2:
        if os.path.exists(p.base_path):
            return p.base_path
        return
    result_list = []
    row_index = 0
    def walker(base_path, spec_r):   
        nonlocal row_index
        row_index += 1    
        print(f'>>> {row_index:5}: {base_path}', file=sys.stderr)
        matches = 0
        ld = os.listdir(base_path)
        spec_k = spec_c
        ld_c = []
        for item in ld:
            path = os.path.join(base_path,item)
            item_c = p.canonicalize(path)
            if item_c is None:
                continue 
            ld_c.append((item,item_c,path))
        ld_p = []
        ref_len = len(spec_r)
        while len(spec_k)>ref_len:
            for item, item_c, path in ld_c:
                if item_c.startswith(spec_k):
                    matches += 1
                    if spec_k == spec_c:
                        result_list.append(path)
                    if os.path.isdir(path):
                        ld_p.append((path,spec_k))
            if matches:
                break
            #spec_k = ':'.join(spec_k.split(':')[:-1]) if spec_k.count('-')==1 else '-'.join(spec_k.split('-')[0:2])
            spec_k = spec_k[:-1]
        for path, spec_k in ld_p:
            matches += walker(path,spec_k)
        return matches
    if not os.path.exists(p.base_path):
        return None
    walker(p.base_path,'')
    if len(result_list)==0:
        return None
    if 'resolve-links' in options:
        final_list = []
        for result_path in result_list:
            result_stack = [result_path]
            link_target = result_path
            while link_target.endswith('.lnk'):
                try:
                    with winshell.shortcut(result_path) as link:
                        link_target = link.path
                    #print('link-target-2', link_target)
                    if not os.path.exists(link_target):
                        break
                    result_stack.append(link_target)
                except:
                    break
            if 'stacked' in options:
                final_list.append(result_stack)
            else:
                final_list.append(result_stack[-1])
    else:
        if 'stacked' in options:
            final_list = [[c] for c in result_list]
        else:
            final_list = result_list
    return final_list if 'as-list' in options else final_list[0]



def locate(doc:str, options=[]):
    return pathname_complete(doc,options)






'''

def ___canonical_name(path, alt=None, compact=False):
    prefix = ''
    if path.find(os.path.sep)>=0:
        path_real = os.path.realpath(path)
        for part, area, drive in ( (W_FOLDER_PATH,'W','X:\\W'), 
                                  (S_FOLDER_PATH,'S','X:\\S'), 
                                  (X_FOLDER_PATH,'X','X:\\X'), 
                                  (Y_FOLDER_PATH,'Y','Y:\\') ):        
            if path_real.startswith(part):
                mark = 3
                break
            if path_real.startswith(drive):
                mark = 2
                break
        else:
            return alt
        path_parts = path_real.split(os.path.sep)
        if mark>=len(path_parts):
            return alt
        match area:
            case 'W':
                zone = path_parts[mark] + '1'
            case 'S':
                zone = path_parts[mark] + '0'
            case 'Y':
                zone = '-'.join(path_parts[mark] .split('-')[:2])
            case _:
                return alt
        offset = mark + 1
        if offset>=len(path_parts):
            return zone
        prefix=f'{zone}-'
        if zone=='31':
            if path_parts[offset] != '1':
                return alt
            offset += 1
            if offset>=len(path_parts):
                return alt
            map = {'1':'D','2':'M','3':'O','4':'F','5':'C','6':'S'}
            if path_parts[offset] not in map:
                return alt
            offset += 1
            if offset>=len(path_parts):
                return alt
            part = path_parts[offset]
            p = __canonical_name(part,'',compact=True)
        else:
            part = path_parts[offset]
            p = __canonical_name(part,'',compact=True)
        if p.startswith(zone):
            prefix = p
        else:
            for c in part:
                if c in string.punctuation:
                    return alt
            prefix += part
        offset += 1 
        if offset>=len(path_parts):
            return prefix 
        offset += 1
        for i, part in enumerate(path_parts[offset:-1],0):
            p = __canonical_name(part,'',compact=True)
            if p.startswith(prefix):
                prefix = p
            else:
                for c in part:
                    if c in string.punctuation:
                        return alt
                prefix = f'{prefix}:{part}' 
        part = path_parts[-1]
        p = __canonical_name(part,'')
        if p.startswith(prefix):
            return p
        else:
            for c in part:
                if c in string.punctuation:
                    return alt
            return f'{prefix}:{part}'
    else:
        parts = path.split('-')
        if 2>len(parts):
            return alt
        parts[1] = ''.join([c if c not in PUNTUACTION else ':' for c in parts[1] ])
        if parts[0][0] == '4':
            if len(parts[1])>2:
                parts[1] = parts[1][:2] + ':'+ parts[1][2:]    
            if len(parts[1])>5:
                parts[1] = parts[1][:5] + ':'+ parts[1][5:]    
        if compact:
            return '-'.join(parts[:2])
        else:
            return '-'.join(parts)


'''