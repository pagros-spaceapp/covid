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
    with shapefile.Reader(file_gadm) as sf:
        polygons_pts = utils.split_polygon(sf.shape(0).points)

    # split into polygon and convert to mdeg
    polygons, lons, lats = [], None, None
    for polygon in polygons_pts:
        if not polygon: continue
        pts, bnds0, bnds1 = utils.get_bounds2cell(polygon)
        polygons.append(pts)

        if not lons or not lats:
            lons, lats = bnds0, bnds1
        lons = [min(lons[0], bnds0[0]), max(lons[1], bnds0[1])]
        lats = [min(lats[0], bnds1[0]), max(lats[1], bnds1[1])]

    # mark active cells
    active = []
    for polygon in polygons:
        active += utils.mark_cells(polygon, lons)
    print(lons, lats)
    return active, lons, lats

def getFeatures():
    with open(file_covid, 'r') as f:
        data = json.load(f)
    return data['features']

def main():
    cells, lons, lats = getActive()
    def cell2rc(coords):
        return (coords[1]-lats[0], coords[0]-lons[0])

    # grid in lats, lons
    grid = np.zeros((lats[1]-lats[0]+1, lons[1]-lons[0]+1, 1), np.uint32)
    transform = Affine.scale(utils.RES/1000)
    transform *= Affine.translation(lons[0],lats[0])
    echo('initialization done')

    for cell in cells:
        r, c = cell2rc(cell)
        grid[r,c,0] = 1

    """
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
    """

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
