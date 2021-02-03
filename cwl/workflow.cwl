#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

#####

requirements:
  ScatterFeatureRequirement: {}

#####

inputs:

  FILENAME: string[]

#####

outputs:

  csv_out:
    type: File[]
    outputSource: csv_step/file

  tsv_out:
    type: File[]
    outputSource: tsv_step/file

  md5_out:
    type: File[]
    outputSource: md5_step/file

#####

steps:

    csv_step:
      run: create_new_file.cwl
      scatter: [filename]
      scatterMethod: dotproduct
      in:
        filename: FILENAME
      out: [file]

    tsv_step:
      run: convert_csv_files_to_tsv.cwl
      scatter: [filename]
      scatterMethod: dotproduct
      in:
        filename: csv_step/file
      out: [file]

    md5_step:
      run: create_md5.cwl
      scatter: [filename]
      scatterMethod: dotproduct
      in:
        filename: tsv_step/file
      out: [file]
