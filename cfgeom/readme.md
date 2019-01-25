## Create a geometry container with line geometries

```python
from cfgeom import Part, Geometry, GeometryContainer

# Geometries are comprised of one or more parts
# The part holds the node coordinates
x1 = [10, 5, 0]
y1 = [0, 5, 0]
part1 = Part(x1, y1)
# Set the geometry type when you create the geometry
line1 = Geometry('line', part1)
# Make another line, this time with z values
x2 = [9, 5, 1]
y2 = [1, 4, 1]
z2 = [1, 1, 1]
line2 = Geometry('line', Part(x2, y2, z2))
# In NetCDF-CF, geometries belong to a geometry container
geometries = [line1, line2]
line_container = GeometryContainer(geometries)
print(len(line_container.geoms))  # 2
```

## Create a polygon with holes

```python
# For polygons, parts can be created as holes
exterior = Part(x1, y1)
hole = Part(x2, y2, is_hole=True)
parts = [exterior, hole]
polygon = Geometry('polygon', parts)
polygon_container = GeometryContainer(polygon)
part = polygon_container.geoms[0].parts[1]
print(part.is_hole)  # True
print(part.x)  # [9, 5, 1]
```

## Write and read netCDF

```python
from cfgeom import read_netcdf
path_to_netcdf_file = 'test_file.nc'
polygon_container.to_netcdf(path_to_netcdf_file, use_vlen=False)
# There could be several geometry containers in a file
containers = read_netcdf(path_to_netcdf_file)
# Get the container named 'geometry_container'
container_from_nc = containers['geometry_container']['container']
# Nodes for polygon holes are oriented clockwise when writing to netCDF
print(container_from_nc.geoms[0].parts[1].x)  # [1.0, 5.0, 9.0]
```

## Write and read shapely

```python
from cfgeom import read_shapely
shapely_lines = line_container.to_shapely()
print(len(shapely_lines))  # 2
print(shapely_lines[0])  # LINESTRING (10 0, 5 5, 0 0)
container_from_shapely = read_shapely(shapely_lines)
print(container_from_shapely.geom_type)  # line
print(container_from_shapely.geoms[0].parts[0].x)  # [10.0, 5.0, 0.0]
```
