[![Build Status](https://travis-ci.org/twhiteaker/netCDF-CF-simple-geometry.svg?branch=master)](https://travis-ci.org/twhiteaker/netCDF-CF-simple-geometry)

# netCDF-CF-simple-geometry

**DRAFT** CF Convention for Representing Simple Geometry Types

## Scope

* Extends existing CF capabilities in CF 1.7 to include _geometries_ of types point, line, and polygon.
* Limited to linear connections between nodes in the coordinate reference system the nodes are defined in.
* Allows geometries to be attached to a Discrete Sampling Geometry (DSG) _instance_ variable.

## Use Cases

* Encode watershed model time series and polygons in a single file to archive model output and geometry.
* Encode a streamflow value for each river segment in the conterminous U.S. at a given point in time.

## Proposal

* Support point, line, and polygon geometry, including multilines and multipolygons with holes, in netCDF-3 for potential inclusion in CF 1.8 with a clear path to enhanced netCDF-4 for inclusion in CF 2.0. 
* Define a standard that the CF timeSeries feature type could use to specify spatial coordinates of a timeSeries variable.

## What does the existing specification do that's similar to this proposal? 
For any coordinate variable, `bounds` can be defined to describe the boundaries of the region (typically in space-time) meant to be represented by the variable. This capability, described in [section 7.1](http://cfconventions.org/cf-conventions/cf-conventions.html#cell-boundaries), supports three types of `bounds`: 1-D bounds such as a time period, 2-D bounds such as the bounding rectangle of a cell in a 2-D grid, and n-d bounds to describe a cell with more than four edges.

For example, consider a 2-D grid of cells that do not lie on an orthogonal grid and consequently have curved cell edges. If these cells are to be represented acurately using lat/lon `bounds` many nodes are required to describe their curvature. In this case, a `lat_bnds` and `lon_bnds` variable will have `p` vertices, where p is the number needed to adequately represent the curvature of the cells.  

Extending Example 7.2 in the NetCDF-CF 1.7 specification, and assuming 10 vertices per edge plus corners are needed, this would look like:

```
dimensions:
  imax = 128 ;
  jmax = 64 ;
  nv = 44 ;
variables:
  float lat(jmax,imax) ;
    lat:long_name = "latitude" ;
    lat:units = "degrees_north" ;
    lat:bounds = "lat_bnds" ;
  float lon(jmax,imax) ;
    lon:long_name = "longitude" ;
    lon:units = "degrees_east" ;
    lon:bounds = "lon_bnds" ;
  float lat_bnds(jmax,imax,nv) ;
  float lon_bnds(jmax,imax,nv) ;
```

With regards to time series, Discrete Sampling Geometries (DSGs) handle data from one (or a collection of) `timeSeries` (point), `trajectory`, `profile`, `trajectoryProfile` or `timeSeriesProfile` geometries. Measurements are from a **point** (timeSeries and profile) or **points** along a trajectory. 

## What doesn't the existing specification do that we need? 
From the perspective of time series associated with polygons, DSGs have no system to define a geometry (multipoint, polyline, polygon, etc.) and an association with a time series that applies over that entire geometry.  
> e.g., The expected rainfall in this watershed polygon for some period of time is 10 mm.  

Current practice has been to assign a nominal point (centroid or some other location) or just use an ID and forgo spatial information within a NetCDF-CF file. In order to satisfy a number of environmental modeling use cases, a way to encode a multipoint, line or polygon geometry that is the static spatial element for which one or more time series can be associated is needed.

The current n-d `bounds` mechanism is limited in that every cell must have the same number of vertices. In order to support geometries more generally a new approach is needed. Typically, these geometries will each have drastically different numbers of nodes and may have multiple parts and/or holes. This requirement is not supported by the existing n-d `bounds` but conceptually, a geometry can be associated with a cell the same as an n-d geometry, albeit with some additional metadata and data.

## How does what we are proposing work with / build on the current specification?
In this proposal, we intend to provide an encoding to define collections of geometries (point, line, polygon, including their multipart equivalents). Geometries are defined by a `geometry_container` variable within the file.  The scalar `geometry_container` variable has attributes pointing to variables providing the coordinates of each node in the collection of geometries, an attribute indicating the geometry type, and additional attributes to deal with multipart features and polygon holes if needed.  Data variables are associated with geometries by including a `geometry` attribute on the data variable.  
This will interface cleanly with the information encoded in Discrete Sampling Geometries, enabling DSGs and Geometries to be used in tandem to describe relevant datasets. 

---

### Example: Representation of polygons in a NetCDF-3 timeSeries featureType file.

Below is sample CDL demonstrating how multipolygons with holes can be encoded in NetCDF-3 using a contiguous ragged array-like encoding. The example includes two polygons. The first polygon is a multipart feature with two triangles, with a triangular hole in the first part.  The second polygon is a single triangle.

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
    lat:geometry = "geometry_container" ;
    lat:axis = "Y" ;
  double lon(instance) ;
    lon:units = "degrees_east" ;
    lon:standard_name = "longitude" ;
    lon:geometry = "geometry_container" ;
    lon:axis = "X" ;
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