import sys
import json
from bars_detection import BarsDetection

bd = BarsDetection()
a = open(sys.argv[1])
b = a.read()
c = bd.annotate(b)
for i in c.views:
    a = i.__dict__
    print (a)
    c = a.get("contains")
    bd = a.get("annotations")
    for d in bd:
        print (d.__dict__)
