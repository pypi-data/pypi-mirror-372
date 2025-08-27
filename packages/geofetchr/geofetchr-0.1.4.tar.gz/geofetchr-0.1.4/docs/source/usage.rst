Usage Examples
--------------


**Try out this demo! Enter your input, and the code will automatically call the package functions to generate a organized, well-formatted output.**


Keyword Search
^^^^^^^^^^^^^^
Search GEO datasets by keyword(s), and display organism counts and dataset counts.

.. code-block:: python

    import geofetchr

    def main():
        global all_results
        while True:
            keywords_input = input("\nEnter keywords (comma-separated, or type 'exit' to quit): ").strip()
            if keywords_input.lower() == 'exit':
                print("Exiting program.")
                return

            keywords = [k.strip() for k in keywords_input.split(",")]
            print("\nFetching all GEO data...")
            all_results = geofetchr.search_geo_data(keywords)

            print("\n🔹 Top Organisms:")
            for organism, count in all_results["ORGANISM_COUNTS"].items():
                print(f"{organism} ({count})")

            print("\n🔹 Dataset Counts:")
            print(f"Total GDS results: {len(all_results['GDS'])}")
            print(f"Total GPL results: {len(all_results['GPL'])}")
            print(f"Total GSE results: {len(all_results['GSE'])}")

    if __name__ == "__main__":
        main()

Sample output::

    Top Organisms:
      Homo sapiens (868)
      Mus musculus (1211)
      Rattus; synthetic construct (1)

    Dataset Counts:
      Total GDS results: 64
      Total GPL results: 18
      otal GSE results: 2564

Group Results by Organism
^^^^^^^^^^^^^^^^^^^^^^^^^
Filter datasets for selected organisms, and view dataset link, PubMed references and assay type.

.. code-block:: python

    import geofetchr

    def main():
        global grouped_results
        while True:
            selected_organisms_input = input(
                "\nEnter organism(s) to filter (comma-separated) or 'exit' to quit: ").strip().lower()
            if selected_organisms_input == 'exit':
                print("Exiting program.")
                return False

            selected_organisms = [o.strip() for o in selected_organisms_input.split(",")]
            grouped_results = geofetchr.group_results_by_organism(all_results, selected_organisms)

            for organism, data in grouped_results.items():
                print(f"\n🔹 Organism: {organism}")
                for category, entries in data.items():
                    print(f"{category}: {len(entries)} results")
                    for entry, link, pubmed_links, assay_type in entries:
                        pubmed_str = ", ".join(pubmed_links)
                        print(f"{entry} - Dataset: {link} - PubMed: {pubmed_str}\nAssay Type: {assay_type}\n")

    if __name__ == "__main__":
        main()

Sample output::

  Organism: danio rerio

    GDS: 0 results
    GPL: 0 results
    GSE: 46 results

    GSE279773 - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE279773 - PubMed: https://pubmed.ncbi.nlm.nih.gov/39832654
    Assay Type: Expression profiling by array

    GSE162148 - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE162148 - PubMed: https://pubmed.ncbi.nlm.nih.gov/34140474 
    Assay Type: Expression profiling by high throughput sequencing, Genome binding/occupancy profiling by high throughput sequencing, Non-coding RNA profiling by high throughput sequencing


Filter by Assay Type
^^^^^^^^^^^^^^^^^^^^
Show all available assay types along with their corresponding datasets, grouped by assay type.

.. code-block:: python

    import geofetchr

    def main():
        while True:
            action = input("\nOptions:  'assay' to filter by assay type or 'exit' to quit: ").strip().lower()
            if action == 'exit':
                print("Exiting program.")
                return False
            elif action == 'assay':
                geofetchr.filter_by_assay_type_across_all(grouped_results)
            else:
                print("Invalid option. Try again.")

    if __name__ == "__main__":
        main()

Sample output::

  Available Assay Types:
    Expression profiling by high throughput sequencing: 29 datasets
    Expression profiling by array: 6 datasets
    Expression profiling by array, Non-coding RNA profiling by array: 1 datasets

  Datasets with Assay Type 'Expression profiling by high throughput sequencing':
    GSE281891 (rattus norvegicus) - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE281891
    PubMed: No PubMed Link

View Metadata by GEO ID
^^^^^^^^^^^^^^^^^^^^^^^
Retrieve detailed metadata for any GEO accession (GSE, GDS, GPL).

.. code-block:: python

    import geofetchr

    def main():
        while True:
            action = input("\nOptions:  'id' to view metadata or 'exit' to quit: ").strip().lower()
            if action == 'exit':
                print("Exiting program.")
                return False
            elif action == 'id':
                geofetchr.view_metadata_by_id()
            else:
                print("Invalid option. Try again.")

    if __name__ == "__main__":
        main()

Sample output::

 Metadata for GSE108484:

  title: ['Transcriptome analysis of Chrdl1-treated RGCs']
  geo_accession: ['GSE108484']
  status: ['Public on Oct 29 2018']
  submission_date: ['Dec 23 2017']
  last_update_date: ['Mar 28 2022']
  pubmed_id: ['30344043']
  summary: ['Chrdl1 treatment promotes formation of synapses and GluA2-AMPAR recruitment in Retinal ganglion cell (RGC) cultures. Analysis of the transcriptome of RGCs with or without Chrdl1 treatment let us determine potential alterations in the expression of genes related to BMP signaling, or genes involved in excitatory synaptogenesis and AMPAR trafficking.']
  overall_design: ['RNA was isolated from RGC cultures treated for 12 hours with 1ug/ml Chrdl1, and compared to RNA isolated from buffer-treated (vehicle) RGCs as a control.']
  type: ['Expression profiling by high throughput sequencing']
  contributor: ['Elena,,Blanco-Suarez', 'Maxim,N,Shokhirev', 'Nicola,,Allen']
  sample_id: ['GSM2901408', 'GSM2901409', 'GSM2901410', 'GSM2901411', 'GSM2901412', 'GSM2901413']
  contact_name: ['April,Elizabeth,Williams']
  contact_institute: ['Salk Institute for Biological Studies']
  contact_country: ['USA']
  supplementary_file: ['ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE108nnn/GSE108484/suppl/GSE108484_fpkm_rat.txt.gz']
  platform_id: ['GPL18694']
  relation: ['BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA427397', 'SRA: https://www.ncbi.nlm.nih.gov/sra?term=SRP127490']


Download GEO Family Data
^^^^^^^^^^^^^^^^^^^^^^^^
Download and store the full GEO Family (GSE) dataset for further processing and visualization.

.. code-block:: python

    import geofetchr

    def main():
        while True:
            action = input("\nOptions:  'id' to download or 'exit' to quit: ").strip().lower()
            if action == 'exit':
                print("Exiting program.")
                return False
            elif action == 'id':
                gse_number = input("\nEnter a GEO ID (e.g., GSE12345, GDS67890, GPL13579): ")
                geofetchr.download_geo_family(gse_number)
            else:
                print("Invalid option. Try again.")

    if __name__ == "__main__":
        main()

Sample output::

   Downloading GEO Family file for GSE108484...
    Saved as: GSE108484_family.soft.gz
