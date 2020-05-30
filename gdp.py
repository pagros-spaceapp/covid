import time
import heatmap
import numpy as np

file_data = 'data/gdp.csv'
file_gadm = 'data/gadm36_USA_1'

def main():
    data = {}
    with open(file_data, 'r') as f:
        lines = f.read().split('\n')
        lines.pop(0)
        for line in lines:
            parts = line.split(',')
            if parts[0]:
                data[parts[0].strip()] = sum([float(i) for i in parts[1:]])

    heatmap.generateShapes(file_gadm, data, 'gdp.tif', np.float32)

if __name__ == '__main__':
    stime = time.time()
    main()
    print(f'done in {time.time()-stime:.3f}s')
