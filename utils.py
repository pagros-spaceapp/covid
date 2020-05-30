import math

# resolution of tif file (mdeg)
RES = 1000

# when to stop the algo
HEATMAP_CUTOFF = 1

def deg2cell(coord):
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

def mark_cells(pts, lons):
    """ polygon fill algo """
    cells = []
    minlon, maxlon = lons

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

        marks.sort()
        cells.append((lon, marks[0]))
        for i in range(1, len(marks)):
            a, b = marks[i-1], marks[i]
            cells.append((lon, b))
            if i%2:
                cells += [(lon, j) for j in range(a+1,b+1)]
    return set(cells)

def fn_inv_deg_sq(start, targ, val):
    if start==targ: return val

    # dist in mdeg
    dist = math.sqrt(sum([((start[i]-targ[i])*RES)**2 for i in range(2)]))/1000
    return val/(dist**2)

def lim_inv_deg_sq(val):
    return HEATMAP_CUTOFF*math.sqrt(val)

def fill_hotspot(grid, start, val):
    W, H, _ = grid.shape
    diff = lim_inv_deg_sq(val)

    # end is exclusive
    minr, maxr = int(max(start[0]-diff, 0)), int(min(start[0]+diff+1, W))
    minc, maxc = int(max(start[1]-diff, 0)), int(min(start[1]+diff+1, H))

    for r in range(minr, maxr):
        for c in range(minc, maxc):
            grid[r][c] += int(fn_inv_deg_sq(start, (r,c), val))
