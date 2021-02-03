# Demo Pipeline using Ruffus

import hashlib
import os
from csv import reader, writer

import ruffus.cmdline as cmdline
from ruffus import Pipeline, output_from, suffix

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


def md5(input_file, _):
    output_file = os.path.abspath(input_file + ".md5sum")
    with open(input_file, "rb") as f, open(output_file, "w") as o:
        bytes = f.read()  # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest()
        o.write(readable_hash)


def build_pipeline():

    pipe = Pipeline("my_pipeline")

    pipe.originate(
        name="create_three_new_files",
        task_func=create_new_file,
        output=[os.path.join(WORK_DIR, f"file{i}.csv") for i in range(1, 4)],
    )

    pipe.transform(
        name="convert_csv_files_to_tsv",
        task_func=csv_to_tsv,
        input=output_from("create_three_new_files"),
        filter=suffix(".csv"),
        output=".tsv",
    )

    pipe.transform(
        name="calculate_md5",
        task_func=md5,
        input=output_from("convert_csv_files_to_tsv"),
        filter=suffix(".tsv"),
        output=".md5sum",
    )

    return pipe


if __name__ == "__main__":
    parser = cmdline.get_argparse(description="CNV Calling", ignored_args=["jobs"])

    options = parser.parse_args()
    options.history_file = os.path.join(WORK_DIR, ".ruffus_history.sqlite")

    pipeline = build_pipeline()

    cmdline.run(options, multithead=3)
