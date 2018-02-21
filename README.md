[![Build Status](https://travis-ci.org/twhiteaker/netCDF-CF-simple-geometry.svg?branch=master)](https://travis-ci.org/twhiteaker/netCDF-CF-simple-geometry)

# netCDF-CF-simple-geometry

A Python Reference Implementation for Representing Geometries in NetCDF Following the CF Conventions

This project demonstrates how points, lines, polygons, and their multipart equivalents can be represented in NetCDF-CF. The project includes a Python reference implementation for reading and writing geometries in a netCDF file.

To view the geometries specification including examples, see the [Geometries section in Dave Blodgett's fork of the CF Conventions](https://github.com/dblodgett-usgs/cf-conventions/blob/master/ch07.adoc#geometries).

## Scope

* Implemented in CF 1.8 to include _geometries_ of types point, line, and polygon.
* Limited to linear connections between nodes in the coordinate reference system the nodes are defined in.
* Allows geometries to be attached to a Discrete Sampling Geometry (DSG) _instance_ variable.
* Demonstrates use of enhanced netCDF-4 capabilities for inclusion in CF 2.0.

## Use Cases

* Encode watershed model time series and polygons in a single file to archive model output and geometry.
* Encode a streamflow value for each river line in the conterminous U.S. at a given point in time.

## How To Use This Project

* To see full examples, view the [use case folders](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/use_cases).  Each folder includes a CDL file to demonstrate how to encode geometries. CDL files are text representations of the content of a netCDF file, and can be viewed with a text editor.
* For simplified examples demonstrating the various geometry types in CDL and netCDF format, see the [simplified examples folder](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/simplified_examples).  You'll find both CRA (contiguous ragged array for netCDF-3) and VLEN (variable length array for netCDF-4) examples.  Note that these examples are simplified in that they do not include data variables associated with the geometries, so they are not truly CF-compliant.
* For additional simplified examples in CDL, see [the wiki](https://github.com/twhiteaker/netCDF-CF-simple-geometry/wiki).
* To read and write geometries using Python, see the [reference implementation](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/src/python/ncgeom).

You may also be interested in the [R reference implementation](https://github.com/dblodgett-usgs/NCDFSG).

---

## Example: Polygons in a NetCDF-3 timeSeries featureType File

Below is sample CDL demonstrating how multipolygons with holes can be encoded in CF-compliant NetCDF-3 using a contiguous ragged array-like encoding. The example includes two polygons. The first polygon is a multipart feature with two triangles, with a triangular hole in the first part.  The second polygon is a single triangle.

```
netcdf multipolygon_example {
dimensions:
  node = 12 ;
  instance = 2 ;
  part = 4 ;
  time = 4 ;
variables:
  int time(time) ;
    time:units = "days since 2000-01-01" ;
  double x(node) ;
    x:units = "degrees_east" ;
    x:standard_name = "longitude" ;
    x:axis = "X" ;
  double y(node) ;
    y:units = "degrees_north" ;
    y:standard_name = "latitude" ;
    y:axis = "Y" ;
  double lat(instance) ;
    lat:units = "degrees_north" ;
    lat:standard_name = "latitude" ;
  double lon(instance) ;
    lon:units = "degrees_east" ;
    lon:standard_name = "longitude" ;
  float geometry_container ;
    geometry_container:geometry_type = "polygon" ;
    geometry_container:node_count = "node_count" ;  // variable counting nodes per feature
    geometry_container:node_coordinates = "x y" ;  // variables containing spatial node data
    geometry_container:part_node_count = "part_node_count" ;  // variable counting nodes per feature part
    geometry_container:interior_ring = "interior_ring" ;  // variable indicating holes
  int node_count(instance) ;  // total number of nodes across all parts of a given feature
  int part_node_count(part) ;
  int interior_ring(part) ;  // 1 for polygon interior ring (hole); 0 for exterior ring
  float datum ;
    datum:grid_mapping_name = "latitude_longitude" ;
    datum:semi_major_axis = 6378137. ;
    datum:inverse_flattening = 298.257223563 ;
    datum:longitude_of_prime_meridian = 0. ;
  double someData(instance, time) ;
    someData:coordinates = "time lat lon" ;
    someData:grid_mapping = "datum" ;
    someData:geometry = "geometry_container" ;
// global attributes:
  :Conventions = "CF-1.8" ;
  :featureType = "timeSeries" ;
data:
 time = 1, 2, 3, 4 ;
 lat = 25, 7 ;
 lon = 10, 40 ;
 x = 20, 10, 0, 5, 10, 15, 20, 10, 0, 50, 40, 30 ;  // note anti-clockwise order of rings
 y = 0, 15, 0, 5, 10, 5, 20, 35, 20, 0, 15, 0 ;
 node_count = 9, 3 ;  // number of nodes per feature
 part_node_count = 3, 3, 3, 3 ;  // four parts, with three nodes each (triangles)
 interior_ring = 0, 1, 0, 0 ;  // holes are indicated by a value of 1
 someData =
   1, 2, 3, 4,
   1, 2, 3, 4 ;
}
```

### How to interpret:
 
1) See CF-1.8 conventions.  
2) See the `timeSeries` featureType.  
3) See the `geometry` attribute on the data variable.
4) See the `geometry_type` in the variable referenced by the `geometry` attribute.  
5) Iterate over geometries found in the `node_coordinates` variable. Geometries are found using the `node_count` variable. Geometry parts are found using the `part_node_count` and `interior_ring` variables.
