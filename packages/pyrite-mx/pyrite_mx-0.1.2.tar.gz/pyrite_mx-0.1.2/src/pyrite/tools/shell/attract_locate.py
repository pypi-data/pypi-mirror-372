from pyrite.attract import locate
import clipboard as cb
from sys import argv
import argparse

def main():
    parser = argparse.ArgumentParser("attract-locate.py")
    parser.add_argument("item", help="Item name fragment", type=str)
    g0 = parser.add_mutually_exclusive_group()
    g0.add_argument("--verbose", "-v", help="Verbose output", action='store_true')
    g0.add_argument("--silent", "-s", help="Silent. No output to stdout", action='store_true')
    parser.add_argument("--clipboard", "-c", help="Copy results to clipboard", action='store_true')
    parser.add_argument("--resolve-links", "-r", help="Resolve links", action='store_true')
    g1 = parser.add_mutually_exclusive_group()
    g1.add_argument("--posix-path", "-p", help="Posix pathname", action='store_true')
    g1.add_argument("--unc-path", "-u", help="UNC pathname", action='store_true')
    g1.add_argument("--wsl-path", "-w", help="WSL pathname", action='store_true')
    args = parser.parse_args()
    result = locate(args.item,options=['resolve_links' if args.resolve_links else None]) 
    if result is None:
        if not args.silent:
            if args.verbose:
                print(f'[E1]attract-locate: "{args.item}" not found.')
        exit(1)
    if args.posix_path:
        result = result.replace('\\','/')    
    elif args.unc_path:
        result = result.replace('/','\\')    
    elif args.wsl_path:
        result = result.replace("\\","/")
        result = f'/mnt/{result[0].lower()}{result[2:]}'
    if not args.silent:
        if args.verbose:
            print(f'[OK]attract-locate: "{result}" found with "{args.item}"')
        print(result)
    if args.clipboard:
        cb.copy(result)

#main()