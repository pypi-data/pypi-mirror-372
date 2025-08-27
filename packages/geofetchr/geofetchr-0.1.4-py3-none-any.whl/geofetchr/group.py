import GEOparse
import pandas as pd
import warnings
import sys

# Suppress specific pandas warning
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

def group_results_by_organism(results, selected_organisms):

    """Group previously fetched results by organism and extract assay type for GSEs.

    Args:
        results (dict): Dictionary returned by `search_geo_data`, containing keys:
            - "GDS", "GPL", "GSE" (lists of accessions)
            - "MAPPING" (dict of accession → organism)
            - "LINKS" (dict of accession → dataset link)
            - "PUBMED" (dict of accession → list of PubMed links)
        selected_organisms (list[str]): List of organisms to filter, e.g., ["Homo sapiens", "Mus musculus"].

    Returns:
        dict: Nested dictionary with structure:
            {
                "organism_lowercase": {
                    "GDS": [(accession, dataset_link, pubmed_links, assay_type), ...],
                    "GPL": [(accession, dataset_link, pubmed_links, assay_type), ...],
                    "GSE": [(accession, dataset_link, pubmed_links, assay_type), ...]
                },
                ...
            }

    Notes:
        - GDS and GPL entries are processed directly.
        - GSE entries are processed in batches of 50 to avoid overloading GEO servers.
        - Users are prompted to continue between batches.
        - Assay type for GDS and GPL is set to "N/A"; for GSE it is extracted from metadata.

    Example:
        >>> grouped_results = geofetchr.group_results_by_organism(all_results, ["drosophila melanogaster"])
        >>> for organism, data in grouped_results.items():
        ...     print(f"Organism: {organism}")
        ...     for category, entries in data.items():
        ...         print(f"{category}: {len(entries)} results")
        ...         for entry, link, pubmed_links, assay_type in entries:
        ...             pubmed_str = ", ".join(pubmed_links)
        ...             print(f"{entry} - Dataset: {link} - PubMed: {pubmed_str} \\nAssay Type: {assay_type}\\n")
        
        Output:
           **Organism: drosophila melanogaster**
        GDS: 1 results
        GDS1977 - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GDS1977 - PubMed: https://pubmed.ncbi.nlm.nih.gov/16533912 
        Assay Type: N/A

        GPL: 1 results
        GPL1322 - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL1322 - PubMed: No PubMed Link 
        Assay Type: N/A

        GSE: 36 results
        GSE305551 - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE305551 - PubMed: No PubMed Link 
        Assay Type: Expression profiling by high throughput sequencing

    """

    selected_organisms = [o.strip().lower() for o in selected_organisms]
    grouped = {organism: {"GDS": [], "GPL": [], "GSE": []} for organism in selected_organisms}

    # Process GDS and GPL normally
    for category in ["GDS", "GPL"]:
        for entry in results[category]:
            organism = results["MAPPING"].get(entry, "unknown organism").lower()
            for selected_organism in selected_organisms:
                if selected_organism in organism:
                    pubmed_links = results["PUBMED"].get(entry, [])
                    dataset_link = results["LINKS"].get(entry, "")
                    assay_type = "N/A"
                    grouped[selected_organism][category].append(
                        (entry, dataset_link, pubmed_links, assay_type)
                    )
                    break

    # Process GSE in batches of 50
    gse_entries = results["GSE"]
    matching_gse = []

    for entry in gse_entries:
        organism = results["MAPPING"].get(entry, "unknown organism").lower()
        for selected_organism in selected_organisms:
            if selected_organism in organism:
                pubmed_links = results["PUBMED"].get(entry, [])
                dataset_link = results["LINKS"].get(entry, "")
                matching_gse.append((entry, selected_organism, dataset_link, pubmed_links))
                break

    batch_size = 50
    for i in range(0, len(matching_gse), batch_size):
        batch = matching_gse[i:i + batch_size]
        for entry, selected_organism, dataset_link, pubmed_links in batch:
            try:
                gse = GEOparse.get_GEO(geo=entry, silent=True)
                assay_type_list = gse.metadata.get("type", ["Unknown"])
                assay_type = ", ".join(assay_type_list)
            except Exception as e:
                assay_type = f"Error: {str(e)}"

            grouped[selected_organism]["GSE"].append(
                (entry, dataset_link, pubmed_links, assay_type)
            )

        if i + batch_size < len(matching_gse):
            cont = input(f"\nProcessed {i + batch_size}/{len(matching_gse)} GSEs. Continue with next 50? (y/n): ").strip().lower()
            if cont != 'y':
                break

    return grouped



def filter_by_assay_type_across_all(grouped_results):

    """
    Display available assay types across all organisms and allow filtering of GSE datasets.

    Args:
        grouped_results (dict): Output of `group_results_by_organism`.

    Returns:
        None: Prints filtered datasets to the console.

    Functionality:
        - Collects all unique assay types from GSE datasets.
        - Displays available assay types and their dataset counts.
        - Prompts user to select an assay type to filter.
        - Prints datasets corresponding to the selected assay type, including:
            accession, organism, GEO dataset link, and PubMed links.

    Notes:
        - If no assay type data is found, prints a warning.
        - Interactive function: requires user input to select assay type.

    Example Output:
        >>> assay_type = geofetchr.filter_by_assay_type_across_all(grouped_results)
        >>> print(assay_type)
        
        Output:
        **Available Assay Types:**
        Expression profiling by high throughput sequencing: 20 datasets
        Expression profiling by high throughput sequencing, Non-coding RNA profiling by high throughput sequencing: 1 datasets
       
        Enter assay type to filter: Expression profiling by array

          **Datasets with Assay Type 'Expression profiling by array':**
        GSE16713 (drosophila melanogaster) - Dataset: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE16713 - PubMed: https://pubmed.ncbi.nlm.nih.gov/20668662
        
    """

    assay_dict = {}
    for org, categories in grouped_results.items():
        for entry, link, pubmed_links, assay_type in categories.get("GSE", []):
            if assay_type not in assay_dict:
                assay_dict[assay_type] = []
            assay_dict[assay_type].append((entry, link, pubmed_links, org))

    if not assay_dict:
        print("\nNo assay type data found.")
        return

    print("\n🔹 **Available Assay Types:**")
    for assay_type, entries in assay_dict.items():
        print(f"{assay_type}: {len(entries)} datasets")

    selected_type = input("\nEnter assay type to filter: ").strip()
    selected_entries = assay_dict.get(selected_type, [])

    if not selected_entries:
        print("\nNo datasets found for that assay type.")
        return

    print(f"\n🔹 **Datasets with Assay Type '{selected_type}':**")
    for entry, link, pubmed_links, organism in selected_entries:
        pubmed_str = ", ".join(pubmed_links)
        print(f"{entry} ({organism}) - Dataset: {link} - PubMed: {pubmed_str}")
        