# Demo Pipeline using plain Python

import hashlib
import os
from csv import reader, writer

WORK_DIR = os.path.abspath(".")


def create_new_file(output_file):
    lines = [
        "col1, col2, col3, col4\n",
        "11, 12, 13, 14\n",
        "15, 16, 17, 19\n",
        "19, 20, 21, 22\n",
    ]
    with open(output_file, "w") as out_fh:
        out_fh.writelines(lines)


def csv_to_tsv(input_file, output_file):
    with open(input_file) as csv_in, open(output_file, "w") as tsv_out:
        csv_reader = reader(csv_in)
        tsv_writer = writer(tsv_out, delimiter="\t")
        for row in csv_reader:
            tsv_writer.writerow(row)


def md5(input_file):
    output_file = os.path.abspath(input_file + ".md5sum")
    with open(input_file, "rb") as f, open(output_file, "w") as o:
        bytes = f.read()  # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest()
        o.write(readable_hash)


for i in range(1, 4):
    create_new_file(os.path.join(WORK_DIR, f"file{i}.csv"))
    csv_to_tsv(
        os.path.join(WORK_DIR, f"file{i}.csv"), os.path.join(WORK_DIR, f"file{i}.tsv")
    )
    md5(os.path.join(WORK_DIR, f"file{i}.tsv"))
