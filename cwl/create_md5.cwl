#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: pipeline:2

baseCommand: md5sum
stdout: $(inputs.filename.basename).md5sum

inputs:
  filename:
    type: File
    inputBinding:
      position: 1

outputs:
  file:
    type: stdout
