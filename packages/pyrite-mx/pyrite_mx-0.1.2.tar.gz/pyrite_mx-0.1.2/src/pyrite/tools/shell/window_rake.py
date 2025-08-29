from pyrite.gui import tools, wintools, winapi
import rich
from rich.table import Table
import re
import sys
import argparse

def main():    
    winapi.CoInitialize() # needed for wintools.hwnd_system_app_user_model_id_get(w.hwnd)
    parser = argparse.ArgumentParser("window-rake.py")
    parser.add_argument("--title", "-t", help="Item name fragment", type=str)
    parser.add_argument("--pname", "-n", help="Item name fragment", type=str)
    parser.add_argument("--pexe", "-x", help="Item name fragment", type=str)
    parser.add_argument("--cmdline", "-c", help="Item name fragment", type=str)
    args = parser.parse_args()
    arg_list = ['title','pname','pexe','cmdline']
    print(f'--title=[{args.title.__repr__()}]', file=sys.stderr)
    wl = tools.rake_windows(**{k:args.__dict__[k] for k in arg_list if args.__dict__[k] is not None})
    if wl:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Z", style="dim")
        #table.add_column("alias")
        table.add_column("scode", overflow="fold")
        table.add_column("title", overflow="fold")
        table.add_column("model", overflow="fold")
        table.add_column("pname", overflow="fold")
        table.add_column("cmdline", overflow="fold")
        table.add_column("id")
        table.add_column("pid")
        table.add_column("class", overflow="fold")
        for w in wl:
            scode = w.spread_code_guess(options="complete")
            table.add_row(
                w.ztag, #w.w_shortcut, 
                scode, 
                w.title.encode('unicode_escape').decode(), 
                wintools.hwnd_system_app_user_model_id_get(w.hwnd), 
                w.pname, 
                ' '.join(w.pcmdline),
                str(w.hwnd), 
                str(w.pid),
                w.classname
            )
        rich.print(table)


if __name__ == '__main__':
    main()
    