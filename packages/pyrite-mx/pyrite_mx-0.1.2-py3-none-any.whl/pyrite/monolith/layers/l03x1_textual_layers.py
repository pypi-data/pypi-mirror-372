from ...helpers import signature
from .l01x0_common_layers import Layer
from textual.message_pump import MessagePump
from textual.widget import Widget
import asyncio
import types
import copy
import inspect
import functools

class textualinit(signature):
    default = ('', {})

'''
class TextualShellLayer(Layer):
    class GeneratorOverride:
        def __init__(self, scope, target):
            functools.update_wrapper(self,target)
            self.scope=scope
            self.target=target
            sig = inspect.signature(self) #sig = inspect.signature(target)
            params = list(sig.parameters.items())
            params.pop(1)
            sig1 = sig.replace(parameters=[b for a,b in params])
            self.__signature__ = sig1
            for k,v in target.__dict__.items():
                if k.startswith('_textual'):
                    setattr(self,k,v)
            #self.__positional_argument_count__ = sum(1 for param in sig1.parameters.values() if param._default == inspect._empty)-1
            self.__positional_argument_count__ = self.target.__code__.co_argcount - 2
            if self.target.__defaults__:
                self.__positional_argument_count__ -= len(self.target.__defaults__)
            pass
        def __get__(self,obj,cls):
            return types.MethodType(self,obj)     
        def __call__(self,instance,*args,**kwargs):
            yield from self.target(instance,self.scope,*args[:self.__positional_argument_count__],**kwargs)
    class MethodOverride:
        def __init__(self, scope, target):
            functools.update_wrapper(self,target)
            self.scope=scope
            self.target=target
            sig = inspect.signature(self) #sig = inspect.signature(target)
            params = list(sig.parameters.items())
            params.pop(1)
            sig1 = sig.replace(parameters=[b for a,b in params])
            self.__signature__ = sig1
            for k,v in target.__dict__.items():
                if k.startswith('_textual'):
                    setattr(self,k,v)
            #self.__positional_argument_count__ = sum(1 for param in sig1.parameters.values() if param._default == inspect._empty)-1
            self.__positional_argument_count__ = self.target.__code__.co_argcount - 2
            if self.target.__defaults__:
                self.__positional_argument_count__ -= len(self.target.__defaults__)
            pass
        def __get__(self,obj,cls):
            return types.MethodType(self,obj)     
        def __call__(self,instance,*args,**kwargs):
            return self.target(instance,self.scope,*args[:self.__positional_argument_count__],**kwargs)


    def item_build(self, builder):
        scope = builder.scope
        this = None 
        if builder.type is not None and (issubclass(builder.type, Widget) or type(builder.type) is type):
            init = builder.kwargs.get('init', None)
            if init is not None:
                if type(init) is textualinit:
                    method, argp, args = init 
                elif type(init) is tuple:
                    method, args = init 
                elif type(init) is dict:
                    args = init
                this = builder.type(**args)
            else:
                this = builder.type()
        else:
            if isinstance(builder.item, types.FunctionType):
                pass
            elif issubclass(builder.item, Widget):
                def Caller_fn(self):
                    pass
                class Caller:
                    def __init__(self):
                        functools.update_wrapper(self,Caller_fn)
                        #self.__signature__ = inspect.signature(Caller_fn).replace()
                        #self.__qualname__ = 'Caller'
                        pass
                    def __get__(self,obj,cls):
                        return types.MethodType(self,obj)     
                    def __call__(self, *args, **kwds):
                        pass
                class WidgetOverride(builder.item):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                    aaa_caller = Caller()
                    pass
                #WidgetOverride = builder.item

                all_methods = inspect.getmembers(builder.item, predicate=inspect.isfunction)                    
                # Get methods defined in the class itself
                class_methods = {name: method for name, method in all_methods if method.__qualname__.startswith(builder.item.__qualname__ + '.')}

                dh = builder.item.__dict__.get('_decorated_handlers',None)
                if dh:
                    dh=copy.deepcopy(dh)
                for method_name in class_methods:
                    method = getattr(WidgetOverride,method_name,None)
                    if method is not None:
                        if method_name.startswith('_'):
                            continue
                        if method_name in ('compose'):
                            wrapper = TextualShellLayer.GeneratorOverride(scope,method)
                        else:
                            wrapper = TextualShellLayer.MethodOverride(scope,method)
                        setattr(WidgetOverride,method_name,wrapper)                       
                        if dh:
                            for k,v in dh.items():
                                for i, h in enumerate(v):
                                    m, _ = h
                                    if m is method:
                                        v[i] = (wrapper,_)
                if dh:
                    setattr(WidgetOverride,'_decorated_handlers',dh)
                
                init = builder.kwargs.get('init', None)
                if init is not None:
                    if type(init) is tuple:
                        method, args = init 
                    elif type(init) is dict:
                        args = init
                    this = WidgetOverride(**args)
                else:
                    this = WidgetOverride()
                pass
            elif type(builder.item) is type:
                init = builder.kwargs.get('init', None)
                if init is not None:
                    if type(init) is tuple:
                        method, args = init 
                    elif type(init) is dict:
                        args = init
                    this = builder.item(**args)
                else:
                    this = builder.item()
        if this is None:
            this = builder.item
        if this is not None:
            if isinstance(this,Widget):
                scope.__joint__.tool = this
            else:
                scope.__joint__.mass = this  
        return this
'''

