
# layer or tier?

class Layer:
    def __init__(self):
        pass
    def item_build(self, builder):
        pass
    def item_stage(self, builder):
        pass
    def item_bind(self, builder):
        pass
    def item_enter(self, builder):
        pass
    def item_leave(self, builder):
        pass
    def __enter__(self): 
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CommonLayer(Layer):
    def item_build(self, builder):
        this = None 
        if type(builder.type) is type:
            init = builder.kwargs.get('init', None)
            if init:
                method, args = init 
                this = builder.type(**args)
            else:
                this = builder.type()
        else:
            if type(builder.item) is type:
                this = builder.item()     
        return this
