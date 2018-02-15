"""Serializes GeometryContainer objects to JSON."""

import json


def _dict_to_json(dict_obj):
    """Exports a Python dictionary to JSON.

    Args:
        dict_obj (dict): The dictionary.

    Returns:
        str: JSON string representing the dictionary.

    """
    return json.dumps(dict_obj, sort_keys=True, indent=4)


def part_to_dict(part):
    """Exports a Part object to a dictionary.

    The export includes computing hidden members.

    Args:
        part (Part): The Part object.

    Returns:
        dict: A copy of the Part object's dictionary

    """
    part.is_clockwise()  # Compute hidden _is_clockwise member
    return part.__dict__.copy()


def part_to_json(part):
    """Serializes a Part object to JSON.

    Args:
        part (Part): The Part object.

    Returns:
        str: The JSON string serialization of the object.

    """
    return _dict_to_json(part_to_dict(part))


def geom_to_dict(geom):
    """Exports a Geometry object to a dictionary.

    The export includes computing hidden members, and converting Part objects
    to native Python objects.

    Args:
        geom (Geometry): The Geometry object.

    Returns:
        dict: A dictionary of native Python objects representing the Geometry

    """
    # Compute hidden members
    geom.has_hole()
    geom.is_multipart()
    geom.has_z()

    ret = geom.__dict__.copy()
    ret['parts'] = [part_to_dict(p) for p in ret['parts']]
    return ret


def geom_to_json(geom):
    """Serializes a Geometry object to JSON.

    Args:
        geom (Geometry): The Geometry object.

    Returns:
        str: The JSON string serialization of the object.

    """
    return _dict_to_json(geom_to_dict(geom))


def container_to_dict(container):
    """Exports a GeometryContainer object to a dictionary.

    The export includes computing hidden members, and converting Geometry
    objects to native Python objects.

    Args:
        geom (GeometryContainer): The GeometryContainer object.

    Returns:
        dict: A dictionary of native Python objects representing the
        GeometryContainer

    """
    # Compute hidden members
    container.has_hole()
    container.is_multipart()
    container.has_z()
    container.wkt_type()

    ret = container.__dict__.copy()
    ret['geoms'] = [geom_to_dict(g) for g in ret['geoms']]
    return ret

    
def container_to_json(container):
    """Serializes a GeometryContainer object to JSON.

    Args:
        container (GeometryContainer): The GeometryContainer object.

    Returns:
        str: The JSON string serialization of the object.

    """
    return _dict_to_json(container_to_dict(container))
