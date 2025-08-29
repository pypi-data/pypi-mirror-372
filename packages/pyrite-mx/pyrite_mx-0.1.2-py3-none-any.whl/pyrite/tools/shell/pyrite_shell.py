from pyrite.monolith import element, section, routine
from rich.console import Console
import threading
import time
import pyrite
import queue

@element()
def console(con):
    con.console = Console()
    def main(con=con):
        con.console.print('HELLO')
        while True:
            m = con.qin.get()
            match m:
                case 'print', args, kwargs:
                    con.console.print(*args,**kwargs) 
        pass
    con.thread = threading.Thread(target=main,args=(con,),daemon=True)
    con.qin = queue.Queue()
    @routine(con)
    def start(con):
        con.thread.start()
    @routine(con)
    def print(con, *args, **kwargs):
        con.qin.put(('print',args,kwargs))
        pass


console.start()
console.print('HELLO2')
time.sleep(3)
console.print('HELLO3')
time.sleep(3)
pass
