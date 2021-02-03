#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: pipeline:2

baseCommand: python

arguments: ["/create_new_file.py"]

inputs:
  filename:
    type: string
    inputBinding:
      position: 1

outputs:
  file:
    type: File
    outputBinding:
      glob: $(inputs.filename)
