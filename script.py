import utils

import json
import shapefile

# resolution of tif file (mdeg)
RES = 100

file_covid = 'covid.json'
file_gadm = 'data/gadm36_USA_0'

def echo(msg):
    print('[log]', msg)

with open(file_covid, 'r') as f:
    data = json.load(f)
features = data['features']

# convert to mdeg
sf = shapefile.Reader(file_gadm)
pts, lons, lats = utils.get_bounds2mdeg(sf.shape(0).points)

print(len(pts), lons, lats)
