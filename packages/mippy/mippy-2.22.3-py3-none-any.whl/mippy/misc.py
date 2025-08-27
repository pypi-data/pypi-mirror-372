# Generic functions for MIPPY windows that don't fit anywhere else

import multiprocessing
from colorama import init
from termcolor import colored
init()  # Using colorama to make termcolor work on Windows

def optionmenu_patch(om, var):
        menu = om['menu']
        last = menu.index("end")
        for i in range(0, last+1):
                menu.entryconfig(i, variable=var)

# from collections import Mapping, Container
# from sys import getsizeof

# Generate threading lock for critical print code
lock = multiprocessing.Lock()


"""
Think this section of code is redundant? Commented out to test.
"""
# def deep_getsizeof(o, ids): 
#         # From https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
#         """Find the memory footprint of a Python object

#         This is a recursive function that drills down a Python object graph
#         like a dictionary holding nested dictionaries with lists of lists
#         and tuples and sets.

#         The sys.getsizeof function does a shallow size of only. It counts each
#         object inside a container as pointer only regardless of how big it
#         really is.

#         :param o: the object
#         :param ids:
#         :return:
#         """
#         d = deep_getsizeof
#         if id(o) in ids:
#                 return 0

#         r = getsizeof(o)
#         ids.add(id(o))

#         if isinstance(o, str) or isinstance(0, str):
#                 return r

#         if isinstance(o, Mapping):
#                 return r + sum(d(k, ids) + d(v, ids) for k, v in o.items())

#         if isinstance(o, Container):
#                 return r + sum(d(x, ids) for x in o)

#         return r
        
# def getsizeof(an_object):
#         from pympler import asizeof
#         return asizeof.asizeof(an_object)

def cprint(*strings,**keyargs):
        # Automatically prints coloured strings for errors and warnings
        strings = list(map(str,strings))
        if str(strings[0]).startswith("INFO:"):
                print(colored(' '.join(strings),'cyan'),**keyargs)
        elif str(strings[0]).startswith("WARNING:"):
                print(colored(' '.join(strings),'yellow'),**keyargs)
        elif str(strings[0]).startswith("ERROR:"):
                print(colored(' '.join(strings),'white','on_red'),**keyargs)
        elif str(strings[0]).startswith("DONE:"):
                print(colored(' '.join(strings),'green'),**keyargs)
        elif str(strings[0]).startswith("=="):
                print(colored(' '.join(strings),'black','on_magenta'),**keyargs)
        else:
                print(' '.join(strings),**keyargs)
        # print(colored('','white','on_black'),end='')
        return