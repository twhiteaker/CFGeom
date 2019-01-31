# CFGeom

[![Build
Status](https://travis-ci.org/twhiteaker/CFGeom.svg?branch=master)](https://travis-ci.org/twhiteaker/CFGeom)
[![Coverage Status](https://codecov.io/gh/twhiteaker/CFGeom/branch/master/graph/badge.svg)](https://codecov.io/gh/twhiteaker/CFGeom)

A Python Reference Implementation for Representing Geometries in NetCDF Following the CF Conventions

This project demonstrates how points, lines, polygons, and their multipart equivalents can be represented in NetCDF-CF. The project includes a Python reference implementation for reading and writing geometries in a netCDF file.

For more on this project, see the [documentation](https://twhiteaker.github.io/CFGeom/), or get started with the [tutorial](https://twhiteaker.github.io/CFGeom/tutorial.html).

To view the geometries specification including examples, see [Chapter 7 of the
CF
Conventions](https://github.com/cf-convention/cf-conventions/blob/master/ch07.adoc#geometries).

You may also be interested in the [R reference implementation](https://github.com/dblodgett-usgs/NCDFSG).


## Use Cases

* Encode watershed model time series and polygons in a single file to archive model output and geometry.
* Encode a streamflow value for each river line in the conterminous U.S. at a given point in time.

## Contributors

* Tim Whiteaker
* Ben Koziol
* David Blodgett
