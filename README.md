# CFGeom

[![Build Status](https://travis-ci.org/twhiteaker/CFGeom.svg?branch=master)](https://travis-ci.org/twhiteaker/netCDF-CF-simple-geometry)

A Python Reference Implementation for Representing Geometries in NetCDF Following the CF Conventions

This project demonstrates how points, lines, polygons, and their multipart equivalents can be represented in NetCDF-CF. The project includes a Python reference implementation for reading and writing geometries in a netCDF file.

To view the geometries specification including examples, see [Chapter 7 of the
CF
Conventions](https://github.com/cf-convention/cf-conventions/blob/master/ch07.adoc#geometries).

## Use Cases

* Encode watershed model time series and polygons in a single file to archive model output and geometry.
* Encode a streamflow value for each river line in the conterminous U.S. at a given point in time.

## How To Use This Project

* To see full examples, view the [use case folders](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/use_cases).  Each folder includes a CDL file to demonstrate how to encode geometries. CDL files are text representations of the content of a netCDF file, and can be viewed with a text editor.
* For simplified examples demonstrating the various geometry types in CDL and netCDF format, see the [simplified examples folder](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/simplified_examples).  You'll find both CRA (contiguous ragged array for netCDF-3) and VLEN (variable length array for netCDF-4) examples.  Note that these examples are simplified in that they do not include data variables associated with the geometries, so they are not truly CF-compliant.
* To read and write geometries using Python, see the [reference implementation](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/cfgeom).

You may also be interested in the [R reference implementation](https://github.com/dblodgett-usgs/NCDFSG).



## Contributors

* Tim Whiteaker
* Ben Koziol
* David Blodgett
