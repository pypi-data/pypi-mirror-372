from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from subprocess import check_output, PIPE, call, Popen
import json
import sys
import urllib
from urllib import request
from urllib import error as urlerror
import os
import platform
from psutil import cpu_count, virtual_memory, swap_memory
from .misc import cprint
from math import sqrt
#from mippy import FROZEN

def launch_mippy(skip_update=False):
        # Set environment variable to limit numpy OpenBLAS threads on high CPU
        # count machines with low RAM. Takes square root of 2x total RAM in GB
        # as max number of threads for numpy. If this is less that CPU count
        # then this is limit, otherwise CPU count is used as the limit
        total_memory = virtual_memory().total
        max_threads_mem = int(round(sqrt(total_memory*2//(1024*1024*1024))))
        if max_threads_mem == 0:
            max_threads_mem = 1
        max_threads_cpu = int(cpu_count())+1
        if max_threads_mem<max_threads_cpu:
            cprint("WARNING: NUMPY threads limited by available RAM")
            threads=max_threads_mem
        else:
            threads=max_threads_cpu
        cprint("INFO: Limiting NumPy to {} threads".format(threads))
        os.environ["OMP_NUM_THREADS"] = "{}".format(threads)
        os.environ["OPENBLAS_NUM_THREADS"] = "{}".format(threads)
        os.environ["MKL_NUM_THREADS"] = "{}".format(threads)
        os.environ["VECLIB_MAXIMUM_THREADS"] = "{}".format(threads)
        os.environ["NUMEXPR_NUM_THREADS"] = "{}".format(threads)



        import mippy.splash as splash
        from pkg_resources import resource_filename
        try:
            splashimage = resource_filename('mippy','resources/splash3.jpg')
        except TypeError:
            # Pyinstaller frozen
            splashimage = os.path.join(os.path.dirname(sys.executable),'mippy','resources','splash3.jpg')

        root_window = Tk()
        with splash.SplashScreen(root_window,splashimage,3.0):
                urlobj = None

                if not skip_update:
                    # Test if PyPI is accessible
                    try:
                        urlobj = request.urlopen('https://pypi.org')
                    except urlerror.URLError:
                        # PyPI not accessible - probably no internet connection...
                        print("Unable to access PyPI - skipping update check...")
                        pass
                    except:
                        raise

                # Check for new version of MIPPY on PyPI
                if not urlobj is None:
                    print('Checking for updates to MIPPY on PyPI...')
                    if 'win' in sys.platform and not 'darwin' in sys.platform:
                        ver = platform.python_version()
                        print("Python ".format(ver))
                        pip_output = check_output([sys.executable,'-m','pip','list','--outdated','--format=json','--disable-pip-version-check'])
                    else:
                        # # Account for dual install of python (2) and python3 on nix systems
                        # this_pip = 'pip3'
                        pip_output = check_output([sys.executable,'-m','pip','list','--outdated','--format=json','--disable-pip-version-check'])
                    if 'mippy' in [row['name'] for row in json.loads(pip_output)]:
                            print("Warning! Outdated version of MIPPY detected!")
                            print("Updated version found")
                            update = messagebox.askyesno("Update available","An update for MIPPY is available from PyPI.  Would you like to install?")
                            if update:
                                    #~ call('pip install mippy --upgrade',shell=True)
                                    if 'win' in sys.platform and not 'darwin' in sys.platform:
                                        # ver = platform.python_version()
                                        try:
                                            p = Popen([sys.executable,'-m','pip','install','mippy','--upgrade','--no-cache-dir','--disable-pip-version-check'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
                                        except:
                                            p = Popen([sys.executable,'-m','pip','install','mippy','--upgrade','--no-cache-dir','--user','--disable-pip-version-check'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
                                    else:
                                        p = Popen([sys.executable,'-m','pip','install','mippy','--upgrade','--no-cache-dir','--user','--disable-pip-version-check'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
                                    output,err = p.communicate()
                                    rc = p.returncode
                                    if len(err)>0:
                                            print(err.decode("utf-8"))
                                    if rc==0:
                                            print("MIPPY updated")
                                            messagebox.showinfo("MIPPY Updated","Update successful! Please restart MIPPY.")
                                    else:
                                            print("Problem occurred...")
                                            messagebox.showwarning("Oops","Something went wrong. Please restart MIPPY.")
                                    sys.exit()
                    else:
                        print('No new version found.')

                from mippy.application import MIPPYMain
                root_app = MIPPYMain(master = root_window)
        root_app.mainloop()




if __name__=='__main__':
        launch_mippy()
        #~ from tkinter import *
        #~ from tkinter.ttk import *


        #~ import mippy.splash as splash
        #~ from pkg_resources import resource_filename
        #~ splashimage = resource_filename('mippy','resources/splash3.jpg')
        #~ root_window = Tk()
        #~ with splash.SplashScreen(root_window,splashimage,3.0):

                #~ # Check for new version of MIPPY on PyPI
                #~ p - Popen(['program','arg'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
                #~ output,err = p.communicate(b'pip list --outdated')
                #~ rc = p.returncode
                #~ print(output)

                #~ from mippy.application import MIPPYMain
                #~ root_app = MIPPYMain(master = root_window)
        #~ root_app.mainloop()
