import json


def _dict_to_json(dict_obj):
    return json.dumps(dict_obj, sort_keys=True, indent=4)


def part_to_dict(part):
    part.is_clockwise()  # Compute hidden _is_clockwise member
    return part.__dict__.copy()


def part_to_json(part):
    return _dict_to_json(part_to_dict(part))


def geom_to_dict(geom):
    # Compute hidden members
    geom.has_hole()
    geom.is_multipart()
    geom.has_z()

    ret = geom.__dict__.copy()
    ret['parts'] = [part_to_dict(p) for p in ret['parts']]
    return ret


def geom_to_json(geom):
    return _dict_to_json(geom_to_dict(geom))


def container_to_dict(container):
    # Compute hidden members
    container.has_hole()
    container.is_multipart()
    container.has_z()
    container.wkt_type()

    ret = container.__dict__.copy()
    ret['geoms'] = [geom_to_dict(g) for g in ret['geoms']]
    return ret

    
def container_to_json(container):
    return _dict_to_json(container_to_dict(container))