class TextualShellLayer(Layer):
    def item_build(self, builder):
        scope = builder.scope
        this = None 
        if builder.type is not None and (issubclass(builder.type, MessagePump) or type(builder.type) is type):
            init = builder.kwargs.get('init', None)
            if init is not None:
                if type(init) is textualinit:
                    method, argp, args = init 
                elif type(init) is tuple:
                    method, args = init 
                elif type(init) is dict:
                    args = init
                this = builder.type(**args)
            else:
                this = builder.type()
        else:
            if isinstance(builder.item, types.FunctionType):
                pass
            elif issubclass(builder.item, MessagePump):
                init = builder.kwargs.get('init', None)
                if init is not None:
                    if type(init) is tuple:
                        method, args = init 
                    elif type(init) is dict:
                        args = init
                    this = builder.item(**args)
                else:
                    this = builder.item()
                pass
            elif type(builder.item) is type:
                init = builder.kwargs.get('init', None)
                if init is not None:
                    if type(init) is tuple:
                        method, args = init 
                    elif type(init) is dict:
                        args = init
                    this = builder.item(**args)
                else:
                    this = builder.item()
        if this is None:
            this = builder.item
        if this is not None:
            if isinstance(this,MessagePump):
                scope.__joint__.tool = this
            else:
                scope.__joint__.mass = this  
        return this

class TextualCompositionLayer(TextualShellLayer):
    def __init__(self):
        self.build_list = []
        self.stack = []
        self.composition = True
        self.last_list_id = 0
    def __enter__(self):
        self.composition = True
        return super().__enter__()
    def item_build(self, builder):
        e = super().item_build(builder)
        if e is builder.scope.__joint__.tool:
           self.build_list.append(e)
        return e
    def item_enter(self, builder):
        if builder.this is builder.scope.__joint__.tool:
            self.stack.append(self.build_list)        
            self.build_list = []
    def item_leave(self, builder):
        if builder.this is builder.scope.__joint__.tool:
            l = self.build_list
            self.build_list = self.stack.pop()
            if l:
                self.build_list[-1] = (self.build_list[-1],l)
    def drop(self):
        blist = self.build_list
        self.build_list = []
        self.composition = False
        def walker(l):
            for x in l:
                if type(x) is tuple:
                    xi, xl = x
                    with xi:
                        yield from walker(xl)
                else:
                    yield x
        yield from walker(blist)

    def __iter__(self):
        yield from self.drop()              

    def item_stage(self, builder):
        if self.composition:
            return
        if id(self.build_list) == self.last_list_id:
            return
        pass
        self.last_list_id = id(self.build_list)
        widget = builder.scope.__joint__.this
        container = builder.scope.__joint__.base.__joint__.this
        loop : asyncio.AbstractEventLoop  = container.screen.app._loop
        async def mount(self, builder, container:Widget):
            async def walker(c:Widget, l):
                for x in l:
                    if type(x) is tuple:
                        xi, xl = x
                        result1 = await c.mount(xi)                        
                        result2 = await walker(xi, xl)
                    else:
                        result3 = await c.mount(x)
            blist = self.build_list
            self.build_list = []
            result = await walker(container, blist)
            
        #loop.call_soon_threadsafe(mount, self, builder, container, widget)
        future = asyncio.run_coroutine_threadsafe(mount(self, builder, container),loop)
        ## result = future.result()  # questo fucnziona solo se il thread del loop non è il thread corrente, cosa che invece pare che sia
        pass


  
