"""Creates a markdown file with VLEN CDL based on WKT examples."""

import datetime
import json
from collections import OrderedDict
import os
import sys

from shapely import wkt

sys.path.append(os.path.abspath('../src/python'))
from ncsg import cf

fixture_wkt = '../data/fixture_wkt.json'
out_file = 'tmp/create_cdl_examples.md'
descriptions = {'point': {'msg': 'Point', 'order': 0},
                'multipoint': {'msg': 'MultiPoint', 'order': 3},
                'polygon': {'msg': 'Polygon', 'order': 2},
                'multipolygon': {'msg': 'MultiPolygon', 'order': 5},
                'linestring': {'msg': 'LineString', 'order': 1},
                'multilinestring': {'msg': 'MultiLineString', 'order': 4},
                'multipolygon_hole': {'msg': 'MultiPolygon with One Interior Ring', 'order': 7},
                'multipolygons_holes': {'msg': 'Multiple MultiPolygons with Interior Rings', 'order': 8},
                'polygon_hole': {'msg': 'Polygon with One Interior Ring', 'order': 6}}

new_desc = OrderedDict()
for ctr in range(len(descriptions)):
    for k, v in descriptions.items():
        if v['order'] == ctr:
            new_desc[k] = v


########################################################################################################################


def add_section(out, wktvalue, dim):
    geom = wkt.loads(wktvalue)
    coll = cf.from_shapely(geom)
    append(out, '## {0} ({1})'.format(descriptions[wktkey]['msg'], dim.upper()))
    append(out, 'Well-Known Text (WKT): ```{}```'.format(wktvalue))
    append(out, '')
    append(out, 'Common Data Language (CDL):'.format(wktvalue))
    append(out, '```')
    desc = coll.describe(header=False, capture=True)
    desc = desc.split('\n')
    for d in desc:
        d = str(d.replace('\t', '  '))
        if d.startswith("b'"):
            d = d[2:]
        if d == "'":
            continue
        append(out, d, add_newline=False)
    append(out, '```')


def append(container, msg, add_newline=True):
    container.append(msg)
    if add_newline:
        container.append('\n')


########################################################################################################################

with open(fixture_wkt) as f:
    wkts = json.load(f)

out = []

append(out, '# Examples - VLEN Ragged Arrays (NetCDF4 Only)')
append(out, 'Created {}'.format(datetime.datetime.now()))
append(out, '')

for wktkey in new_desc.keys():
    for dkey in ['2d', '3d']:
        try:
            wktvalue = wkts[dkey][wktkey]
        except KeyError:
            if dkey != '3d' or 'holes' not in wktkey:
                raise
            else:
                continue
        print dkey, wktkey
        add_section(out, wktvalue, dkey)

with open(out_file, 'w') as fout:
    for l in out:
        fout.write(l)
