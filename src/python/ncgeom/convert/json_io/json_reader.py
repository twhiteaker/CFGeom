import json

from ... container import GeometryContainer
from ... geometry import Geometry
from ... part import Part


def json_to_part(json_string):
    data = json.loads(json_string)
    part = Part([0], [0])  # make a dummy to overwrite
    part.__dict__ = data
    return part


def json_to_geom(json_string):
    data = json.loads(json_string)
    parts = [json_to_part(json.dumps(p)) for p in data['parts']]
    geom = Geometry(data['geom_type'], parts)
    for key in data:
        if key != 'parts':
            geom.__dict__[key] = data[key]
    return geom


def json_to_container(json_string):
    data = json.loads(json_string)
    geoms = [json_to_geom(json.dumps(g)) for g in data['geoms']]
    container = GeometryContainer(geoms)
    for key in data:
        if key != 'geoms':
            container.__dict__[key] = data[key]
    return container
