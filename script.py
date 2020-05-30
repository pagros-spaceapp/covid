import utils

import json
import shapefile

file_covid = 'covid.json'
file_gadm = 'data/gadm36_USA_0'

def echo(msg):
    print('[log]', msg)

with open(file_covid, 'r') as f:
    data = json.load(f)
features = data['features']

# convert to mdeg
sf = shapefile.Reader(file_gadm)
pts, bnds0, bnds1 = utils.get_bounds2cell(sf.shape(0).points)
echo('reading done')

utils.mark_cells(pts, bnds0)
