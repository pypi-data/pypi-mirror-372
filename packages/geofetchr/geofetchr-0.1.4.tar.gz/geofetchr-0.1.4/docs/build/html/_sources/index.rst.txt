.. geofetchr documentation master file, created by
   sphinx-quickstart on Wed Aug 27 00:32:54 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GeoFetchr Documentation
=======================


GeoFetchr is a Python package that helps you easily search, filter, fetch metadata, and download datasets from the NCBI Gene Expression Omnibus (GEO) database. It provides functions to quickly explore GEO datasets by keywords, organism, assay type, accession IDs and to download GEO Family files.



Why use GeoFetchr
=======================

- This package can search GEO data for datasets based on provided keywords and display the top organisms associated with those keywords and the counts of GDS, GPL, and GSE results.
- It can group the search results by top organisms and display the number of datasets for each category (GDS, GPL, GSE) within the selected organisms.
- It can provide details for each dataset, including the dataset link, PubMed links (if available), and the assay type.
- It can filter the grouped results by assay type and list the datasets matching the selected assay type.
- It supports multi-keyword searching and can display results for multiple organisms and assay types.
- It can provide detail metadata for a given GEO ID (GSE, GDS, or GPL), including title, accession, status, submission date, summary, overall design, type, contributors, sample IDs, 
  contact information, supplementary files, platform details, and related projects (BioProject, SRA).
- It can download GEO Family files for a given GEO ID, including series matrix, family XML, family soft, and raw data files.




.. include:: README.rst
   :maxdepth: 2
   :caption: Overview

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   requirements
   license
