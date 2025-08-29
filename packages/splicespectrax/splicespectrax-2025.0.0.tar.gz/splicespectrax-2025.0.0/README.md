# SPECTRA: Unsupervised Analysis of Alternative Splicing


## ✂️ About

**SPECTRA** (Splicing-based Pattern Extraction and Clustering using TRAnscriptomics) is an end-to-end pipeline for discovering patient subtypes based on alternative splicing. It is a modernized and optimized version of the original OncoSplice algorithm.

SPECTRA leverages an **iterative clustering strategy** to identify stable and dominant splicing patterns across patient samples. The new implementation enhances the **speed**, **accuracy**, and **modularity**, allowing seamless integration into both command-line workflows and interactive Python environments.

![SPECTRA Workflow](spectra_workflow-01.png)

## 📌 Installation

SPECTRA can installed as a Python package via `pip`. We recommend using conda environment with python version set to 3.12. 

`pip install -i https://test.pypi.org/simple/ spectra-kairaveet`


## 📚 Documentation

Detailed documentation on how to perform SPECTRA analysis is provided on [https://spectra-kairaveethakkar.readthedocs.io/en/latest/](ReadTheDocs) now.


## 👩‍🏫 Tutorial
Example datasets: 
PSI files for each TCGA cancer can be downloaded from [https://www.synapse.org/Synapse:syn64934289](here). 

SPECTRA can be used in two ways:
- As a **command-line tool** for end-to-end execution
- As a **modular workflow**, where individual functions are called step-by-step

See the tutorials and example scripts for each approach:

### Command-Line Interface (CLI)

Run the entire pipeline with a single command using `main.py`. This is ideal for multiple dataset processing and automated workflows.

### Modular Usage

Import and run individual components such as preprocessing, clustering, or visualization in a custom step-by-step analysis.

## 📝 Overview of Modules

| Module | Description |
|--------|-------------|
| `main.py` | Entry point for running the complete SPECTRA pipeline. Handles argument parsing and execution flow. |
| `round_wrapper.py` | Wraps a single iteration of clustering (SPECTRA performs 3 iterations by default). |
| `preprocess.py` | Performs variance-based and intercorrelation-based filtering of splicing events prior to clustering. |
| `remove_redundancy.py` | Removes redundant splicing events based on intra-gene correlation. |
| `feature_selection.py` | Implements PCA-based feature selection, similar to the splice-ICGS method in the original OncoSplice. |
| `median_impute.py` | Imputes missing values in the splicing matrix using the median for each event. |
| `visualizations.py` | Generates visual summaries, including splicing event annotation bar plots and cluster heatmaps. |
| `determine_rank.py` | Automatically determines the optimal NMF rank (if not user-specified). |
| `run_nmf.py` | Performs NMF clustering and assigns multi-label cluster memberships. |
| `metadata_analysis.py` | Analyzes and annotates differential splicing events across clusters. |
| `linear_svm.py` | Applies linear SVM for final cluster assignment. |
| `correlation_depletion.py` | Identifies and depletes splicing events associated with a clustering round. |
| `correlation_depletion_vectorized.py` | A faster version of `correlationDepletion.py` using imputed values and optimized calculations. |

## 📖 Citation

Coming soon — citation information for referencing SPECTRA in publications.
