# Apscale Installer

## Important changes
* APSCALE4 is now implement in APSCALE-GUI [22.08.2025]
* Please update the environment to "apscale4" (upgraded to python3.12)
* The original "apscale" environment is outdated (python3.10 is no longer supported).

## Introduction

The easiest way to install the apscale metabarcoding workflow is by using [Miniconda3](https://docs.anaconda.com/miniconda/#). Miniconda will create an isolated environment with all the suggested versions of each tool.

> **Note:** Currently, [vsearch](https://github.com/torognes/vsearch) and [blast+](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html) cannot be automatically installed via conda. For now, the easiest solution is the installation through the apscale-installer script. We will update this Wiki when vsearch and blast+ are available via conda. Linux users can install vsearch and blast+ already now using conda.

This tutorial will install the following tools:
* [Apscale](https://github.com/DominikBuchner/apscale)
* [Apscale-GUI](https://github.com/TillMacher/apscale_gui)
* [Apscale_blast](https://github.com/TillMacher/apscale_blast)
* [Boldigger3](https://github.com/DominikBuchner/BOLDigger3)
* [Demultiplexer2](https://github.com/DominikBuchner/demultiplexer2)
* TaxonTableTool2 (coming soon)

## Miniconda Installation

1. Install Miniconda by following the instructions.

2. Open a new Anaconda (Miniconda3) terminal.
   - **Windows**: Type 'Anaconda' in your search bar and select 'Anaconda Powershell Prompt (miniconda3)'.
   - **MacOS**: Open a new terminal. You will see the (base) environment before your user name.

3. Download the respective environment installation file for [Windows](https://github.com/TillMacher/apscale_installer/blob/main/environments/apscale_env_windows_aarch64.yml) or [MacOS](https://github.com/TillMacher/apscale_installer/blob/main/environments/apscale_env_macos_aarch64.yml).

4. Install the metabarcoding environment by typing:
   ```sh
   conda env create -f apscale_env_windows_aarch64.yml
   
5. This should automatically install all dependencies. After the installation, activate the environment:
   ```sh
   conda activate apscale4

6. **Windows and MacOS** users run the apscale-installer script:
   ```sh
   apscale_installer

7. **Linux and MacOS (intel)** users can use conda:
   ```sh
   conda install bioconda::vsearch
   conda install bioconda::blast
   playwright install

8. Verify your installations:
   ```sh
   vsearch --help
   blastn -h

* If you want to uninstall the old apscale environment type:
  ```sh
  conda remove -n apscale --all

## Miniconda Installation (manual)

* If the yml installation of the environment fails a manual installation can be performed:

   ```sh
   conda create -n apscale4 python=3.12 ipython
   conda activate apscale4
   pip install apscale
   pip install apscale_gui
   pip install apscale_installer
   pip install apscale_blast
   pip install boldigger3
   pip install demultiplexer2
   apscale_installer

## Usage

Now that everything is installed, you can use the installed software. 

Refer to the homepages of each program to run learn how to use them:
* [Apscale](https://github.com/DominikBuchner/apscale/tree/main?tab=readme-ov-file#how-to-use)
* [Apscale-GUI](https://github.com/TillMacher/apscale_gui)
* [Apscale_blast](https://github.com/TillMacher/apscale_blast?tab=readme-ov-file#how-to-use)
* [Boldigger3](https://github.com/DominikBuchner/BOLDigger3?tab=readme-ov-file#installation-and-usage)
* [Demultiplexer2](https://github.com/DominikBuchner/demultiplexer2)
* TaxonTableTool2 (coming soon)

## Video tutorial
There is also a [YouTube tutorial](https://www.youtube.com/watch?v=c6pm0FhcINI) available, where the installation of **Windows** and **MacOS** is demonstrated.

