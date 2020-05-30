""" whole project in int, cos easier """

import utils
import json

import rasterio
import shapefile
import numpy as np

file_covid = 'covid.json'
file_gadm = 'data/gadm36_USA_0'

Affine = rasterio.transform.Affine

def echo(msg):
    print('[log]', msg)

def getActive():
    # convert to mdeg
    with shapefile.Reader(file_gadm) as sf:
        pts, bnds0, bnds1 = utils.get_bounds2cell(sf.shape(0).points)
        echo('reading done')

    active = utils.mark_cells(pts, bnds0)
    return active, bnds0, bnds1

def getFeatures():
    with open(file_covid, 'r') as f:
        data = json.load(f)
    return data['features']

def main():

    cells, lons, lats = getActive()
    def cell2rc(coords):
        return (coords[0]-lons[0], coords[1]-lats[0])

    grid = np.zeros((lons[1]-lons[0], lats[1]-lats[0], 1), np.uint32)
    transform = Affine.scale(utils.RES)
    transform *= Affine.translation(lons[0],lats[0])
    echo('initialization done')

    # fill in the hotspot map
    feats = getFeatures()
    for feat in feats:
        attrs = feat['attributes']
        lat, lon = attrs['Lat'], attrs['Long_']
        if not lon or not lat: continue

        confirmed, recovered =  attrs['Confirmed'], attrs['Recovered']
        deaths, active = attrs['Deaths'], attrs['Active']
        cell = utils.deg2cell((lon,lat))

        if cell in cells:
            utils.fill_hotspot(grid, cell2rc(cell), confirmed)
    echo('grid filled')

    # write to tiff file
    tiff = rasterio.open(
         'test.tif', 'w',
         driver='GTiff',
         height=grid.shape[0],
         width=grid.shape[1],
         count=1, dtype=grid.dtype,
         crs='+proj=latlong',
         transform=transform,
    )
    tiff.write(grid[:,:,0], 1)
    tiff.close()
    echo('tif file saved')

if __name__ == '__main__':
    main()
