import re

class SmartTupleBuilder:
    def __init__(self):
        pass
    def __call__(self, **kwds):
        return kwds

smarttuple = SmartTupleBuilder()

class SmartClass:
    def __init__(self,**kwargs):
       self.__SmartClass__ = list(kwargs.keys())
       self.__dict__.update(kwargs) 
    def as_tuple(self):
        return tuple([self.__dict__[k] for k in self.__SmartClass__])
    def as_dict(self):
        return {k:self.__dict__[k] for k in self.__SmartClass__}

class SmartClassBuilder:
    def __call__(self, **kwargs):
        return SmartClass(**kwargs)
    def from_tree(self,root):
        def walker(node):
            if type(node) is dict:                
                v = SmartClass(**{kk:walker(xx) for kk,xx in node.items()})
            elif type(node) is list:
                v = [walker(xx) for xx in node]
            elif type(node) is tuple:
                v = (walker(xx) for xx in node)
            else:
                v = node
            return v
        return walker(root)
        
smartclass = SmartClassBuilder()



class SmartMatch:
    def __init__(self):
        self.lastmatch : re.Match = None
    def __call__(self, *args, **kwds):
        self.lastmatch = re.match(*args,**kwds)
        return self.lastmatch
    def __getattr__(self,name):
        return self.__getitem__(name)
    def __getitem__(self, key):
        if type(key) is tuple:
            _key, _cast, _default = key
            _val = self.lastmatch.groupdict().get(_key,None)
            if _val is not None:
                return _cast(_val)
            else:
                return _default
        else:            
            return self.lastmatch.groupdict().get(key,None)
    def __contains__(self, key):
        v = self.lastmatch.groupdict().get(key,None)
        return v is not None
    def keys(self):
        return self.lastmatch.groupdict().keys()
    def items(self):
        return self.lastmatch.groupdict().items()
    def values(self):
        return self.lastmatch.groupdict().values()
    def escape(self, **keys):
        return {k:v.encode('unicode-escape').decode() for k,v in self.items() if v is not None and (not keys or k in keys)}
        


class SmartMatchBuilder:
    def __call__(self, **kwargs):
        return SmartMatch(**kwargs) 
smartmatch = SmartMatchBuilder()
