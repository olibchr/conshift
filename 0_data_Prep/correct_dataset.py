import json
import os
import sys

path = sys.argv[1]

for filename in os.listdir(path):
    if ("##" in filename) or ("DS_" in filename):
        continue
    output_file  = open(path + "output/" + filename, "wr")
    try:
        with open(path + filename, "rb") as this_file:
            for line in this_file:
                if "wiki/wiki/" in line:
                    line = line.replace("wiki/wiki/", "wiki/")
                    print "instance found in " + filename
                output_file.write(line)
    except Exception:
        print "exception"