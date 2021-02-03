import sys

lines = [
    "col1, col2, col3, col4\n",
    "11, 12, 13, 14\n",
    "15, 16, 17, 19\n",
    "19, 20, 21, 22\n",
]
with open(sys.argv[1], "w") as out_fh:
    out_fh.writelines(lines)
