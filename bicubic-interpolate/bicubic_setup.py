from distutils.core import setup, Extension
import os
import subprocess
import numpy as np

cmd = "conda info | grep 'active env location'"
ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
conda_path = ps.communicate()[0].decode("utf-8").split()[4]
this_dir = os.path.dirname(os.path.abspath(__file__))

if os.name == 'nt':
    # Windows
    include_dirs = [
        conda_path + '/Library/include',
        np.get_include()
    ]
    library_dirs = [
        conda_path + '/Library/lib',
        conda_path + '/Library/bin'
    ]
    libraries = [
    ]
elif os.name == 'posix':
    include_dirs = [
        conda_path + '/include',
        np.get_include()
    ]
    library_dirs = [
        conda_path + '/Library/lib'
    ]
    libraries = [
    ]

os.environ["CC"] = "g++"
module_bicubic = Extension(
    '_bicubic',
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries = libraries,
    sources=[
        'bicubic.cpp'
    ],
    extra_compile_args=['-std=c++11']
)

setup(name='_bicubic', ext_modules=[module_bicubic])
