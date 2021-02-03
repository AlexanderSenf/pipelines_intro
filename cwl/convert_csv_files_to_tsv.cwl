#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: pipeline:2

baseCommand: python

arguments: ["/convert_csv_files_to_tsv.py"]

inputs:
  filename:
    type: File
    inputBinding:
      position: 2

outputs:
  file:
    type: File
    outputBinding:
      glob: $(inputs.filename.nameroot).tsv
