# netCDF-CF-simple-geometry
CF Convention for Representing Simple Geometry Types

## Scope

* Extends existing CF geometries in CF 1.7 to include lines and polygons
* Linear between nodes, not curves?
* Parametric shapes, e.g., circles, ellipses?

## Use Cases (not exhaustive)

* Encode watershed model time series and polygons in single file. Archiving the model output and geometry is the purpose.
* A single streamflow value for all rivers in the conterminous U.S. at a given point in time.

## Proposal

* Extending the CF timeseries feature type.
* polygon or polyline used for spatial 'coordinates' of a timeseries variable.
* mimic well known text style for encoding multi polygons with holes and multilines.

## Data Elements and Structure

For discussion, the structure and attributes below should be what's needed to store a polygon as the `timeseries_id` of a `timeSeries` featuretype. This is using a rectangular array for the time series data and a contiguous ragged array (indexed ragged array would be silly) for the polygon nodes. In CF 2 we would expect the ragged array notation to change to a variable length data field that uses more natural 2d indexing.

### Format overview with timeSeries featureType as context.
 
A piece of software reading this would be expected to:
1) See CF-1.8 conventions
2) See the timeSeries featureType
3) Find the timeseries\_id cf\_role
4) Find the coordinates 
5) See that the coordinates have a standard\_name "polygon node" to determine that these are polygons according to this new specification.
6) Find the variable with sample_dimension "node" to determine the count of 'samples' (nodes) along the node dimension. (See CF 1.7 Section 9.3.3, could also use format in 9.3.2 - Incomplete multidimensional array representation.)
7) Iterate over polygons, picking out geometries for each `timeSeries` using the count to pick out the required nodes.

Dimensionality;
1) strlen is long enough for the character array timeseries id.
2) node would be as long as all the nodes of all the timeseries + enough special characters to separate 'holes'. 
3) polygons would be as long as the number of timeseries/polygons in the file.
4) time is the length of the maximum length time series in the file. 

```
netcdf example {
dimensions:
    strlen ;
    node ;
		polygons ;
    time ;
variables:
		int crs() ;
    double polyLat(node) ;
            polyLat:standard_name = "polygon y node" ;
						polyLat:grid\_mapping = "crs"
    double polyLon(node) ;
            polyLon:standard_name = "polygon x node" ;
						polyLon:grid\_mapping = "crs"
		int polyIndex(node) ;
				polyIndex:sample_dimension = "node" ;
    char polygonsID(polygons, strlen) ;
            polygonsID:cf_role = "timeseries_id" ;
    int data(polygons, time) ;
            data:coordinates = "time polyLat polyLon" ;

// global attributes:
                :Conventions = "CF-1.8" ;
                :featureType = "timeSeries" ;
```

### Representation of WKT - style polygons using NetCDF3.

In `Format Overview with timeSeries featureType`, above, the `polyLat`, `polyLon`, and polyIndex variables make up a collection of polygons stored in contiguous ragged array format. The important details this new convention would require are the standard\_name "polygon x node" and "polygon y node" otherwise, the data structures all adopt from the existing CF contiguous or incomplete ragged array formats. A file holding only polygon information without the timeSeries featureType would look like:

```
netcdf example {
dimensions:
    node ;
		polygons ;
variables:
		int crs() ;
    double polyLat(node) ;
            polyLat:standard_name = "polygon y node" ;
						polyLat:grid\_mapping = "crs"
    double polyLon(node) ;
            polyLon:standard_name = "polygon x node" ;
						polyLon:grid\_mapping = "crs"
		int polyIndex(node) ;
				polyIndex:sample_dimension = "node" ;

// global attributes:
                :Conventions = "CF-1.8" ;
```

### Encoding of WKT multiPolygons and multiLine.

... TBD ...