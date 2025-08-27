# from setuptools import setup
from Cython.Build import cythonize

# setup(
#     ext_modules=cythonize("./utils.pyx"),)

# 命令行：python setup.py build_ext --inplace

from distutils.core import setup
# from distutils.extension import Extension
# from Cython.Distutils import build_ext
import numpy as np

setup(
    ext_modules=cythonize("./utils.pyx"),
    include_dirs=[np.get_include()])
