from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import setuptools
import numpy as np
import platform

# Add debugging information
print(f"sys.path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Environment variables:")
for k, v in os.environ.items():
    if 'ARM' in k.upper() or 'INCLUDE' in k.upper() or 'LIB' in k.upper():
        print(f"  {k}: {v}")

__version__ = '0.7.0'

# Detect platform
is_windows = sys.platform.startswith('win')

# Prepare environment for compilation
include_dirs = [
    "pybind11/include",
    "carma/include",
    "/usr/include",  # For Linux
    "src",
    np.get_include(),  # Add NumPy include directory explicitly
]

# Print NumPy include path for debugging
print(f"NumPy include path: {np.get_include()}")

# Check for Armadillo from environment variables
armadillo_include = os.environ.get('ARMADILLO_INCLUDE_DIR', '').strip()  # Strip any trailing spaces
if armadillo_include:
    include_dirs.append(armadillo_include)
    print(f"Using Armadillo include dir from environment: {armadillo_include}")
else:
    # Try to use hardcoded paths
    if platform.system() == 'Windows':
        include_dirs.append(os.path.join('C:', os.sep, 'armadillo', 'include'))
        print(f"Using hardcoded Windows Armadillo include path")

# Check for Windows platform and skip Armadillo linking if requested
libraries = []
library_dirs = []

# Check if we should skip armadillo linking on Windows
skip_linking = platform.system() == 'Windows' and os.environ.get('SKIP_ARMADILLO_LINKING', '').strip() == '1'
use_openblas = platform.system() == 'Windows' and os.environ.get('USE_OPENBLAS', '').strip() == '1'

if platform.system() == 'Windows' and not skip_linking:
    # Only add armadillo to libraries if not skipping
    libraries.append('armadillo')
    
    # Ensure proper path format with backslash after C:\
    lib_path = os.path.join('C:', os.sep, 'armadillo', 'lib')
    library_dirs.append(lib_path)
    print(f"Using hardcoded Windows Armadillo lib path: {lib_path}")
elif skip_linking and use_openblas:
    # Add OpenBLAS for Windows build
    blas_dir = os.environ.get('BLAS_LAPACK_DIR', '').strip()
    if blas_dir:
        print(f"Using OpenBLAS from {blas_dir}")
        library_dirs.append(blas_dir)
        libraries.append('openblas')
    else:
        print("BLAS_LAPACK_DIR environment variable not set. Searching for OpenBLAS...")
        openblas_dir = os.environ.get('OPENBLAS_HOME', '').strip()
        if openblas_dir:
            # Look for .lib files in the openblas directory recursively
            for root, dirs, files in os.walk(openblas_dir):
                for file in files:
                    if file.endswith('.lib'):
                        lib_dir = os.path.dirname(os.path.join(root, file))
                        library_dirs.append(lib_dir)
                        lib_name = os.path.splitext(file)[0]
                        libraries.append(lib_name)
                        print(f"Found OpenBLAS library: {lib_name} in {lib_dir}")
                        break
                if libraries:  # Stop if we found libraries
                    break
elif skip_linking:
    print("Skipping Armadillo linking and library setup due to SKIP_ARMADILLO_LINKING=1")
elif platform.system() != 'Windows':
    # For Linux/Unix systems, add BLAS and LAPACK libraries
    libraries.extend(['armadillo', 'blas', 'lapack'])
    print("Adding blas and lapack libraries for Linux/Unix")

# Define macros - removed flags that disable BLAS/LAPACK
define_macros = [
    # Keep only necessary macros, remove those that disable BLAS/LAPACK
    ("ARMA_USE_EXTERN_CXX11_RNG", "1"),
]

# Print the macros for debugging
print(f"Define macros: {define_macros}")

# Add platform-specific environment-controlled macros
if platform.system() == 'Windows':
    for env_var in ['ARMA_USE_EXTERN_CXX11_RNG']:
        if os.environ.get(env_var, '').strip() == '1':
            print(f"Ensuring macro {env_var}=1 is defined based on environment variable")

print(f"Final libraries list: {libraries}")
print(f"Final library_dirs list: {library_dirs}")

# Define the extension module
ext_modules = [
    Extension(
        'tlars.tlars_cpp',
        ['src/tlars_cpp_pybind.cpp', 'src/tlars_cpp.cpp'],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        define_macros=define_macros,
        language='c++'
    ),
]

# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    import os
    with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False) as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True

# A custom build extension for dealing with C++14 compiler requirements
class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc', '/std:c++14'],  # Use MSVC standard flag instead of GCC
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append('-std=c++14')
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO="%s"' % self.distribution.get_version())
            
            # Add Windows-specific flags for Armadillo - keeping only the necessary ones
            if os.environ.get('ARMA_USE_EXTERN_CXX11_RNG', '').strip() == '1':
                opts.append('/DARMA_USE_EXTERN_CXX11_RNG')
            
            # Debugging information for Windows
            print(f"Compiler type: {ct}")
            print(f"Compiler flags: {opts}")
            print(f"Link flags: {link_opts}")
        
            # Special handling for Windows when SKIP_ARMADILLO_LINKING=1
            if os.environ.get('SKIP_ARMADILLO_LINKING', '').strip() == '1':
                print("Windows build with SKIP_ARMADILLO_LINKING=1, removing armadillo from libraries")
                # Force remove armadillo from all extensions
                for ext in self.extensions:
                    if 'armadillo' in ext.libraries:
                        ext.libraries.remove('armadillo')
                        print(f"Removed armadillo from {ext.name} libraries: {ext.libraries}")
            
            # Add OpenBLAS flags if needed
            if os.environ.get('USE_OPENBLAS', '').strip() == '1':
                opts.append('/DARMA_USE_BLAS')
                opts.append('/DARMA_USE_LAPACK')
        
        for ext in self.extensions:
            ext.extra_compile_args = opts.copy()
            ext.extra_link_args = link_opts.copy()
            
            # Don't make any assumptions about STD_MUTEX
            # Just keep the macros as they are defined
            ext.define_macros = [(name, value) for name, value in ext.define_macros]
            
            # Print extension information for Windows
            if ct == 'msvc':
                print(f"Extension {ext.name} include_dirs: {ext.include_dirs}")
                print(f"Extension {ext.name} library_dirs: {ext.library_dirs}")
                print(f"Extension {ext.name} libraries: {ext.libraries}")
                print(f"Extension {ext.name} define_macros: {ext.define_macros}")
                
        build_ext.build_extensions(self)

setup(
    name='tlars',
    version=__version__,
    author='Arnau Vilella',
    author_email='avp@connect.ust.hk',
    url='https://github.com/ArnauVilella/tlars-python',
    description='Python port of the tlars R package by Jasin Machkour',
    long_description='',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.6.0', 'numpy', 'matplotlib>=3.3.0'],
    setup_requires=['pybind11>=2.6.0', 'numpy', 'matplotlib>=3.3.0'],
    cmdclass={'build_ext': BuildExt},
    packages=['tlars'],
    zip_safe=False,
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
)
