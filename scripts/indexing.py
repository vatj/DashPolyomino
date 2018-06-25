import glob
import json

index_file = '/rscratch/vatj2/cloud/PolyominoDash/DashPolyomino/index.json'

current_files = glob.glob('/rscratch/vatj2/public_html/Polyominoes/data/gpmap/V6/experiment/*.txt')
file_names = [file.rsplit('/')[-1] for file in current_files]

with open(index_file, "w") as fopen:
	json.dump(file_names, fopen)
