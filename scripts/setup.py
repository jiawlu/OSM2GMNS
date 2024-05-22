from setuptools import setup, Extension

#  https://stackoverflow.com/questions/4529555/building-a-ctypes-based-c-library-with-distutils
from distutils.command.build_ext import build_ext as build_ext_orig
import os

# os.environ["CXX"] = "/opt/homebrew/Cellar/llvm/15.0.6/bin/clang++"



class build_ext(build_ext_orig):

    def build_extension(self, ext):
        self._ctypes = isinstance(ext, Extension)
        return super().build_extension(ext)

    def get_export_symbols(self, ext):
        if self._ctypes:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):
        if self._ctypes:
            return ext_name + '.pyd'
        return super().get_ext_filename(ext_name)


setup(
    py_modules = ["osm2gmns"],
    ext_modules=[
        Extension(
            "osm2gmns",
            # sources=["osm2gmns.cpp"],
            sources=["osm2gmns.cpp","networks.cpp","io.cpp","util_geo.cpp"],
            include_dirs=["/opt/homebrew/Cellar/libosmium/2.19.0/include",
                          "/opt/homebrew/Cellar/libosmium/2.19.0/libexec/include",
                          "/opt/homebrew/Cellar/expat/2.5.0/include",
                          "/opt/homebrew/opt/bzip2/include",
                          "/opt/homebrew/opt/zlib/include",
                          "/opt/homebrew/Cellar/geos/3.11.1/include",],
            library_dirs=["/opt/homebrew/Cellar/bzip2/1.0.8/lib",
                          "/opt/homebrew/opt/zlib/lib",
                          "/opt/homebrew/Cellar/expat/2.5.0/lib",
                          "/opt/homebrew/Cellar/geos/3.11.1/lib",],
            libraries=["expat", "bz2", "z", "geos_c"],
            extra_compile_args=['-std=c++17'],
        ),
    ],
    cmdclass={'build_ext': build_ext},
)