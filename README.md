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

## Documentation

For background information, installation instructions, and a tutorial, see [the docs](https://twhiteaker.github.io/CFGeom/).

You may also be interested in the [R reference implementation](https://github.com/dblodgett-usgs/NCDFSG).

## Contributors

* Tim Whiteaker
* Ben Koziol
* David Blodgett
