import re
import setuptools


def get_version():
    VERSIONFILE = 'cfgeom/_version.py'
    with open(VERSIONFILE, 'rt') as fh:
        verstrline = fh.read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        m = 'Unable to find version string in %s.' % (VERSIONFILE,)
        raise RuntimeError(m)
    return verstr


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cfgeom',
    version=get_version(),
    author='TIm Whiteaker',
    author_email='whiteaker@utexas.edu',
    packages=setuptools.find_packages(),
    scripts=[],
    url='https://github.com/twhiteaker/CFGeom',
    license='LICENSE',
    description='Reference implementation for representing geometries in NetCDF with the CF Conventions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'shapely >= 1.6.4.post1',
        'numpy >= 1.9.3',
        'netcdf4 >= 1.0.8',
    ],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
