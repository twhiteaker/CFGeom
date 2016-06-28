[![Build Status](https://travis-ci.org/bekozi/netCDF-CF-simple-geometry.svg?branch=master)](https://travis-ci.org/bekozi/netCDF-CF-simple-geometry)
[![Join the chat at https://gitter.im/bekozi/netCDF-CF-simple-geometry](https://badges.gitter.im/bekozi/netCDF-CF-simple-geometry.svg)](https://gitter.im/bekozi/netCDF-CF-simple-geometry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# netCDF-CF-simple-geometry

**DRAFT** CF Convention for Representing Simple Geometry Types

## Scope

* Extends existing CF geometries in CF 1.7 to include lines and polygons
* Linear between nodes, not curves?
* Parametric shapes, e.g., circles, ellipses?

## Use Cases (not exhaustive)

* Encode watershed model time series and polygons in single file. Archiving the model output and geometry is the purpose.
* Encode a streamflow value for each river segment in the conterminous U.S. at a given point in time.

## Proposal

* Extend the CF timeseries feature type.
* Polygon or polyline used for spatial 'coordinates' of a timeseries variable.
* Mimic well known text style for encoding multipolygons with holes and multilines.

## Data Elements and Structure

For discussion, the structure and attributes below should be what's needed to store a polygon as the spatial coordinates of a `timeSeries` CF `featuretype`. This is using a rectangular array for the time series data and a contiguous ragged array (indexed ragged array would be silly) for the polygon nodes. In CF 2 we would expect the ragged array notation to change to a variable length data field that uses more natural 2d indexing.

### Representation of WKT-style polygons using NetCDF3.

The important detail this new convention would require are the standard\_name "polygon x node" and "polygon y node" otherwise, the data structures all adopt from the existing CF contiguous or incomplete ragged array formats. A file holding only polygon information without a timeSeries featureType would look like:

```
netcdf example {
dimensions:
    polyNodes ;
    polygons ;
variables:
    int crs() ;
    double polyLat(polyNodes) ;
        polyLat:standard_name = "polygon y node" ;
        polyLat:grid_mapping = "crs"
    double polyLon(polyNodes) ;
        polyLon:standard_name = "polygon x node" ;
        polyLon:grid_mapping = "crs"
    int polyNodeCount(polygons) ;
        polyNodeCount:sample_dimension = "polyNodes" ;
    double someVariable(polygons) ;
        someVariable:long_name = "a variable describing a single-valued attribute of a polygon"

// global attributes:
        :Conventions = "CF-1.8" ;
```

### Format overview with timeSeries featureType as context.
 
A piece of software reading this would be expected to:  
1) See CF-1.8 conventions  
2) See the timeSeries featureType  
3) Find the timeseries\_id cf\_role  
4) Find the coordinates  
5) See that the coordinates have a standard\_name "polygon node" to determine that these are polygons according to this new specification.  
6) Find the variable with sample_dimension "polyNodes" to determine the count of 'samples' (nodes) along the node dimension. (See CF 1.7 Section 9.3.3, could also use format in 9.3.2 - Incomplete multidimensional array representation.)  
7) Iterate over polygons, picking out geometries for each `timeSeries` using the count to pick out the required nodes.  

Dimensionality:  
1) strlen is long enough for the character array timeseries id.  
2) polyNodes would be as long as all the nodes of all the timeseries + enough special characters to separate 'holes'.  
3) polygons would be as long as the number of timeseries features in the file.  
4) time is the length of the maximum length time series in the file.  

```
netcdf example {
dimensions:
    strlen ;
    polyNodes ;
    polygons ;
    time ;
variables:
    int crs() ;
    double polyLat(polyNodes) ;
        polyLat:standard_name = "polygon y node" ;
        polyLat:grid_mapping = "crs"
    double polyLon(polyNodes) ;
        polyLon:standard_name = "polygon x node" ;
        polyLon:grid_mapping = "crs"
    int polyNodeCount(polygons) ;
        polyNodeCount:sample_dimension = "polyNodes" ; // Note this is backward compatible with CF1.6 but sample_dimension is problematic.
        polyNodeCount:contiguous_ragged_dimension = "polyNodes" ; // This is a proposal for a more approriate name for sample_dimension.
    char polygonsID(polygons, strlen) ;
        polygonsID:cf_role = "timeseries_id" ;
    int data(polygons, time) ;
        data:coordinates = "time polyLat polyLon" ;

// global attributes:
        :Conventions = "CF-1.8" ;
        :featureType = "timeSeries" ;
```


### Encoding of WKT multiPolygons and multiLine.

... TBD ...
