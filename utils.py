def get_bounds2mdeg(points):
    pts = []
    mins, maxs = [None]*2
    for p in points:
        a, b = [int(i*1000) for i in p]
        if not mins or not maxs:
            mins = [a,b]
            maxs = [a,b]
        mins = [min(mins[0], a), min(mins[1], b)]
        maxs = [max(maxs[0], a), max(maxs[1], b)]

        pts.append((a,b))

    return pts, mins, maxs

