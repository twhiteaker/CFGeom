# netCDF-CF-simple-geometry
CF Convention for Representing Simple Geometry Types

## Scope

* Extends existing CF geometries in CF 1.7 to include lines and polygons
* Linear between nodes, not curves?
* Parametric shapes, e.g., circles, ellipses?

## Use Cases (not exhaustive)

* Encode watershed model time series and polygons in single file. Archiving the model output and geometry is the purpose.
* A single streamflow value for all rivers in the conterminous U.S. at a given point in time.
