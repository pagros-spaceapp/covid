import shapefile
import utils

def echo(msg):
    print('[log]', msg)

def processShapeFile(fname, recordfn=lambda x: x[3], onlyone=False):
    active_all, lons, lats = {}, [], []
    if onlyone: recordfn = lambda x: 'main'

    with shapefile.Reader(fname) as sf:
        for pid in range(1 if onlyone else len(sf)):
            # split into polygon and convert to mdeg
            polygons_pts = utils.split_polygon(sf.shape(pid))
            state_name = recordfn(sf.record(pid)).lower().strip()
            echo(f'processing {state_name}')

            polygons = []
            for polygon in polygons_pts:
                if not polygon: continue
                pts, bnds0, bnds1 = utils.get_bounds2cell(polygon)
                polygons.append(pts)

                if not lons or not lats:
                    lons, lats = bnds0, bnds1
                lons = [min(lons[0], bnds0[0]), max(lons[1], bnds0[1])]
                lats = [min(lats[0], bnds1[0]), max(lats[1], bnds1[1])]

            # mark active cells
            active=[]
            for i in range(len(polygons)):
                if not i%300: echo(f"processing polygon {i}")
                polygon = polygons[i]
                active += utils.mark_cells(polygon, lons)
            active_all[state_name] = active
    return active_all, lons, lats

def generateShapes(boundaryFile, keyval, outfile=utils.FILE_TIFF,
        dtype=utils.np.uint32, recordfn=lambda x:x[3], nodata=-1):
    """ keyval = { 'SomeState': 1.2, 'SomeCouty': 1.3 } """
    cells, lons, lats = processShapeFile(boundaryFile, recordfn)
    def cell2rc(coords):
        return (coords[1]-lats[0], coords[0]-lons[0])

    grid, transform, nodata = utils.init_grid(lons, lats, dtype, nodata)
    for key in keyval:
        if not key: continue
        val, active = keyval[key], cells.get(key.lower().strip())
        if not active:
            echo(f'ERR cannot find {key} in boundary file')
            continue

        echo(f'processing {key}')
        for cell in active:
            r, c = cell2rc(cell)
            grid[r,c,0] = val
    utils.write_tiff(outfile, grid, transform, nodata)

def generateHeatmap(boundaryFile, coordval, outfile=utils.FILE_TIFF,
        dtype=utils.np.uint32, nodata=-1):
    """ coordval = { (20.31, 102.34672): 12, (latVal, lonVal): val } """
    cells, lons, lats = processShapeFile(boundaryFile, onlyone=True)
    def cell2rc(coords):
        return (coords[1]-lats[0], coords[0]-lons[0])

    active, processed_cnt = cells.get('main'), 0
    if not active:
        echo('ERR processing boundary, stopping here')
        return

    grid, transform, nodata = utils.init_grid(lons, lats, dtype, nodata)
    for key in coordval:
        if len(key)!=2 or not key[0] or not key[1]: continue

        val = coordval[key]
        cell = utils.deg2cell(key)
        if cell in active:
            echo(f'processing {key} = {val}')
            processed_cnt += 1
            utils.fill_hotspot(grid, cell2rc(cell), val)
    echo(f'total processed {processed_cnt}')
    utils.write_tiff(outfile, grid, transform, nodata)

if __name__ == '__main__':
    generateShapes(file_gadm, getFeatures(), np.float32)
