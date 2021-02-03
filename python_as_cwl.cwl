#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

baseCommand: [python]

inputs:
  script:
    type: File
    inputBinding:
      position: 1

outputs:
  new_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: "file*"
