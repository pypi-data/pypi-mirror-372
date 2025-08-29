#from typing import Any
#from builtins import type as builtin_type
#import itertools
import types
import functools
#from functools import partial
from . import layers
#from __future__ import annotations
#import logging
# Example of logging a debug message
#logging.debug("This is a debug message.")



# element
# ogni funzione o classe decorata con @element diventa un simbolo globale nella gerarchia di strutturazione dell'applicazione.
# Un element è un nodo di gestione per un compito specifico
# - può essere un elemento di interfaccia utente, come un widget o una window
# - può essere un elemento di gestione dati, tipo una tablle, un record.

# scope
# - [0]: root scope
# - [1]: scope appena sotto root percorrendo lo scope-bhanch all'indietro
# - [-1]: base scope
# - ['<path>']: scope at path, in teoria potremmo gestire anche le stringhe quì ed usare anche un approccio tipo pathname uri
# - base: base scope
# - mass: elemento più vicino, precorrendo lo scope-branch all'indietro, che è di categoria "data" (table,record,ecc)
# - tool: elemento più vicino, precorrendo lo scope-branch all'indietro, che è di categoria "tool" (widget,window,ecc)


# @element decorator
#def element(scope=scope_root, type=None, *args, **kwargs):
#    return lambda item, scope=scope, type=type, args=args, kwargs=kwargs: element_factory(scope,type,item,*args,**kwargs)

# penso che se ElementDecorator.__call__() ritorna una istanza di una classe fatta come sotto, 
# gestendo opportunamente __call__, __enter__ e __exit__,
# si dovrebbe poter usare il simbolo "element" si come decoratore che come context-manager

def dprint(*args,**kwargs):
    pass
class Wrapper:
    pass
