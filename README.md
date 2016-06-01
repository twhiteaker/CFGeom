[![Build Status](https://travis-ci.org/bekozi/netCDF-CF-simple-geometry.svg?branch=master)](https://travis-ci.org/bekozi/netCDF-CF-simple-geometry)

# netCDF-CF-simple-geometry
**DRAFT** CF Convention for Representing Simple Geometry Types

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

## Important Elements and Structure

For discussion, the structure and attributes below should be what's needed. This is using a rectangular array for the data and an indexed ragged array for the polygon nodes. In CF 2 we would expect the ragged array notation to change to a variable length data field that uses more natural 2d indexing.

A piece of software reading this would be expected to:
1) See CF-1.8 conventions
2) See the timeSeries featureType
3) Find the timeseries\_id cf\_role
4) Find the coordinates 
5) See that the coordinates have a standard\_name "polygon node"
6) Find the variable with cf_role "node\_index" (is there another way to do this with ragged arrays? I'm typing from memory.)
7) Iterate over stations, picking out geometries for each timeseries.

Dimensionality;
1) strlen is long enough for the character array timeseries id.
2) node would be as long as all the nodes of all the timeseries + enough special characters to separate 'holes'. 
3) timeseries would be as long as the number of timeseries in the file.
4) index_start_stop would be 2 or 3 depending if the just the first node of a given time series or both the first and last node of a given timeseries is to be stored.
5) time is the length of the maximum length time series in the file. 

```
netcdf example {
dimensions:
        strlen ;
        node ;
				timeseries ;
				index_start_stop ;
        time;
variables:
        double polyLat(node) ;
                polyLat:standard_name = "polygon node" ;
        double polyLon(node) ;
                polyLon:standard_name = "polygon node" ;
				int polyIndex(timeseries, index_start_stop) ;
								polyIndex:cf_role = "node_index" ;
        char timeseriesID(timeseries, strlen) ;
                timeseriesID:cf_role = "timeseries_id" ;
        int data(timeseries, time) ;
                data:coordinates = "time polyLat polyLon" ;

// global attributes:
                :Conventions = "CF-1.8" ;
                :featureType = "timeSeries" ;
```
