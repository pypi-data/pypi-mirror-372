from .l01x0_common_layers import Layer
#from .. import gui
from ...helpers import signature
from ...gui import gui04x1_tkliterals as tkliterals
from ...gui import gui06x2_tktraits as tktraits
from ...gui import gui07x2_tktools as tktools
from ...gui import gui08x2_tktypes as tktypes
from ...gui import tkfonts as tkfonts
from ...gui.gui04x1_tkliterals import *
from ...gui import init, run, after

import sys 

class tklayout:
    class pack(signature): pass
    class grid(signature): pass
    class place(signature): pass

class tkinit(signature):
    default = ('', (), {})

class tkconfigure(signature):
    pass

class tkstyle(signature):
    default = ('', (), {})
    def configure(self, *args):
        style_name = self[1][0]
        for class_name in args:
            if not style_name.endswith(f'.{class_name}'):
                complete_name = f'{style_name}.{class_name}'
            else:
                complete_name = style_name
            tktypes.Style().configure(complete_name, *self[1][1:], **self[2])

class TkGuiLayer(Layer):
    def item_build(self, builder):
        scope = builder.scope
        this = None
        if type(builder.type) is type:
            if issubclass(builder.type,tktypes.Tool):  
                init_signature = builder.kwargs.get('init', None)
                method, args, kwargs = init_signature if init_signature is not None else tkinit.default
                if scope.__joint__.base.__joint__.tool is not None:
                    master = getattr(scope.__joint__.base.__joint__.tool,'interior_frame',None)
                    if master is None:
                        master = getattr(scope.__joint__.base.__joint__.tool,'client_frame',None)
                    if master is None:
                        master = scope.__joint__.base.__joint__.tool
                    this = builder.type(master, *args, **kwargs)
                else:
                    if issubclass(builder.type, tktypes.AppWindow): 
                        theme_signature = builder.kwargs.get('theme', None)
                        if theme_signature:
                            del builder.kwargs['theme']
                        this = init(*args, **kwargs)
                        if theme_signature:
                            if type(theme_signature) is str:
                                tktools.set_theme(theme_signature)
                    else:
                        this = builder.type(*args, **kwargs)
            else:
                init_signature = builder.kwargs.get('init', None)
                if init_signature:
                    method, args, kwargs = init_signature 
                    this = builder.type(*args, **args)
                else:
                    this = builder.type()
        else:
            if type(builder.item) is type:
                this = builder.item()     
        if this is None:
            this = builder.item
        if this is not None:
            if isinstance(this,tktypes.Tool):
                scope.__joint__.tool = this
            else:
                scope.__joint__.mass = this  
        return this

    def item_stage(self, builder):
        if type(builder.type) is type:
            if issubclass(builder.type,tktypes.Tool):
                this = builder.this
                style_signature = builder.kwargs.get('style', None)
                if style_signature is not None:                    
                    class_name = this.winfo_class()
                    if type(style_signature) is str:
                        style_name = style_signature
                        if style_name not in ('','.'):
                            if not style_name.endswith(f'.{class_name}'):
                                style_name = f'{style_name}.{class_name}'
                        else:
                            style_name = class_name
                    else:
                        method, args, kwargs = style_signature
                        if args:
                            style_name = args[0]
                            args = args[1:]
                        else:
                            style_name = this.winfo_name()
                        if not style_name.endswith(f'.{class_name}'):
                            style_name = f'{style_name}.{class_name}'
                        if args or kwargs:
                            tktypes.Style().configure(style_name,*args,**kwargs)
                    this.configure(style=style_name)

                cfg_sig = builder.kwargs.get('configure',None)
                if cfg_sig is None:
                    cfg_sig = builder.kwargs.get('config',None)
                if cfg_sig is not None:
                    method, args, kwargs = cfg_sig
                    this.configure(*args,**kwargs)

                self.item_bind(builder)
                '''
                bind_spec = builder.kwargs.get('bindings',None)
                if bind_spec is None:
                    bind_spec = builder.kwargs.get('bind',None)
                if bind_spec is not None:
                    if bind_spec[0]=='<':
                        builder.this.bind(bind_spec,lambda *a,scope=builder.scope,**b:builder.wrapper(scope,*a,**b))
                    else:                        
                        builder.this.configure(**{bind_spec:builder.wrapper})
                '''
                layout_signature = builder.kwargs.get('layout',None)
                if builder.context.stack:
                    if layout_signature is None:
                        layout_signature = builder.context.trail.get('layout',None)
                    else:
                        builder.context.trail['layout'] = layout_signature
                if layout_signature is not None:
                    method, args, kwargs = layout_signature
                    method_instance = getattr(builder.this,method)
                    method_instance(*args, **kwargs)
                    #print(layout)

    def item_bind(self, builder):
        scope = builder.scope
        joint = scope.__joint__
        this = joint.this        
        if isinstance(this,tktypes.Tool):
            bind_spec = builder.kwargs.get('bindings',None)
            if bind_spec is None:
                bind_spec = builder.kwargs.get('bind',None)
            if bind_spec is not None:
                if bind_spec[0]=='<':
                    this.bind(bind_spec,lambda *a,scope=scope,**b:builder.wrapper(scope,*a,**b))
                elif bind_spec[0]=='[' and bind_spec[-1]==']':
                    this.protocol(bind_spec[1:-1], lambda scope=scope:builder.wrapper(scope))
                else:                        
                    this.configure(**{bind_spec:builder.wrapper})


