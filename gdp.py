import time
import heatmap
import numpy as np

file_data = 'data/gdp.csv'
file_gadm = 'data/gadm36_USA_1'

def main():
    data = {}
    with open(file_data, 'r') as f:
        # split into different lines and remove first line (the header)
        lines = f.read().split('\n')
        lines.pop(0)

        # process the rest of the lines
        for line in lines:
            # split by commas
            parts = line.split(',')

            # clean up the name, and convert rest to float
            name = parts[0].strip()
            rest = [float(i) for i parts[1:]]

            # set the val to the sum of all the quarters
            if name:
                data[name] = sum(rest)

    heatmap.generateShapes(file_gadm, data, 'gdp.tif', np.float32)

if __name__ == '__main__':
    stime = time.time()
    main()
    print(f'done in {time.time()-stime:.3f}s')
