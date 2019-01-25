from distutils.core import setup

setup(
    name='CFGeom',
    version='0.2.0',
    author='TIm Whiteaker',
    author_email='whiteaker@utexas.edu',
    packages=['cfgeom', 'cfgeom.test'],
    scripts=['bin/json_to_examples.py'],
    url='http://pypi.python.org/pypi/CFGeom/',
    license='LICENSE',
    description='Reference implementation for representing geometries in NetCDF with the CF Conventions',
    long_description=open('README.md').read(),
    install_requires=[
        'shapely >= 1.6.4.post1',
        'netcdf4 >= 1.0.8',
    ],
)
