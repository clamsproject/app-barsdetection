'''
This script is meant to be applied to a directory of videos that are mounted via a docker volume.
Running the script produces a csv containing
video_filename, bars_start, bars_end, bars_start, bars_end...
'''

import argparse
import os
import json
import csv
from tqdm import tqdm
from bars_detection import BarsDetection

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("output")
args = parser.parse_args()
bd = BarsDetection()

with open(args.output, 'w') as out:
    writer = csv.writer(out)
    for file in tqdm(os.listdir(args.directory)):
        if file.endswith("mp4"):
            res = BarsDetection.run_bd(os.path.join(args.directory, file))
            row = [file] + [ts for el in res for ts in el]
            writer.writerow(row)
