# A Short Introduction to CWL
This repo attempts to demonstrate the basics of a CWL pipeline by
taking a simple Python script and rendering it in a variety of
possible frameworks and workflow description languages.

The code is not really doing anything interesting, but the tasks
can be used to demonstrate a few of the capabilities of each
approach.

## Setup

Not much is required. This code is written and tested in Ubuntu
18.04 LTS and Python version 3.6.9. Recommended setup steps are:

System prerequisites:
```
sudo apt install python3-venv
sudo apt install cwltool
sudo apt install docker.io
sudo apt install python3-dev
```
This installs the CWL reference runner, which allows for easy execution
of CWL pipelines on localhost. CWL is meant to be portable ("bring the
computation to the data"), many of the advantages are in this portability.

Python prerequisites:
```
git clone https://github.com/AlexanderSenf/pipelines_intro.git
cd pipelines_intro
python3 -m venv pipelines-env
source pipelines-env/bin/activate
pip install -e requirements.txt
```

## Option 1: plain Python

`plain_python.py` shows the basic function: 3 `CSV` files are created,
and then converted into `TSV` files, and the MD5 checksum is
calculated for each output file. Running this script:
```
python plain_python.py
```
(The resulting files can be removed using `rm file*`)

This is a single-threaded Python script, running a loop for 3 times,
each time creating a new `CSV` file, transforming it into a `TSV` file,
and then calculating its MD5 checksum.

## Option 2: Ruffus-based Python pipeline

`ruffus_pipeline.py` performs the very same tasks, but this time using
the Ruffus framework, which allows building and running pipelines in a
much more  convenient way. For example, handling input and output
between steps of the pipeline; multi-treading or multi-processing.
```
python ruffus_pipeline.py
```
(The resulting files can be removed using `rm file*`)

This code defines a pipeline with three steps. The ordering of each
step is not defined by the order of the Python code, but instead by
dependencies based on using output files from one step as input files
for another step. Order can also be enforced manually.

## Option 3: Intro to CWL: wrapping Python

CWL (Common Workflow Language) differs from Ruffus by being a language
to describe a workflow, instead of a framework that deals with all
aspects of code and execution. CWL describes what should be done,
without prescribing what language, environment, etc. must be used.

This allows for a (not recommended, but very easy) way to convert
existing code as CWL workflows. As a first look at CWL, the 'what' of
the CWL script is just a Python script.

Both of these work:
```
cwl-runner python_as_cwl.cwl --script plain_python.py
cwl-runner python_as_cwl.cwl --script ruffus_pipeline.py
```
(The resulting files can be removed using `rm file*`)

The command that is run in this CWL step is just `python`, with the
next element provided as input parameter. If further parameters are
used (for example, if the Python script has input parameters) then
these are specified as input parameters in the CWL `inputs:` section.
It is also possible to use default values, or to pre-process input
values based on other information available at run-time.

## Option 4: Intro to CWL: using Docker

In many cases the code requires a specific environment, possibly also
very specific versions of libraries, etc. One of the easiest ways to
provide that is by using a Docker container to run the code defined in
a CWL step.

In this example the requirements are minimal: Python 3 and ruffus. This
leads to a very simple `Dockerfile` suitable for this pipeline:
```
FROM python:3.6-slim-buster
RUN pip install ruffus
```
This should be built locally using (the tag is used in the CWL code):
```
docker build . -t pipeline:1
```
And the only thing that needs to be added to the CWL script is a
hint to use Docker:
```
hints:
  DockerRequirement:
    dockerPull: pipeline:1
```
The cwl runner takes care of mounting the working directories and paths
to the Docker container, and running the `baseCommand` inside of
Docker, instead of in the local environment.  In fact, the Docker commands
used to run each step are part of the standard output.

Both of these work:
```
cwl-runner python_as_cwl_docker.cwl --script plain_python.py
cwl-runner python_as_cwl_docker.cwl --script ruffus_pipeline.py
```
(The resulting files can be removed using `rm file*`)

The ideal-case scenario is for all code to be inside of the Docker
container, so that only parameters and input data are passed in.
One advantage of this is that no code is required locally to run a
CWL pipeline - everything is automatically obtained via a
Docker repository at runtime, unless it is already available locally.

## Option 5: Separating Python into individual, separate steps

For better clarity the CWL code is in subdirectory `cwl/`, and for
convenience scripts are included in the Docker image as well,
so a new Docker image must be created (also, `ruffus` is no longer
required, so the Docker image can be smaller):
```
cd cwl
docker build . -t pipeline:2
```
Options 3 and 4 merely wrap an existing script as a single-step CWL
pipeline. The advantage of CWL is that each step in a pipeline should
also be a step in CWL. This will enable steps within a pipeline to be
shared and re-used by other pipelines, reducing code duplication and
maintenance.

The existing demo pipeline has three steps: (1) generate CSV files,
(2) transform CSV files into TSV files, and (3) calculate MD5
checksums of the TSV files. Here is a brief look at each of the new
steps (Python and CWL):

### create_three_new_files

In `ruffus` this function is called three times by providing the
`originate` step with a list of three input parameters. CWL works the
same way; so the script itself needs to generate only 1 file, and the
CWL pipeline automatically calls it with three input values.

This step can be tested and run in isolation, creating one file,
named `file1.csv`:
```
cwl-runner create_new_file.cwl --filename file1.csv
```

### convert_csv_file_to_tsv_file

This is very basic Python, just 7 lines of code are used in this demo.
This is a 1-1 step, similar to the `transform` pipeline step in
`ruffus`. Handling multiple files is handled by CWL.

This step can also be run in isolation, but requires an existing `CSV`
to work properly; ideally the file produced by the previous step:
```
cwl-runner convert_csv_file_to_tsv.cwl --filename file1.csv
```

### calculate_md5

This exists as command line call already; no additional code is
neccessary. Each individual CWL step is run as its own task, it is
easy to mix Python, Shell, or any other languages or tools necessary
in the same pipeline. Each CWL `CommandLineTool` acts as a black box,
taking input, producing output.

This step can also be run in isolation; with any existing file. To
test this workflow, this would requires an existing `TSV` file;
ideally the file produced by the previous step:
```
cwl-runner create_md5.cwl --filename file1.tsv
```
As a result there should now be three files:
```
file1.csv
file1.tsv
file1.tsv.md5sum
```

### CWL `CommandLineTool`

Each individual step in a CWL pipeline is a CommandLineTool; while it
is possible to combine multiple tools and workflows in the same `.cwl`
file, it is better practice to keep the code separated.

Each CLW CommandLineTool is an independent unit of code, which can be
used to build pipelines; with each functional step to be programmed only
once. And this being a standard, there are existing libraries of tools
available; such as:
* https://github.com/ncbi/cwl-ngs-workflows-cbb
* https://github.com/common-workflow-library/bio-cwl-tools

These repositories also contain whole pipelines, as CWL `Workflow`s.
This potentially speeds up development of new pipelines by already
providing ready-to-use building blocks.

### CWL `Workflow`

A Workflow is a set of CommandLineTools, or other Workflows. This allows
for the description of pipelines in a similar way to Ruffus.

In this example, with the availability of the three individual building
blocks, the same pipeline that was implemented by Ruffus in Option 2 (above)
can be implemented using CWL. The principles are very similar - the pipeline
has individual steps. The order of steps in the code does not determine the
order of execution. Instead, sequence is inferred by looking at which steps
use output provided by prior steps.

Unlike Ruffus, each step in the pipeline is its own unit of execution, so
there is no continuity of files between steps. Files must be passed on
explicitly; otherwise they just exist in temporary directories of the current
step, and the next step has no access or knowledge of these files.

Running this workflow for the same three files:
```
cwl-runner workflow.cwl --FILENAME file1.csv --FILENAME file2.csv --FLENAME file3.csv
```
(There are better ways to specify input parameters. Usually they would be
provided in a `yaml` file; but for demo purposes it is interesting to see the
command-line call in full.)

## Execution

CWL is just a description language, it does not supply an execution environment.
The reference package `cwltool` provides a reference implementation of a
Python-based runner. However, this tool is limited, and performs all actions
sequentially in a single thread. This is good for test and development, but not
for compute-intensive applications.

Other CWL runners exist, which run the individual steps of a CWL workflow in
parallel. Among the best examples is `toil`, which can be installed by:
`pip install toil[cwl]`. With this the workflow can be run using a different
runner (also: `toil` does require input parameters in a `yaml` file):
```
toil-cwl-runner workflow.cwl workflow.yaml
```
`Toil` opens up many more options. For example, `Toil` can set up remote execution
environments (AWS, Slurm, etc..) and then distribute the workflow across that
environment, so running a workflow is not tied to locally available resources.

Remote execution is one of the biggest advantages of CWL. One of the driving
forces behind this is to enable moving the compute closer to the data, as the
size of data often makes it infeasible to move closer to where local compute
resources may be available. This allows for a separation of where the results
of pipelines are needed (e.g. a Web server, a researcher's laptop, ...) and
where the computations are carried out.

## Execution in Kubernetes

Using `Toil` as an example, execution can be directed towards a Kubernetes
environment with the option `--batchSystem kubernetes`. All it needs is a Toil
node configured for Kubernetes (and AWS S3) This could also be done locally
with `minikube`.

Setup instrauctions are here: https://toil.readthedocs.io/en/latest/running/cloud/kubernetes.html

## Using yet another CWL execution engine for Kubernetes: Arvados

For this local demo the Kubernetes cluster used is `minikube`, and the
deployment mechanism uses `helm`. This installs a Kubernetes environment locally.

The prerequisites are: `kubectl`, `minikube`, and `helm`.
* kubectl (https://kubernetes.io/docs/tasks/tools/install-kubectl/)
  ```
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
  rm kubectl
  ```
* minikube (https://minikube.sigs.k8s.io/docs/start/)
  ```
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
  sudo dpkg -i minikube_latest_amd64.deb
  rm minikube_latest_amd64.deb
  ```
* helm
  ```
  curl -LO https://get.helm.sh/helm-v3.5.2-linux-amd64.tar.gz
  tar -zxvf helm-v3.5.2-linux-amd64.tar.gz
  mv linux-amd64/helm ../pipelines-env/bin/
  rm helm-v3.5.2-linux-amd64.tar.gz
  rm -rf linux-amd64
  ```

Arvados can then be deployed (https://doc.arvados.org/install/arvados-on-kubernetes-minikube.html)
```
git clone https://github.com/arvados/arvados-k8s.git
cd arvados-k8s/charts/arvados
```
The Arvados server will be available at the IP address of minikube. It also needs
a SSL certificate to run services. With Arvados running, return to the cwl
directory, and get the CWL runner for Arvados:
```
minikube start
./cert-gen.sh `minikube ip`
helm install arvados . --set externalIP=`minikube ip`
./minikube-external-ip.sh
export ARVADOS_API_TOKEN=thisisnotaverygoodsuperusersecretstring00000000000
export ARVADOS_API_HOST=`minikube ip`:444
export ARVADOS_API_HOST_INSECURE=true
cd ../../..
pip install arvados-cwl-runner
```

### Running the workflow

With this the pipeline can be run on Kubernetes:
```
arvados-cwl-runner workflow.cwl workflow.yaml
```
The output is identical again, but the pipeline was now run in `minikube`.
If `Arvados` is configured with an existing remote Kubernetes setup, the same
command would run the workflow remotely. Using the Apache 2.0 licensed Arvados
SDK programmatic access to the API allows easy integration to code.

### Shutting down again

```
helm del arvados
minikube stop
```

### Alternatives

There are several options for running CWL pipeline in Kubernetes; `Toil` is
just one of them. Here are some example of other execution environments:

* https://toil.ucsc-cgl.org/
  A scalable, efficient, cross-platform pipeline management system written
  entirely in Python and designed around the principles of functional programming.
  Scalability: https://www.biorxiv.org/content/10.1101/062497v1.full
* https://docs.reana.io/
  This is the system developed by CERN. It comes with instruction on how to
  install REANA in Kubernetes via Helm charts. Software from CERN has the
  advantage that it is genrally designed to work with much larger volumes of
  data than most other domains, including Genomics.
* https://github.com/Duke-GCB/calrissian
  Calrissian is a CWL implementation designed to run inside a Kubernetes cluster.
  Its goal is to be highly efficient and scalable, taking advantage of high
  capacity clusters to run many steps in parallel.
* https://github.com/uc-cdis/mariner
  Mariner is a workflow execution service written in Go for running CWL
  workflows on Kubernetes. Mariner's API is an implementation of the GA4GH
  standard WES API.
* https://arvados.org/
  Arvados allows bioinformaticians run and scale compute-intensive workflows,
  developers create biomedical applications, and IT administrators manage large
  compute and storage resources.  100% free and open software that you can
  control. Software that is developed in public, backed by both strong
  commercial support and an active community.

### License considerations

* Toil: Apache 2.0
* REANA: MIT License
* Calrissian: MIT License
* Mariner: Apache 2.0
* Arvados:
  * Server side: GNU Affero GPL version 3
  * Client SDK: Apache 2.0

### GA4GH

Within the GA4GH (Global Alliance for Genomics and Health) there is active work
on a set of standards to enable cloud-based execution of workflows (CWL, WDL, ...).
The standard responsible for executing code is the Task Execution Service (TES); and
one example of a server implementing TES is `Funnel` (https://github.com/ohsu-comp-bio/funnel).

`Mariner` is an example of a CWL execution engine implementing the Workflow
Execution Service (WES) API, which makes it compatible with all software and
web sites implementing access to WES.

There are many other applicable and useful standards; but this is not the place
to describe them.

# More Complex Example

This repository just covers the basics of what CWL is capable of. A more
interesting example is available within the context of ELIXIR Europe's
implementation of the GA4GH standards:
* https://github.com/elixir-cloud-aai/demo-workflows/tree/dev/cwl

One of these workflows is the a rare diseases workflow actually being used by
RD Connect's own processing pipeline. This is a CWL-based pipeline taking a
FASTQ file as input, and producing a gVCF file for ingestion into the RD Connect
project. This pipeline uses FastQC, BWA-MEM, Picard, GATK, etc..)

With the setup completed within this demo, it is already possible to run this
workflow locally!
```
git clone https://github.com/elixir-cloud-aai/demo-workflows.git
cd cwl/rare_diseases_workflows
cwl-runner workflow.cwl workflow.yml
[or]
toil-cwl-runner workflow.cwl workflow.yml
```
(Although the paths in the `workflow.yml` file may need to be adjusted).

The RD Connect project: https://rd-connect.eu/
