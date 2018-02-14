import sys
sys.path.insert(0, r'C:\Users\twhit\Documents\GitHub\netCDF-CF-simple-geometry\src\python')
from os.path import join

import pytest
from ncgeom import Part, Geometry, GeometryContainer


@pytest.fixture(scope="class")
def arrays():
    array_dict = {}
    array_dict['point'] = ([1], [1])
    array_dict['point z'] = ([2], [3], [50])
    array_dict['multipoint'] = ([[1], [4]], [[4], [3]])
    array_dict['line'] = ([3, 1, 4], [1, 3, 4])
    array_dict['line2'] = ([7, 8], [9, 10])
    array_dict['line z'] = ([3, 1, 4], [1, 3, 4], [2, 2, 1])
    array_dict['multiline'] = ([[1, 2], [2, 4]], [[4, 3], [3, 2]])
    array_dict['multiline2'] = ([[5, 6, 5], [5, 5, 6]], [[7, 9, 8], [7, 8, 9]])
    array_dict['polygon'] = ([10, 5, 0], [0, 5, 0])
    array_dict['polygon clockwise'] = ([0, 5, 10], [0, 5, 0])
    array_dict['hole'] = ([1, 5, 9], [1, 4, 1])
    array_dict['hole anticlockwise'] = ([9, 5, 1], [1, 4, 1])
    array_dict['polygon2'] = ([20, 15, 11, 15], [20, 25, 20, 15])
    array_dict['polygon3'] = ([100, 75, 50], [100, 500, 100])
    array_dict['multipolygon'] = (array_dict['polygon'], array_dict['polygon2'])
    return array_dict


def parts():
    coord_arrays = arrays()
    parts_dict = {}
    for key in coord_arrays:
        coords = coord_arrays[key]
        has_z = 'z' in key
        is_hole = 'hole' in key
        if 'multi' in key:
            parts_dict[key] = [Part(c[0], c[1], is_hole=is_hole) for c in coords]
        else:
            if has_z:
                parts_dict[key] = Part(coords[0], coords[1], coords[2], is_hole=is_hole)
            else:
                parts_dict[key] = Part(coords[0], coords[1], is_hole=is_hole)
    return parts_dict


def geoms():
    parts_dict = parts()
    geom_dict = {}
    for key in parts_dict:
        parts_list = parts_dict[key]
        if 'point' in key:
            geom_type = 'point'
        elif 'line' in key:
            geom_type = 'line'
        else:
            geom_type = 'polygon'
        if 'hole' not in key:
            geom_dict[key] = Geometry(geom_type, parts_list)

    geom_dict['polygon hole'] = Geometry(
        'polygon', [parts_dict['polygon'], parts_dict['hole']])
    geom_dict['multipolygon hole'] = Geometry(
        'polygon', [parts_dict['polygon'], parts_dict['hole'],
                    parts_dict['polygon2']])
    return geom_dict


def containers():
    geom_dict = geoms()
    container_dict = {}
    for key in geom_dict:
        geom = geom_dict[key]
        container_dict[key] = GeometryContainer(geom)
    container_dict['points'] = GeometryContainer(
        [geom_dict['point'], geom_dict['point z']])
    container_dict['multipoints'] = GeometryContainer(
        [geom_dict['point'], geom_dict['multipoint']])    
    container_dict['lines'] = GeometryContainer(
        [geom_dict['line'], geom_dict['line2']])
    container_dict['multilines'] = GeometryContainer(
        [geom_dict['line'], geom_dict['multiline']])
    container_dict['polygons'] = GeometryContainer(
        [geom_dict['polygon'], geom_dict['polygon2']])
    container_dict['polygons hole'] = GeometryContainer(
        [geom_dict['polygon hole'], geom_dict['polygon2']])
    container_dict['multipolygons'] = GeometryContainer(
        [geom_dict['polygon3'], geom_dict['multipolygon hole']])
    return container_dict


def save(container, name):
    with open(name + '.json', 'w') as f:
        f.write(container.to_json())
    container.to_netcdf(name + '_cra.nc')
    container.to_netcdf(name + '_vlen.nc', True)


if __name__ == '__main__':
    container_dict = containers()
    save(container_dict['points'], 'point_z')
    save(container_dict['multipoints'], 'multipoint')
    save(container_dict['lines'], 'line')
    save(container_dict['multilines'], 'multiline')
    save(container_dict['polygons'], 'polygon')
    save(container_dict['polygons hole'], 'polygon_hole')
    save(container_dict['multipolygons'], 'multipolygons')
