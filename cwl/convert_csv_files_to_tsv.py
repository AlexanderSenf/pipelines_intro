import os
import sys

from csv import reader, writer

base = os.path.basename(sys.argv[1])
output_filename = os.path.splitext(base)[0] + ".tsv"
with open(sys.argv[1]) as csv_in, open(output_filename, "w") as tsv_out:
    csv_reader = reader(csv_in)
    tsv_writer = writer(tsv_out, delimiter="\t")
    for row in csv_reader:
        tsv_writer.writerow(row)
