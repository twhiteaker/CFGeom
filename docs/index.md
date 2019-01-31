# CFGeom

A Python Reference Implementation for Representing Geometries in NetCDF
Following the CF Conventions

This project demonstrates how points, lines, polygons, and their multipart
equivalents can be represented in NetCDF-CF. The project includes a Python
reference implementation for reading and writing geometries in a netCDF file.

* Install this package and start coding with the [tutorial](tutorial.html).
* For simplified examples demonstrating the various geometry types in CDL and
  netCDF format, see the [simplified examples
  folder](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/simplified_examples).
  You'll find both CRA (contiguous ragged array for netCDF-3) and VLEN (variable
  length array for netCDF-4) examples.  Note that these examples are simplified
  in that they do not include data variables associated with the geometries, so
  they are not truly CF-compliant.
* For full examples, see the [use case
  folders](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/data/use_cases).
  Each folder includes a CDL file to demonstrate how to encode geometries. CDL
  files are text representations of the content of a netCDF file, and can be
  viewed with a text editor.
* To read and write geometries using Python, see the [reference
  implementation](https://github.com/twhiteaker/netCDF-CF-simple-geometry/tree/master/cfgeom).
* For more about CF geometries and the scope of this project, see the remainder
  of this document.

You may also be interested in the [R reference implementation](https://github.com/dblodgett-usgs/NCDFSG).

## Dependencies

* Shapely
* netCDF4

## Scope

CFGeom is primarily concerned with reading and writing the geometry portion of a
netCDF file. While supporting CF 1.8, the implementation also demonstrates use
of enhanced netCDF-4 capabilities for possible inclusion in CF 2.0.

### What This Package Is Not

This package is not a general CF library for Python. For that, see David
Hassell's [cf-python package](https://pypi.org/project/cf-python/)).

This package does not handle reading coordinate system information or transforming
from one system to another. Data variables in CF 1.8 include a **grid_mapping**
attribute naming a variable that provides coordinate system details, so users
should read that variable (which can be done with the [netCDF4
package](https://pypi.org/project/netCDF4/)) if interested in coordinate system
information. Likewise, when writing geometries to a netCDF file, users should
project geometries to the same coordinate system as specified for the data
variable prior to adding the geometries to the netCDF file.

## About CF Geometries

NetCDF is a self-describing file format for storing scientific data, typically
as multidimensional arrays. The [Climate and Forecast conventions
(CF)](http://cfconventions.org/latest.html) prescribe data structures and
attributes within a netCDF file to promote data sharing and reuse. In addition
to data measured on a regular grid, CF also enables users to represent data
associated with [discrete sampling
geometries](http://cfconventions.org/cf-conventions/cf-conventions.html#discrete-sampling-geometries),
such as a time series of average areal precipitation over a watershed. Using
watersheds as an example, locations of watershed feature instances could be
represented as a point (e.g., the watershed centroid). The variables defining
each point's location comprise the coordinate variables associated with the data
variable.

CF version 1.8 introduced a specification for representing [line and polygon
geometries](https://github.com/cf-convention/cf-conventions/blob/master/ch07.adoc#geometries),
allowing for the shape of a watershed boundary or river line to be encoded in a
netCDF file in a standard way. 

**Note:** Henceforth in this text, we shall use the term *geometry* to refer to
line and polygon geometries introduced in CF 1.8.

These geometries are stored in addition to coordinate variables so that software
can fall back to the simple point representation of features if the software is
unaware of CF 1.8 geometries.  

The geometries described in CF 1.8 include points, lines, polygons (including
polygons with holes), and their multipart equivalents. The nodes comprising
lines or polygons are assumed to be connected with straight lines in the
coordinate system of the data variable.

In a CF-compliant netCDF file with geometries, the geometries are always
associated with a data variable. The data variable includes a **geometry**
attribute naming a geometry container variable which provides more information
about the geometries via its attributes. At a minimum, the geometry container
includes attributes declaring the geometry type and the names of variables
storing x, y, and optionally z coordinates for each node in each geometry. The
container may also have attributes naming which variables store the number of
nodes per geometry, which variable stores the number of nodes per geometry part
if multipart geometries are present, and which variable stores whether each part
is a hole if holes are present.  For more information including examples, see
[Chapter 7 of the CF
Conventions](https://github.com/cf-convention/cf-conventions/blob/master/ch07.adoc#geometries).

### Example: Polygons in a NetCDF-3 timeSeries featureType File

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
    x:nodes = "X" ;
  double y(node) ;
    y:units = "degrees_north" ;
    y:standard_name = "latitude" ;
    y:nodes = "Y" ;
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

#### How to interpret

1) See CF-1.8 conventions.  
2) See the `timeSeries` featureType.  
3) See the `geometry` attribute on the data variable.
4) See the `geometry_type` in the variable referenced by the `geometry` attribute.  
5) Iterate over geometries found in the `node_coordinates` variable. Geometries
   are found using the `node_count` variable. Geometry parts are found using the
   `part_node_count` and `interior_ring` variables.