class Joint:
    def Wrapper(_scope, _callee, *_args, **_kwargs) -> type:
        class WrapperType(Wrapper):
            base_scope = _scope
            base_kwargs = dict(_kwargs)
            base_args = list(_args)
            base_callee = staticmethod(_callee)
            ismethod = isinstance(_callee,types.MethodType)
            def free(self):
                if type(self) is not type:
                    for k in self.kwargs:
                        x = self.__dict__[k] 
                        self.__dict__[k] = f'id(0x{id(x):X})'
                    self.kwargs.clear()
                    self.callee = f'id(0x{id(self.callee):X})'
                    self.scope = f'id(0x{id(self.scope):X})'
                self.base_args.clear()
                self.base_kwargs.clear()
                self.base_callee = f'id(0x{id(self.base_callee):X})'
                self.base_scope = f'id(0x{id(self.base_scope):X})'
                
            def scoped(self):
                self.scope.__joint__.add_referrer('wrapper',self)
                return self
            
            def  __init__(self, **_kwargs):
                functools.update_wrapper(self,self.base_callee)
                self.scope = self.base_scope
                self.callee = self.base_callee
                self.kwargs = dict(self.base_kwargs)
                self.kwargs.update(_kwargs)
                self.__dict__.update(self.kwargs)
            def __get__(self, obj, owner):
                if self.ismethod:
                    return types.MethodType(self,obj)
                else:
                    return self
            def __call__(self, *_args, **_kwargs):
                return self.callee(self,*_args,**_kwargs)
            def select_scope(self, *scopes):
                for scope in scopes:
                    if scope is not None:
                        return scope
                else:
                    return self.scope
            def divert_scope(self, mold, molded):
                if self.scope is mold:
                    return self.select_scope(molded)
                else:
                    return self.scope
        _scope.__joint__.add_referrer('Wrapper',WrapperType)
        return WrapperType
    
    def __init__(self, name=None, pool=None, base=None, mass=None, tool=None, 
                 call=None, call2=None, this=None, mold=None, layer=None, 
                 host=None, tag=None, overrides=None):
        self.name = name
        self.pool = pool
        self.base : Scope = base
        self.mass = mass if mass is not None else base.__joint__.mass if base is not None else None
        self.tool = tool if tool is not None else base.__joint__.tool if base is not None else None
        self.call2 = call2
        self.call = call
        self.this = this
        self.mold = mold
        if layer is None:
            if mold is not None:
                layer = mold.__joint__.layer
        if layer is None:
            if base is not None:
                layer = base.__joint__.layer
        if layer is None:
            layer = layers.common.CommonLayer()
        self.layer = layer 
        self.host = host
        self.tag = tag
        self.overrides = overrides
        self.routines = {}
        self.referrers = []
        #self.features = {}
        self.counter = 0
        self.bond = None

    def add_referrer(self,role,scope=None,drop=None):
        self.referrers.append((role,scope,drop))

    def __del__(self):
        dprint(f"__del__: {self}")
        #logging.debug(f"__del__: {self}")
        pass

    def __repr__(self):
        return f'Joint tag:"{self.tag}" at:0x{id(self):X}({id(self)})'

    def free(self, scope=None):
        #self.features = f"id(0x{id(self.features):X})"

        for _role, _scope, _drop in reversed(self.referrers):
            if _role in ('element','feature','cluster','section'):
                _scope.__joint__.free(_scope)
            elif _role in ('binding','routine','attribute'):
                __scope, __name = _scope
                ref = getattr(__scope,__name,None)
                if ref is not None:
                    setattr(__scope,__name,f'id(0x{id(ref):X})')
            elif _role=='base':
                __scope, __name = self.base, self.name
                ref = getattr(__scope,__name,None)
                if ref is not None:
                    setattr(__scope,__name,f'id(0x{id(ref):X})')

        for _role, _scope, _drop in reversed(self.referrers):
            if _role == 'Wrapper':
                _scope.free(_scope)
            elif _role == 'wrapper':
                _scope.free()

        self.referrers.clear()
        #for x, (y,z) in reversed(self.routines.items()):
        #    for w in z:
        #        w.free(w)
        #    y.free()
        self.routines.clear()
        #self.routines = f"id(0x{id(self.routines):X})"
        if self.call2 is not None:
            self.call2 = f"id(0x{id(self.call2):X})"
        if self.call is not None:
            self.call = f"id(0x{id(self.call):X})"
        if self.mold is not None:
            self.mold = f"id(0x{id(self.mold):X})"
        if self.host is not None:
            self.host = f"id(0x{id(self.host):X})"
        if self.layer is not None:
            self.layer = f"id(0x{id(self.layer):X})"
        if self.base is not None:
            self.base = f"id(0x{id(self.base):X})"
        if self.tool is not None:
            self.tool = f"id(0x{id(self.tool):X})"
        if self.mass is not None:
            self.mass = f"id(0x{id(self.mass):X})"
        if self.this is not None:
            self.this = f"id(0x{id(self.this):X})"
        #if self.pool is not None:
        #    self.pool = f"id(0x{id(self.pool):X})"



    def routine_wrap(self, scope, host, name, item, aggregation=None, **kwargs):
        final_name = name
        final_wrapper = None
        final_host = None
        r_list = None        
        if host is None:
            if scope.__joint__.host is not None:
                final_host = scope.__joint__.host
                final_wrapper, r_list = scope.__joint__.host.__joint__.routines.get(final_name,(None,None))
        else:
            if isinstance(host, types.FunctionType):
                final_wrapper, _list = getattr(host,'__sequence__',(None,None))
            elif isinstance(host, types.MethodType) and isinstance(host.__self__,Scope):
                #host.__func__ is host.__self__.__joint__.routines['free'][0]  -> True
                r_dict = host.__self__.__joint__.routines
                for n, (r, l) in r_dict.items():
                    if r is host.__func__:
                        break
                else:
                    raise Exception('routine_wrap failed')    
                final_name = n
                final_wrapper = r
                r_list = l
                final_host = host.__self__
                pass
            elif isinstance(host,Scope):         
                final_host = host       
                final_wrapper, _list = getattr(host,'__sequence__',(None,None))
            else:
                raise Exception('routine_wrap failed')
        class RoutineWrapper(Joint.Wrapper(scope,item)):
            def __call__(self, _scope=None, *args, **kwargs):
                with self.select_scope(_scope) as scope:
                    return self.callee(scope,*args,**kwargs)        
        if final_wrapper and r_list:
            r_list.append(RoutineWrapper)
            class FinalWrapper(Joint.Wrapper(scope, item, host=final_host, accessor=final_wrapper)):
                def __call__(self, _scope=None, *args, **kwargs):
                    return self.accessor(self.host,*args,**kwargs)
            final_wrapper = FinalWrapper().scoped()
        else:
            if not aggregation:
                aggregation = 'ordered'
            if aggregation=='reversed':
                class FinalWrapper(Joint.Wrapper(scope,item,final_name=final_name)):
                    def __call__(self, _scope=None, *args, **kwargs):
                        with self.select_scope(_scope) as enclosing_scope:
                            _, _list = enclosing_scope.__joint__.routines[self.final_name]
                            for Wrapper in reversed(_list):
                                wrapper = Wrapper(detached=True, enclosing_scope=enclosing_scope)
                                with wrapper.scope as scope:
                                    wrapper(scope,*args,**kwargs)                    
            else:
                class FinalWrapper(Joint.Wrapper(scope,item,final_name=final_name)):
                    def __call__(self, _scope=None, *args, **kwargs):
                        with self.select_scope(_scope) as enclosing_scope:
                            _, _list = enclosing_scope.__joint__.routines[self.final_name]
                            for Wrapper in _list:
                                wrapper = Wrapper(detached=True, enclosing_scope=enclosing_scope)
                                with wrapper.scope as scope:
                                    result = wrapper(scope,*args,**kwargs)                    
                                    if result is not None:
                                        return result
            routine_wrapper = FinalWrapper().scoped()
            self.routines[final_name] = (routine_wrapper, [RoutineWrapper])
            final_wrapper = routine_wrapper        
        setattr(scope, item.__name__, types.MethodType(final_wrapper, scope))
        scope.__joint__.add_referrer('routine',(scope, item.__name__))
        return final_wrapper
        
    def feature_wrap(self, scope, name, item):
        host = self.host
        helper = item
        final_name = name
        final_host = host
        '''
        qui bisogna ragionare sul fatto che si abbia o meno un host altrimenti non funziona un piffero
        dato che ora è sempre una funzione 
        '''
        #raise Exception('Leggi il commento sopra')
        if host is None:
            class FeatureWrapper(Joint.Wraper(scope,item)):
                def __call__(self,_scope=None,*args,**kwargs):
                    with self.select_scope(_scope) as scope:
                        self.callee(scope,*args,**kwargs)
            self.routines[final_name] = (FeatureWrapper(), [FeatureWrapper])
            wrapper = final_wrapper
            target = item
        else:
            final_wrapper, _list = final_host.__joint__.routines[final_host.__name__]
            class FeatureWrapper(Joint.Wrapper(scope,item,molded=None)):
                def __call__(self, __scope=None, *args, **kwargs):                    
                    if self.molded is not None:                      
                        _scope = self.scope  
                        _joint = _scope.__joint__
                        _joint.counter += 1
                        joint = Joint(name=_joint.name, pool=_joint.pool,base=_joint.base,
                                      mass=_joint.mass,call=_joint.call,call2=_joint.call2,this=_joint.this,
                                      overrides=_joint.overrides, host=self.molded, mold=_scope, tag=f'{_joint.tag}#{_joint.counter}')
                        scope = type(_scope)(joint)
                        with scope:
                            res = self.callee(scope,*args,**kwargs)                
                            if res is not None:
                                pass 
            _list.append(FeatureWrapper)
            wrapper = final_wrapper
            target = item
        def simple_wrapper(scope, *args, **kwargs):
            with scope:
                helper(scope,*args,**kwargs)
        helper.wrapper = simple_wrapper
        self.name = final_name        
        scope.__joint__.base.__joint__.add_referrer('feature',scope)
        scope.__joint__.add_referrer('base')
        return target, wrapper, helper, final_name

    def element_wrap(self, scope, name, item):
        final_name = name
        if isinstance(item, types.FunctionType):
            class ElementWrapperAccessor(Joint.Wrapper(scope,item,final_name=final_name)):
                def __call__(self,_scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as enclosing_scope:
                        _, _list = enclosing_scope.__joint__.routines[self.final_name]
                        for Wrapper in _list:
                            wrapper = Wrapper(enclosing_scope=enclosing_scope)
                            with wrapper.scope as scope:
                                wrapper(scope,*args,**kwargs)
            element_wrapper = ElementWrapperAccessor()
            class ElementWrapper(Joint.Wrapper(scope,item)):
                def __call__(self, _scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as scope:
                        self.callee(scope,*args,**kwargs)
            self.routines[final_name] = (element_wrapper, [ElementWrapper])
            helper = item
            wrapper = element_wrapper
            target = wrapper
        else:
            raise Exception('UNIMPLEMENTED')
        class SimpleWrapper(Joint.Wrapper(scope,helper)):
            def __call__(self, _scope=None, *args, **kwargs):
                with self.select_scope(_scope) as scope:
                    self.callee(scope,*args,**kwargs)
        simple_wrapper = SimpleWrapper().scoped()
        helper.wrapper = simple_wrapper
        self.name = final_name
        scope.__joint__.base.__joint__.add_referrer('element',scope)
        scope.__joint__.add_referrer('base')
        return target, wrapper, helper, final_name
    
    def section_wrap(self, scope, name, item):
        final_name = name
        if isinstance(item, types.FunctionType):
            class SectionWrapper(Joint.Wrapper(scope, item)):
                def __call__(self, _scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as scope:
                        self.callee(scope,*args,**kwargs)
            class SectionAccessor(Joint.Wrapper(scope, item, final_name=final_name)):
                def __call__(self, _scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as enclosing_scope:
                        _, _list = enclosing_scope.__joint__.routines[self.final_name]
                        for Wrapper in _list:
                            wrapper = Wrapper(enclosing_scope=enclosing_scope)
                            with wrapper.scope as scope:                                
                                wrapper(scope,*args,**kwargs)
            section_wrapper = SectionAccessor()
            self.routines[final_name] = (section_wrapper, [SectionWrapper])
            helper = item
            wrapper = section_wrapper
            target = wrapper
        else:
            raise Exception('UNIMPLEMENTED')
        class SimpleWrapper(Joint.Wrapper(scope,helper)):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs)
                pass
            def __call__(self, _scope=None, *args, **kwargs):
                with self.select_scope(_scope) as scope:
                    self.callee(scope,*args,**kwargs)
        simple_wrapper = SimpleWrapper().scoped()
        helper.wrapper = simple_wrapper
        self.name = final_name
        scope.__joint__.base.__joint__.add_referrer('section',scope)
        scope.__joint__.add_referrer('base')
        return target, wrapper, helper, final_name

    def cluster_wrap(self, scope, name, item):
        final_name = name
        if isinstance(item, types.FunctionType):
            class ClusterWrapper(Joint.Wrapper(scope,item)):
                def __call__(self, _scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as scope:
                        self.callee(scope,*args,**kwargs)
            class ClusterAccessor(Joint.Wrapper(scope,item,final_name=final_name)):
                def __call__(self, _scope=None, *args, **kwargs):
                    with self.select_scope(_scope) as mold:
                        _joint = mold.__joint__
                        _joint.counter += 1
                        joint = Joint(name=_joint.name, pool=_joint.pool,base=_joint.base,mass=_joint.mass,
                                    call=_joint.call,this=_joint.this,host=_joint.host,mold=mold,
                                    tag=f'{_joint.tag}#{_joint.counter}') 
                        molded = type(mold)(joint)
                        _, _list = mold.__joint__.routines[self.final_name]
                        for Wrapper in _list:
                            wrapper = Wrapper(molded=molded)                                        
                            with wrapper.divert_scope(mold, molded) as scope:
                                wrapper(scope,*args,**kwargs)
            cluster_wrapper = ClusterAccessor()
            self.routines[final_name] = (cluster_wrapper, [ClusterWrapper])
            helper = item
            wrapper = cluster_wrapper
            target = wrapper
        else:
            raise Exception('UNIMPLEMENTED')
        class SimpleWrapper(Joint.Wrapper(scope,helper)):
            def __call__(self, _scope=None, *args, **kwargs):
                with self.select_scope(_scope) as scope:
                    self.callee(scope,*args,**kwargs)
        simple_wrapper = SimpleWrapper().scoped()
        helper.wrapper = simple_wrapper
        self.name = final_name
        scope.__joint__.base.__joint__.add_referrer('cluster',scope)
        scope.__joint__.add_referrer('base')
        return target, wrapper, helper, final_name    
    
    def binding_wrap(self, scope, name, item):
        final_name = name
        helper = None
        wrapper = None
        target = item
        self.name = final_name
        scope.__joint__.add_referrer('binding',(scope,self.name))
        return target, wrapper, helper, final_name
    
    def realize(self, scope, *args, **kwargs):
        if self.bond:
            return self.bond(scope,*args,**kwargs)
    #def __del__(self):
    #    print(f'==> Joint.__del__ {self.tag} id={id(self):X} ')
      
class Scope:
    def __init__(self, joint:Joint):
        self.__joint__:Joint = joint
    def __enter__(self):        
        self.__joint__.pool.select(self)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__joint__.pool.restore()
    def __call__(self, *args, **kwargs):
        return self.__joint__.call(*args, **kwargs)
    def __getattr__(self, name):
        return getattr(self.__joint__.this,name)
    def __setattr__(self, name, value):
        inner = self.__dict__.get('__joint__',None)
        if inner:
            inner = inner.__dict__.get('this', None)
            if inner:
                if hasattr(inner,name):
                    return setattr(inner,name,value)
        return object.__setattr__(self,name,value)
    def __getitem__(self, key):
        return  self.__joint__.this.__getitem__(key)
    def __setitem__(self, key, value):
        return  self.__joint__.this.__setitem__(key, value)
    def __iter__(self):
        return self.__joint__.this.__iter__()
    def __del__(self):
        dprint(f"__del__: Scope of {self.__joint__}")
        #logging.debug(f"__del__: Scope of {self.__joint__}")
        #print(f'==> Scope.__del__ {type(self).__name__} {self.__joint__.tag} id={id(self):X} __joint__.id={id(self.__joint__):X}')
        pass
      
class Element(Scope):
    def __init__(self, joint):
        super().__init__(joint)        

class Section(Scope):
    def __init__(self, joint):
        super().__init__(joint)

class Cluster(Scope):
    def __init__(self, joint):
        super().__init__(joint)

class Decorator:
    def __init__(self, context, tag=None):
        self.context = context
        self.tag = tag
    def scope(self):
        return self.context.scope
    def __getattr__(self,name):
        return getattr(self.context.scope,name)
    def update(self, scope=None, **kwargs):
        if scope is None:
            scope = self.context.scope
        return scope.__joint__.__dict__.update(kwargs)
    def unbound(self, scope):
        return scope.__joint__.bond is None
    def realize(self, scope, *args, **kwargs):
        return scope.__joint__.realize(scope,*args,**kwargs)
    def free(self,scope):
        scope.__joint__.free(scope)


class Context:
    def __init__(self, tag = None):
        self.tag = tag
        self.scope_root = Scope(Joint(pool=self, base=None,mass=None,tool=None,tag='root'))
        self.scope = self.scope_root
        self.all = []
        self.line = []
        self.stack = []
        self.head = 0
        self.trail0 = {}
        self.trail = None
        self.stuff = None
        self.default_layer = None
    def take(self, builder):
        if builder.context is not self:
            return
        self.scope = builder.scope
        self.line.append(builder)
        self.head += 1
    def drop(self, builder):
        if builder.context is not self:
            return
        #### builder.context = None
        self.head -= 1
        self._build()
        self.scope = builder.scope.__joint__.base
    def select(self, scope):
        self.stack.append((self.scope,self.line,self.head,self.trail0,self.stuff))
        self.stuff = None
        self.trail = self.stack[-1][3]
        self.trail0 = {}
        self.scope = scope
        self.line = []
        self.head = 0
    def restore(self):
        self._build()
        self.scope, self.line, self.head, self.trail0, self.stuff = self.stack.pop() 
        self.trail = self.stack[-1][3] if self.stack else None
        return self.scope
    def _build(self):
        if self.head == 0 and self.line:
            line = self.line
            self.line = []
            for builder in line:
                save_scope = self.scope
                self.scope = builder.scope
                self.all.append(builder)
                builder.build()
                self.scope = save_scope
            if self.all:
                if builder is self.all[0]:
                    line = self.all
                    self.all = []
                    for builder in line:
                        save_scope = self.scope
                        with builder.scope:                        
                            builder.stage()

class ElementBuilder:
    def __init__(self, context=None, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs):
        self.context : Context = context
        # self.scope = Element(Joint(pool=context, base=scope, tag=intents, layer=layer))
        self.scope = None
        self.layer : layers.common.Layer = layer #self.scope.__joint__.layer
        self.base = scope 
        self.type = type
        self.intents = intents
        self.item = item
        self.helper = None
        self.name = None
        self.args = args
        self.kwargs = kwargs
        self.this = None
        # self.context.take(self)
    def __call__(self, item):
        if self.base is not None and hasattr(self.base,item.__name__):
            self.scope = getattr(self.base,item.__name__)
            self.building = False
        else:
            self.scope = Element(Joint(pool=self.context, base=self.base, tag=self.intents, layer=self.layer))
            self.building = True
        self.layer = self.scope.__joint__.layer
        self.context.take(self)
        target, wrapper, helper, name = self.scope.__joint__.element_wrap(self.scope,item.__name__,item)
        self.item = item
        self.helper = helper
        self.wrapper = wrapper
        self.name = name
        self.context.drop(self)
        return self.scope ### target            
    def __enter__(self) -> Scope:        
        self.layer.item_enter(self)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.layer.item_leave(self)
    def stage(self):
        self.layer.item_stage(self)
    def build(self):
        scope = self.scope
        item = self.item
        helper = self.helper
        if self.building:
            this = self.layer.item_build(self)
            scope.__joint__.this = this
        else:
            this = scope.__joint__.this
        scope.__joint__.call = self.wrapper
        scope.__joint__.call2 = self.helper.wrapper
        self.this = this
        attrs = self.kwargs.get('attrs',None)
        if attrs:
            scope.__dict__.update(attrs)
        if item is not None:
            delegated_bindings = [k for k in self.kwargs if k in ('bind','bindings')]
            with self:
                if type(item) is str:                
                    pass ##print('build_end -> str -> ', item)    
                elif isinstance(item, types.FunctionType):
                    setattr(scope.__joint__.base,self.name,scope)
                    if not delegated_bindings:
                        helper(scope)
                else:
                    setattr(scope.__joint__.base,self.name,scope)
                    if not delegated_bindings:
                        if this is not None and helper is not None:
                            helper(this, scope)
            
class ElementDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        self.stack = []
    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__\n')
    def __call__(self, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs) -> ElementBuilder:
        if scope is None:
            scope = self.scope()
        self.update(scope, closest_layer=layer)
        return ElementBuilder(context=self.context, scope=scope, type=type, intents=intents, item=item, layer=layer, *args, **kwargs)
    def __enter__(self) -> Scope:        
        self.stack.append(self.context.scope)
        return self.context.scope
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.scope = self.stack.pop()
    def free(self, scope):
        return scope.__joint__.free(scope)

class SectionBuilder:
    def __init__(self, context=None, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs):
        self.context : Context = context
        self.scope = Section(Joint(pool=context, base=scope, tag=intents, layer=layer))
        self.layer : layers.common.layer = self.scope.__joint__.layer
        self.base = scope
        self.type = type
        self.intents = intents
        self.item = item
        self.helper = None
        self.name = None
        self.args = args
        self.kwargs = kwargs
        self.this = None
        self.context.take(self)        

    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__ {self.name}\n')

    def __call__(self, item):
        #print("ElementBuilder.__call___:",self.intents)
        # self.scope = Section(Joint(pool=self.context, base=self.base, tag=self.intents))
        #self.context.take(self)
        target, wrapper, helper, name = self.scope.__joint__.section_wrap(self.scope,item.__name__,item)
        self.item = item
        self.helper = helper
        self.wrapper = wrapper
        self.name = name
        self.context.drop(self)
        return self.scope 
    def __enter__(self) -> Scope:        
        return None
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def build(self):
        scope = self.scope
        item = self.item
        this = self.layer.item_build(self)
        if  False:
            if type(self.type) is type:       
                this = self.type()     
            else:
                if type(item) is type:
                    this = item()     
                else:
                    this = item
        scope.__joint__.call = self.wrapper
        scope.__joint__.call2 = self.helper.wrapper
        scope.__joint__.this = this
        self.this = this
        attrs = self.kwargs.get('attrs',None)
        if attrs:
            scope.__dict__.update(attrs)
        setattr(scope.__joint__.base,self.name,scope)        
    def stage(self):
        pass

class SectionDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        self.stack = []
    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__\n')
    def __call__(self, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs) -> SectionBuilder:
        if scope is None:
            scope = self.scope()
        self.update(scope, closest_layer=layer)
        return SectionBuilder(context=scope.__joint__.pool, scope=scope, type=type, intents=intents, item=item, layer=layer, *args, **kwargs)
    def __enter__(self) -> Scope:        
        self.stack.append(self.context.scope)
        return self.context.scope
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.scope = self.stack.pop()
    def free(self, scope):
        return scope.__joint__.free(scope)
    
class ClusterBuilder:
    def __init__(self, context=None, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs):
        self.context : Context = context
        self.scope = Cluster(Joint(pool=context, base=scope, tag=intents, layer=layer))
        self.layer : layers.common.layer = self.scope.__joint__.layer
        self.base = scope
        self.type = type
        self.intents = intents
        self.item = item
        self.helper = None
        self.name = None
        self.args = args
        self.kwargs = kwargs
        self.this = None
        self.context.take(self)        

    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__ {self.name}\n')

    def __call__(self, item):
        #print("ElementBuilder.__call___:",self.intents)
        # self.scope = Cluster(Joint(pool=self.context, base=self.base, tag=self.intents))
        #self.context.take(self)
        target, wrapper, helper, name = self.scope.__joint__.cluster_wrap(self.scope,item.__name__,item)
        self.item = item
        self.helper = helper
        self.wrapper = wrapper
        self.name = name
        self.context.drop(self)
        return self.scope 
    def __enter__(self) -> Scope:        
        return None
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def build(self):
        scope = self.scope
        item = self.item
        if type(self.type) is type:       
            this = self.type()     
        else:
            if type(item) is type:
                this = item()     
            else:
                this = item
        scope.__joint__.call2 = self.helper.wrapper
        scope.__joint__.call = self.wrapper
        scope.__joint__.this = this
        self.this = this
        attrs = self.kwargs.get('attrs',None)
        if attrs:
            scope.__dict__.update(attrs)
        setattr(scope.__joint__.base,self.name,scope)        
    def stage(self):
        pass

class ClusterDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        self.stack = []
    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__\n')
    def __call__(self, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs) -> ClusterBuilder:
        if scope is None:
            scope = self.scope()
        self.update(scope, closest_layer=layer)
        return ClusterBuilder(context=scope.__joint__.pool, scope=scope, type=type, intents=intents, item=item, layer=layer, *args, **kwargs)
    def __enter__(self) -> Scope:        
        self.stack.append(self.context.scope)
        return self.context.scope
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.scope = self.stack.pop()
    def free(self, scope):
        return scope.__joint__.free(scope)

class FeatureBuilder:
    def __init__(self, context=None, scope=None, host=None, type=None, intents=None, item=None, layer=None, overrides=None, *args, **kwargs):
        self.context : Context = context
        self.scope = Cluster(Joint(pool=context, base=scope, tag=intents, layer=layer, host=host, overrides=overrides))
        self.layer : layers.common.layer = self.scope.__joint__.layer
        self.base = scope
        self.type = type
        self.intents = intents
        self.item = item
        self.helper = None
        self.name = None
        self.args = args
        self.kwargs = kwargs
        self.this = None
        self.context.take(self)        

    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__ {self.name}\n')

    def __call__(self, item):
        #print("ElementBuilder.__call___:",self.intents)
        # self.scope = Cluster(Joint(pool=self.context, base=self.base, tag=self.intents))
        #self.context.take(self)
        target, wrapper, helper, name = self.scope.__joint__.feature_wrap(self.scope,item.__name__,item)
        self.item = item
        self.helper = helper
        self.wrapper = wrapper
        self.name = name
        self.context.drop(self)
        return self.scope 
    def __enter__(self) -> Scope:        
        return None
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def build(self):
        scope = self.scope
        item = self.item
        if type(self.type) is type:       
            this = self.type()     
        else:
            if type(item) is type:
                this = item()     
            else:
                this = item
        scope.__joint__.call2 = self.helper.wrapper
        scope.__joint__.call = self.wrapper
        scope.__joint__.this = this
        self.this = this
        attrs = self.kwargs.get('attrs',None)
        if attrs:
            scope.__dict__.update(attrs)
        setattr(scope.__joint__.base,self.name,scope)        
    def stage(self):
        pass

class FeatureDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        self.stack = []
    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__\n')
    def __call__(self, scope=None, host=None, type=None, intents=None, item=None, layer=None, overrides=None, *args, **kwargs) -> FeatureBuilder:
        if scope is None:
            scope = self.scope()
        self.update(scope, closest_layer=layer)
        return FeatureBuilder(context=scope.__joint__.pool, scope=scope, host=host, type=type, intents=intents, item=item, layer=layer, 
                                overrides=overrides, *args, **kwargs)
    def __enter__(self) -> Scope:        
        self.stack.append(self.context.scope)
        return self.context.scope
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.scope = self.stack.pop()
    def free(self, scope):
        return scope.__joint__.free(scope)

    
class RoutineBuilder:
    def __init__(self, context, scope, host, *args, **kwargs):
        self.context : Context = context
        self.scope : Scope = scope
        self.layer : layers.common.Layer = self.scope.__joint__.layer
        self.host = host
        self.args = args
        self.kwargs = kwargs
        self.context.head += 1
        pass
    def __call__(self, item):
        self.context.head -= 1
        self.wrapper = self.scope.__joint__.routine_wrap(self.scope, self.host, item.__name__, item, **self.kwargs)       
        self.layer.item_bind(self)
        if self.kwargs.get('implicit',False):
            self.wrapper(self.scope)
        return self.wrapper

      
class RoutineDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        pass
    def __call__(self, scope=None, host=None, *args, **kwargs):
        if scope is None:
            scope = element.scope()
        return RoutineBuilder(context=scope.__joint__.pool,scope=scope,host=host,*args,**kwargs)
    def free(self, scope):
        pass

class BindingBuilder:
    def __init__(self, context=None, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs):
        self.context : Context = context
        self.scope :Scope = scope
        self.layer : layers.common.Layer = self.scope.__joint__.layer
        self.base = scope 
        self.type = type
        self.intents = intents
        self.item = item
        self.helper = None
        self.name = None
        self.args = args
        self.kwargs = kwargs
        self.this = None
        self.context.take(self)
    def __call__(self, item):
        target, wrapper, helper, name = self.scope.__joint__.binding_wrap(self.scope,item.__name__,item)
        self.item = item
        self.helper = helper
        self.wrapper = wrapper
        self.name = name
        self.context.drop(self)
        return self.scope ### target            
    def __enter__(self) -> Scope:        
        self.layer.item_enter(self)
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.layer.item_leave(self)
    def stage(self):
        self.layer.item_stage(self)
    def build(self):
        scope = self.scope
        item = self.item
        helper = self.helper
        this = self.layer.item_build(self)
        scope.__joint__.this = this
        #scope.__joint__.call = self.wrapper
        #scope.__joint__.bond = self.wrapper
        scope.__joint__.bond = scope.__joint__.call2

class BindingDecorator(Decorator):
    def __init__(self, context, tag=None):                    
        Decorator.__init__(self,context,tag)
        self.stack = []
    #def __del__(self):        
    #    print(f'\n===> {type(self).__name__} __del__\n')
    def __call__(self, scope=None, type=None, intents=None, item=None, layer=None, *args, **kwargs) -> ElementBuilder:
        if scope is None:
            scope = self.scope()
        self.update(scope, closest_layer=layer)
        return BindingBuilder(context=self.context, scope=scope, type=type, intents=intents, item=item, layer=layer, *args, **kwargs)
    def __enter__(self) -> Scope:        
        self.stack.append(self.context.scope)
        return self.context.scope
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.scope = self.stack.pop()
    def free(self, scope):
        return scope.__joint__.free(scope)



def decorator_set(tag=None):
    context = Context(tag)
    element = ElementDecorator(context,tag)
    section = SectionDecorator(context,tag)
    cluster = ClusterDecorator(context,tag)
    feature = FeatureDecorator(context,tag)
    routine = RoutineDecorator(context,tag)
    binding = BindingDecorator(context,tag)
    return element, section, cluster, feature, routine, binding

element, section, cluster, feature, routine, binding = decorator_set('default')


'''
    [Scope]
    [Section]
    [Element]
    [Spawned]
    [Routine]
    Context
    Layer
    ElementDecorator.__call__ -> ElementBuilder
        EmentBuilder.__call__
            self.scope.__joint__.element_wrap :> istanza i wrappers
            self.context.drop(self)
                foreach builder in line:
                    builder.build() :>
                        layer.element_build
                        helper(...)  :> - generato in element_wrap
                                        - è la funzione originale, in caso il decoratore sia collegato ad una funzione,
                                        - se invece l'elemento decorato non è una funzione ma un oggetto...
                    builder.stage() :> ideato come supporto per propagare i layout del Tk senza doverli per forza rispecificare
'''


