import math

import rasterio
import numpy as np

# resolution of tif file (mdeg)
RES = 100
FILE_TIFF = 'out.tif'

# when to stop the algo
HEATMAP_E = 2
HEATMAP_CUTOFF = 1

Affine = rasterio.transform.Affine

def deg2cell(coord):
    # convert lon to pos for easier calc
    return tuple([int(i*1000/RES) for i in coord])

def get_bounds2cell(points):
    pts = []
    mins, maxs = [None]*2
    for p in points:
        a, b = deg2cell(p)
        if not mins or not maxs:
            mins = [a,b]
            maxs = [a,b]
        mins = [min(mins[0], a), min(mins[1], b)]
        maxs = [max(maxs[0], a), max(maxs[1], b)]

        # optimize: skip if conseq same pt
        if len(pts) and pts[-1]==(a,b):
            continue
        pts.append((a,b))

    lons, lats = [(mins[i], maxs[i]) for i in range(2)]
    return pts, lons, lats

def split_polygon(shape):
    parts = shape.parts
    points = shape.points

    pts_set = []
    for i in range(1, len(parts)):
        pts_set.append(points[parts[i-1]:parts[i]-1])
    pts_set.append(points[parts[-1]:-1])

    return pts_set

def mark_cells(pts, lons):
    """ polygon fill algo """
    cells = []
    minlon, maxlon = lons

    if len(pts) == 1:
        return pts

    for lon in range(minlon, maxlon+1):
        marks = []

        for i in range(len(pts)):
            a, b = pts[-i], pts[1-i]

            if not a[0]<=lon<=b[0] and not b[0]<=lon<=a[0]:
                continue
            c, d = [a[i]-b[i] for i in range(2)]
            v = int(a[1] if c==0 else a[1]+((lon-a[0])*(d/c)))

            if marks and marks[-1]==v: continue
            marks.append(v)
        if not marks: continue

        marks.sort()
        cells += [(lon, i) for i in range(marks[0], marks[-1]+1)]

        """
        TODO: failed because of fat pixels
        cells.append((lon, marks[0]))
        for i in range(1, len(marks)):
            a, b = marks[i-1], marks[i]
            cells.append((lon, b))
            if i%2:
                cells += [(lon, j) for j in range(a+1,b+1)]
        """
    return set(cells)

# NOTE: grid and stuff
def init_grid(lons, lats, dtype=np.uint32, nodata=0):
    grid = np.full((lats[1]-lats[0]+1, lons[1]-lons[0]+1, 1), nodata, dtype)
    transform = Affine.scale(RES/1000)
    transform *= Affine.translation(lons[0],lats[0])
    return  grid, transform, grid[0, 0, 0]

def write_tiff(outfile, grid, transform, nodata=None):
    # write to tiff file
    tiff = rasterio.open(
         outfile, 'w',
         driver='GTiff',
         height=grid.shape[0],
         width=grid.shape[1],
         count=1, dtype=grid.dtype,
         crs='+proj=latlong',
         transform=transform,
         nodata=nodata
    )
    tiff.write(grid[:,:,0], 1)
    tiff.close()

# NOTE: filling mechanism
def fill_hotspot(grid, start, val):
    e = HEATMAP_E
    def fn_pow_e(start, targ, val):
        if start==targ: return val

        # dist in mdeg
        dist = math.sqrt(sum([((start[i]-targ[i])*RES)**2 for i in range(2)]))/1000
        return val*(e**(-1*dist))

    def lim_pow_e(val):
        return math.log(val/HEATMAP_CUTOFF, e)*1000/RES

    W, H, _ = grid.shape
    diff = lim_pow_e(val)

    # end is exclusive
    minr, maxr = int(max(start[0]-diff, 0)), int(min(start[0]+diff+1, W))
    minc, maxc = int(max(start[1]-diff, 0)), int(min(start[1]+diff+1, H))

    for r in range(minr, maxr):
        for c in range(minc, maxc):
            grid[r][c] += int(fn_pow_e(start, (r,c), val))
