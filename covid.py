import time
import json

import heatmap
import numpy as np

# if you do state, rmb to change file_gadm
file_data = 'data/covid.json'
file_gadm0 = 'data/gadm36_USA_0'
file_gadm1 = 'data/gadm36_USA_1'

def main():
    with open(file_data, 'r') as f:
        data = json.load(f)
    feats = data['features']

    coordval, keyval = {}, {}
    for feat in feats:
        attrs = feat['attributes']
        state = attrs['Province_State']
        lat, lon = attrs['Lat'], attrs['Long_']
        confirmed, recovered =  attrs['Confirmed'], attrs['Recovered']
        deaths, active = attrs['Deaths'], attrs['Active']

        coordval[(lon,lat)] = confirmed
        keyval[state] = confirmed

    heatmap.generateShapes(file_gadm1, keyval, 'covid_shape.tif')
    heatmap.generateHeatmap(file_gadm0, coordval, 'covid_hotspot.tif')

if __name__ == '__main__':
    stime = time.time()
    main()
    print(f'done in {time.time()-stime:.3f}s')
