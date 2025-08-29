
class signature(tuple):
    def __new__(cls, *args, **kwargs):
        return super().__new__( cls, (cls.__name__, args, kwargs) )
    def __init__(self, *args, **kwargs):
        super().__init__()
